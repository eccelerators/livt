import importlib.util
from pathlib import Path
import tempfile
import tomllib
import unittest

spec = importlib.util.spec_from_file_location("workspace_runner", Path(__file__).with_name("test-workspace.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class WorkspaceRunnerTests(unittest.TestCase):
    def test_focused_mode_uses_only_workspace_iterator_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "livt"
            (project / "tests").mkdir(parents=True)
            (project / "workspace-tests").mkdir()
            (project / "workspace-tests/WorkspaceIteratorCompatibility.lvt").write_text("component WorkspaceIteratorCompatibility {}")
            (project / "livt.toml").write_text(
                '[project]\nname="Livt"\nversion="1.0.1"\n[tests]\ncomponents=["Existing"]\n'
                '[dependencies]\nLivt.Base="1.0.1"\nLivt.Collections="1.0.1"\nLivt.Utils="1.0.1"\n')
            original = (project / "livt.toml").read_text()
            for name in ("Base", "Collections", "Utils"):
                package = root / ("livt-" + name.lower())
                package.mkdir()
                (package / "livt.toml").write_text(f'[project]\nname="Livt.{name}"\nversion="1.1.0-dev"\n')
            _, combined = runner.prepare(project, root, root / "stage", root / "reports", True)
            settings = runner.load(combined)
            self.assertEqual({"Livt.Base", "Livt.Collections"}, set(settings["dependencies"]))
            self.assertEqual(["WorkspaceIteratorCompatibility"], settings["tests"]["components"])
            self.assertEqual("workspace-tests", settings["tests"]["path"])
            self.assertEqual(original, (project / "livt.toml").read_text())

    def test_manifest_round_trip_preserves_dotted_package_names(self):
        data = {"project": {"name": "Test", "version": "1.0.0"},
                "tests": {"components": ["One", "Two"]},
                "dependencies": {"Livt.Base": {"path": "/tmp/base"}},
                "build": {"debug": {"enabled": True, "number": 7}}}
        self.assertEqual(data, tomllib.loads(runner.manifest_text(data)))

    def test_staging_overrides_dependencies_without_editing_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / "source", root / "snapshot"
            (source / "src").mkdir(parents=True)
            (source / "src/Main.lvt").write_text("component Main {}")
            (source / "out").mkdir()
            (source / "out/stale.vhd").write_text("not copied")
            original = '[project]\nname="Test"\nversion="1.0.0"\n[dependencies]\nLivt.Base="1.0.1"\n'
            (source / "livt.toml").write_text(original)
            runner.stage_project(source, target, {"Livt.Base": root / "base"})
            self.assertEqual(original, (source / "livt.toml").read_text())
            self.assertEqual({"path": str(root / "base")}, runner.load(target)["dependencies"]["Livt.Base"])
            self.assertTrue((target / "src/Main.lvt").is_file())
            self.assertFalse((target / "out").exists())

    def test_unmapped_dependency_is_not_silently_resolved_from_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "livt.toml").write_text('[project]\nname="Test"\n[dependencies]\nOther="1.0.0"\n')
            with self.assertRaisesRegex(ValueError, "Unmapped"):
                runner.stage_project(source, source / "snapshot", {})

    def test_source_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "livt.toml").write_text('[project]\nname="Test"\npath="../outside"\n')
            with self.assertRaisesRegex(ValueError, "Source path"):
                runner.stage_project(source, source / "snapshot", {})
