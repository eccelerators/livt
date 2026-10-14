# Livt 1.1.0 Package Set

The authoritative release pins are in [livt.toml](../livt.toml):

| Package | Version |
|---|---|
| Livt.Base | 1.2.0 |
| Livt.Bus | 1.0.2 |
| Livt.Collections | 1.1.0 |
| Livt.Crypto | 1.0.4 |
| Livt.IO | 1.2.0 |
| Livt.Math | 1.3.0 |
| Livt.ML | 1.4.1 |
| Livt.Net | 1.1.0 |
| Livt.Utils | 1.0.2 |

## Verification modes

- `make test`: pinned package suites and the released combined compatibility test.
- `make test-integration`: only that combined compatibility test.
- `make test-workspace`: all sibling package suites in an isolated source snapshot,
  followed by combined compatibility and the current iterator API checks.
- `make test-workspace-integration`: only the combined workspace checks.
- `make test-workspace-iterators`: focused Base/Collections compatibility with
  separate reports, useful when investigating iterator failures.

Workspace mode does not change the release pins and does not establish that a
published bundle is compatible. It records source versions, Git revisions and dirty
status in its report directory. A dirty workspace remains a development snapshot,
not an immutable released dependency set.

## Ownership and release checklist

Package-specific tests stay with their packages; this repository orchestrates them
and owns cross-package compatibility tests. Compiler-language regressions belong
in livt-gen-vhdl-verification with minimal fixture-owned models.

Before publishing: select available package versions deliberately, run the pinned
suite, promote applicable workspace-only compatibility tests, and update the
manifest, README table and this document together. No production components belong
in this meta-package.
