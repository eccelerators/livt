# Livt

`Livt` is the standard-library meta-package for Livt projects. It gives
applications and larger packages one dependency that brings in the official Livt
library packages as a tested, compatible set.

The 1.0.1 package is a manifest bundle. It does not publish production source
components of its own; it pins versions of the focused library packages that
make up the current Livt standard library and provides an integration test for
the complete package set.

## 📦 Package

```toml
[dependencies]
Livt = "1.0.1"
```

Use `Livt` when an application wants the full standard library surface. Smaller
reusable packages should usually depend only on the specific package they need,
such as `Livt.Math`, `Livt.IO`, or `Livt.Crypto`.

## 📚 Package Set

`Livt 1.0.1` pins this compatible package set:

| Package | Version | Role |
|---|---:|---|
| `Livt.Base` | `1.0.1` | Foundational helpers and common library components |
| `Livt.Bus` | `1.0.1` | Reusable AXI4-Lite, Avalon, Wishbone, and bridge components |
| `Livt.Collections` | `1.0.1` | Fixed-capacity queues, stacks, lists, circular buffers, and bit sets |
| `Livt.Crypto` | `1.0.3` | Cryptographic primitives, hashes, MACs, KDFs, AEADs, and DRBGs |
| `Livt.IO` | `1.0.1` | RAM, UART, and I²C components |
| `Livt.Math` | `1.0.0` | Numeric, fixed-point, arithmetic, lookup, and random helpers |
| `Livt.ML` | `1.0.1` | Fixed-size ML building blocks and approximation/reference components |
| `Livt.Net` | `1.0.1` | Ethernet, ARP, IPv4, ICMP, TCP, checksums, and EthernetLite helpers |
| `Livt.Utils` | `1.0.1` | General-purpose utility components such as CRC32 |

The authoritative dependency pins live in [`livt.toml`](livt.toml). Keep the
table above aligned with that manifest when preparing a new meta-package release.

## 🔌 Dependency Policy

`Livt` is for consumers that want the whole standard library. It is intentionally
not a replacement for precise dependencies in small reusable libraries.

Good fits for depending on `Livt`:

- application packages
- board demos and integration projects
- examples that intentionally show multiple standard-library areas
- internal projects that prefer one coordinated upgrade point

Good fits for depending on focused packages directly:

- a math helper package that only needs `Livt.Math`
- a networking package that only needs `Livt.IO`
- a crypto wrapper that only needs `Livt.Crypto`
- a utility package that should stay dependency-light

## 🧪 Build and Test

Run the complete standard-library verification from this repository:

```sh
make test
```

The command synchronizes the pinned package set, runs every package's own test
suite in an isolated writable workspace using the dependency versions pinned by
this meta-package, and then runs this project's combined compatibility test.
JUnit reports are written below
`.livt/reports/standard-library`.

To run only the combined compatibility test:

```sh
make test-integration
```

Supporting notes live in [`docs/package-set.md`](docs/package-set.md) and
[`docs/usage.md`](docs/usage.md).

## 🛠️ Development Notes

- Keep `Livt` free of production source components.
- Keep package-specific tests in their owning repositories; this project only
  owns cross-package compatibility coverage and orchestration.
- Add new standard-library packages here only after they are publish-ready on
  their own.
- Update `livt.toml`, the README package table, and `docs/package-set.md`
  together.
- Use focused package dependencies for reusable libraries unless the full bundle
  is genuinely intended.

## 🚧 Outlook

Future `Livt` releases should track stable combinations of the standard library
packages. The meta-package version can move independently from the individual
package versions whenever the compatible bundle changes.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
