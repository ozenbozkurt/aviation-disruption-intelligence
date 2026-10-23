# Release process

## v0.5.0 checklist

Before publishing the release:

1. Confirm the protected `main` branch is green on all required Windows/Linux checks.
2. Confirm `python -m build` succeeds in CI.
3. Confirm installed package metadata and `aviation_disruption.__version__` both report `0.5.0`.
4. Confirm the real-data case-study workflow installs both the EUROCONTROL and DuckDB extras.
5. Confirm the generated case-study bundle contains CSV, DuckDB, Parquet, Markdown and AI-explanation artifacts.
6. Confirm README safety, provenance and data-source limitations remain visible.
7. Merge the release-preparation pull request.
8. Create a GitHub release from `main` with tag `v0.5.0`.
9. Use `CHANGELOG.md` as the basis for the release notes.

This repository is not currently published to PyPI. A GitHub release is the maintained distribution marker for this milestone.
