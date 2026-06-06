# Livt 0.1.0 Package Set

`Livt` is a manifest package. Its purpose is to publish one coordinated standard
library dependency set.

## Pinned Versions

| Package | Version |
|---|---:|
| `Livt.Base` | `0.1.1` |
| `Livt.Math` | `0.3.0` |
| `Livt.Net` | `0.24.1` |
| `Livt.Crypto` | `1.0.1` |
| `Livt.ML` | `0.1.0` |
| `Livt.IO` | `0.1.0` |
| `Livt.Utils` | `0.1.0` |

## Release Checklist

Before publishing a new `Livt` meta-package release:

- confirm every pinned package version exists and is publish-ready
- run each package's configured `livt test`
- expect this repository itself to have no local test VHDL because it is manifest-only
- update `livt.toml`
- update this file
- update the README package table
- keep this repository source-free unless the package policy changes

## Compatibility Boundary

The meta-package promises a convenient compatible bundle. It does not imply that
every package depends on every other package. Package-level dependency direction
remains owned by each focused library.
