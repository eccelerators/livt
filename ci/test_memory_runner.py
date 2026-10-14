import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("memory_runner", Path(__file__).with_name("test-memory.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class MemoryRunnerTests(unittest.TestCase):
    def package(self, root, folder, name, dependencies=""):
        source = root / folder
        (source / "src").mkdir(parents=True)
        (source / "src/Example.lvt").write_text("component Example {}")
        (source / "livt.toml").write_text(
            f'[project]\nname="{name}"\nversion="1.0.0"\n' + dependencies)
        return source

    def test_stages_only_memory_dependencies_without_changing_pins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.package(root, "livt-collections", "Livt.Collections")
            io = self.package(root, "livt-io", "Livt.IO", '[dependencies]\n"Livt.Collections"="1.0.0"\n')
            original = (io / "livt.toml").read_text()
            sources, projects = runner.prepare(root / "stage", root)
            self.assertEqual({"Livt.Collections", "Livt.IO"}, set(sources))
            self.assertEqual(["WorkspaceMemory"], list(projects))
            settings = runner.workspace.load(projects["WorkspaceMemory"])
            self.assertEqual({"Livt.IO"}, set(settings["dependencies"]))
            self.assertTrue((projects["WorkspaceMemory"] / "src").is_dir())
            self.assertTrue((projects["WorkspaceMemory"] / "tests/WorkspaceMemoryCompatibility.lvt").is_file())
            self.assertEqual(original, (io / "livt.toml").read_text())

    def test_consumers_use_staged_io_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.package(root, "livt-collections", "Livt.Collections")
            self.package(root, "livt-io", "Livt.IO")
            cli = self.package(root, "cli", "Eccelerators.Cli", '[dependencies]\n"Livt.IO"="1.2.0-dev"\n')
            app = self.package(root, "app", "UartCliApp", '[dependencies]\n"Eccelerators.Cli"="1.1.0"\n"Livt.IO"="1.2.0-dev"\n')
            _, projects = runner.prepare(root / "stage", root, cli, app)
            self.assertEqual(["WorkspaceMemory", "Eccelerators.Cli", "UartCliApp"], list(projects))
            settings = runner.workspace.load(projects["UartCliApp"])
            self.assertEqual({"path": str(root / "stage/Eccelerators.Cli")}, settings["dependencies"]["Eccelerators.Cli"])

    def test_app_requires_cli(self):
        with self.assertRaisesRegex(ValueError, "requires --cli-root"):
            runner.prepare(Path("unused-stage"), Path("unused-source"), app_root=Path("unused-app"))

    def test_package_identity_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.package(root, "livt-collections", "Wrong")
            with self.assertRaisesRegex(ValueError, "expected Livt.Collections"):
                runner.prepare(root / "stage", root)
