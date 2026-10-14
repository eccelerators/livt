# Livt Usage

## Full Standard-Library Dependency

Use the meta-package when an application wants the full Livt standard library:

```toml
[dependencies]
Livt = "1.1.0"
```

This brings in the package versions pinned by `Livt 1.1.0`.

## Focused Library Dependency

Reusable libraries should usually depend only on the packages they use:

```toml
[dependencies]
Livt.Math = "1.3.0"
Livt.IO = "1.2.0"
```

This keeps dependency boundaries clear and avoids pulling unrelated domains into
small packages.

## Importing Components

`Livt` itself does not define source namespaces. Import components from the
focused packages:

```livt
using Livt.Math.FixedPoint
using Livt.IO
using Livt.Utils.Hashing
```

The namespaces are owned by the packages that implement the components.

## Workspace Memory Verification

Run `make test-workspace-memory` to verify the current sibling Livt.IO and
Livt.Collections sources without publishing them or changing version pins.
Pass `WORKSPACE_ARGS="--cli-root ../eccelerators-cli"` to include the CLI's
tests; add `--app-root ../../livt-demo/livt-uart-cli-app` for its UART consumer.
The runner prints the retained snapshot/log directory and fails visibly on
any consumer error. Add `--release` or `--no-optimizations` to select the profile.
