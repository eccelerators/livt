#!/usr/bin/env python3
"""Verify workspace RAM APIs and optional CLI consumers without changing package pins."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("workspace_runner", ROOT / "ci/test-workspace.py")
workspace = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspace)


def prepare(stage, workspace_root, cli_root=None, app_root=None):
    sources = {name: workspace_root / folder for name, folder in
               (("Livt.Collections", "livt-collections"), ("Livt.IO", "livt-io"))}
    if cli_root:
        sources["Eccelerators.Cli"] = cli_root
    if app_root:
        if not cli_root:
            raise ValueError("--app-root requires --cli-root")
        sources["UartCliApp"] = app_root
    paths = {name: stage / name for name in sources}
    for name, source in sources.items():
        if workspace.load(source)["project"]["name"] != name:
            raise ValueError(f"Unexpected package at {source}: expected {name}")
        workspace.stage_project(source, paths[name], paths)
    integration = stage / "WorkspaceMemory"
    (integration / "tests").mkdir(parents=True)
    (integration / "src").mkdir()
    shutil.copy2(ROOT / "workspace-tests/WorkspaceMemoryCompatibility.lvt", integration / "tests")
    settings = {"project": {"name": "WorkspaceMemory", "path": "src", "outdir": "out"},
                "tests": {"path": "tests", "components": ["WorkspaceMemoryCompatibility"]},
                "dependencies": {"Livt.IO": {"path": str(paths["Livt.IO"])}},
                "vhdl": {"file_header": False}}
    (integration / "livt.toml").write_text(workspace.manifest_text(settings))
    projects = {"WorkspaceMemory": integration}
    for name in ("Eccelerators.Cli", "UartCliApp"):
        if name in paths:
            projects[name] = paths[name]
    return sources, projects


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, default=ROOT.parent)
    parser.add_argument("--cli-root", type=Path)
    parser.add_argument("--app-root", type=Path)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--no-optimizations", action="store_true")
    args = parser.parse_args()
    stage = Path(tempfile.mkdtemp(prefix="livt-memory-workspace-"))
    print(f"Workspace snapshot and evidence: {stage}", flush=True)
    sources, projects = prepare(stage, args.workspace_root.resolve(), args.cli_root, args.app_root)
    (stage / "workspace.json").write_text(json.dumps(
        {"packages": {name: workspace.revision(source) for name, source in sources.items()},
         "release": args.release, "optimizations": "none" if args.no_optimizations else "default"},
        indent=2) + "\n")
    environment = dict(os.environ)
    environment.pop("_JAVA_OPTIONS", None)
    flags = (["-R"] if args.release else []) + (["-O", "none"] if args.no_optimizations else [])
    for name, project in projects.items():
        print(f"Testing {name}...", flush=True)
        with (stage / (name + ".log")).open("w") as log:
            result = subprocess.run([environment.get("LIVT", "livt"), "test", "-f", *flags,
                                     "--junit", str(stage / (name + ".xml"))],
                                    cwd=project, env=environment, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=600)
        if result.returncode:
            parser.exit(1, f"FAILED {name}: see {stage / (name + '.log')}\n")
    print("Workspace memory verification passed.")


if __name__ == "__main__":
    main()
