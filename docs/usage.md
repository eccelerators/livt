# Livt Usage

## Full Standard-Library Dependency

Use the meta-package when an application wants the full Livt standard library:

```toml
[dependencies]
Livt = "0.3.0"
```

This brings in the package versions pinned by `Livt 0.3.0`.

## Focused Library Dependency

Reusable libraries should usually depend only on the packages they use:

```toml
[dependencies]
Livt.Math = "0.3.1"
Livt.IO = "0.2.0"
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
