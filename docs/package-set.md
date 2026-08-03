# Livt 0.3.0 Package Set

`Livt` is a manifest package. Its purpose is to publish one coordinated standard
library dependency set.

## Pinned Versions

| Package | Version |
|---|---:|
| `Livt.Base` | `0.2.0` |
| `Livt.Math` | `0.3.1` |
| `Livt.Net` | `0.25.0` |
| `Livt.Crypto` | `1.0.3` |
| `Livt.ML` | `0.2.0` |
| `Livt.IO` | `0.2.0` |
| `Livt.Bus` | `0.3.0` |
| `Livt.Utils` | `0.1.0` |

## Release Checklist

Before publishing a new `Livt` meta-package release:

- confirm every pinned package version exists and is publish-ready
- run `make test` to execute every package suite against this coordinated set
  and run the combined compatibility test
- update `livt.toml`
- update this file
- update the README package table
- keep this repository free of production source components

## Compatibility Boundary

The meta-package promises a convenient compatible bundle. It does not imply that
every package depends on every other package. Package-level dependency direction
remains owned by each focused library.
