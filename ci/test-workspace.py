#!/usr/bin/env python3
"""Verify a coherent snapshot of sibling libraries without changing release pins."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def load(project):
    return tomllib.loads((project / "livt.toml").read_text())


def dependencies(table, prefix=""):
    for name, value in table.items():
        name = prefix + name
        if isinstance(value, dict) and not {"path", "version"}.intersection(value):
            yield from dependencies(value, name + ".")
        else:
            yield name, value


def value_text(value):
    if isinstance(value, dict):
        return "{" + ", ".join(json.dumps(k) + " = " + value_text(v) for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(value_text(v) for v in value) + "]"
    return json.dumps(value)


def manifest_text(data, path=()):
    lines = ["[" + ".".join(json.dumps(key) for key in path) + "]"] if path else []
    for key, value in data.items():
        if not isinstance(value, dict):
            lines.append(json.dumps(key) + " = " + value_text(value))
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(manifest_text(value, path + (key,)))
    return "\n".join(lines) + "\n"


def stage_project(source, target, package_paths):
    settings = copy.deepcopy(load(source))
    for section, fallback in (("project", "src"), ("tests", "tests")):
        relative = Path(settings.get(section, {}).get("path", fallback))
        if relative.is_absolute() or not (source / relative).resolve().is_relative_to(source.resolve()):
            raise ValueError(f"Source path must stay in {source}: {relative}")
        if (source / relative).is_dir():
            shutil.copytree(source / relative, target / relative, dirs_exist_ok=True)
    rewritten = {}
    for name, specification in dependencies(settings.get("dependencies", {})):
        if name not in package_paths:
            raise ValueError(f"Unmapped workspace dependency {name} in {source}; refusing a mixed package set")
        rewritten[name] = {"path": str(package_paths[name])}
    settings["dependencies"] = rewritten
    settings.setdefault("project", {})["outdir"] = "out"
    target.mkdir(parents=True, exist_ok=True)
    (target / "livt.toml").write_text(manifest_text(settings))
    return settings


def revision(source):
    def git(*args):
        result = subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {"path": str(source), "version": load(source)["project"]["version"],
            "commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}


def prepare(project, workspace_root, stage, report_dir, iterators_only=False):
    names = list(dict(dependencies(load(project)["dependencies"])))
    sources = {name: workspace_root / name.lower().replace(".", "-") for name in names}
    for name, source in sources.items():
        if not (source / "livt.toml").is_file() or load(source)["project"]["name"] != name:
            raise ValueError(f"Missing or mismatched workspace package {name}: {source}")
    paths = {name: stage / name for name in names}
    for name, source in sources.items():
        stage_project(source, paths[name], paths)
    combined = stage / "Livt"
    settings = stage_project(project, combined, paths)
    if iterators_only:
        (combined / "workspace-tests").mkdir(exist_ok=True)
        shutil.copy2(project / "workspace-tests/WorkspaceIteratorCompatibility.lvt", combined / "workspace-tests")
        settings["tests"] = {"path": "workspace-tests", "components": ["WorkspaceIteratorCompatibility"]}
        settings["dependencies"] = {name: settings["dependencies"][name]
                                    for name in ("Livt.Base", "Livt.Collections")}
    else:
        shutil.copytree(project / "workspace-tests", combined / "tests", dirs_exist_ok=True)
        settings["tests"]["components"].append("WorkspaceIteratorCompatibility")
        settings["tests"]["components"].append("WorkspaceMemoryCompatibility")
    (combined / "livt.toml").write_text(manifest_text(settings))
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "workspace.json").write_text(json.dumps(
        {"mode": "workspace-iterators" if iterators_only else "workspace",
         "integration_dependencies": list(settings["dependencies"]),
         "packages": {name: revision(source) for name, source in sources.items()}}, indent=2) + "\n")
    return paths, combined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, default=ROOT.parent)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--integration-only", action="store_true")
    mode.add_argument("--iterators-only", action="store_true")
    args = parser.parse_args()
    reports = ROOT / ".livt/reports" / ("workspace-iterators" if args.iterators_only else "workspace")
    livt = os.environ.get("LIVT", "livt")
    failures = []
    try:
        with tempfile.TemporaryDirectory(prefix="livt-workspace-") as temporary:
            packages, combined = prepare(ROOT, args.workspace_root.resolve(), Path(temporary), reports, args.iterators_only)
            projects = {} if args.integration_only or args.iterators_only else packages
            for name, project in [*projects.items(), ("Livt", combined)]:
                print(f"Testing workspace {name}...", flush=True)
                with (reports / f"{name}.log").open("w") as log:
                    result = subprocess.run([livt, "test", "-f", "--project", str(project),
                                             "--junit", str(reports / f"{name}.xml")],
                                            stdout=log, stderr=subprocess.STDOUT)
                if result.returncode:
                    failures.append(name)
                    print(f"FAILED: {name}; see {reports / (name + '.log')}", flush=True)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Workspace verification setup failed: {error}\n")
    print(f"Workspace reports: {reports}")
    if failures:
        parser.exit(1, "Workspace verification failed: " + ", ".join(failures) + "\n")
    print("Workspace verification passed.")


if __name__ == "__main__":
    main()
