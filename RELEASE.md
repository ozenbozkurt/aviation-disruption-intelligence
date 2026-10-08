# Release process

## v0.4.1 checklist

Before publishing the release:

1. Confirm the protected `main` branch is green on all required Windows/Linux checks.
2. Confirm `python -m build` succeeds in CI.
3. Confirm installed package metadata and `aviation_disruption.__version__` both report `0.4.1`.
4. Confirm README safety and data-source limitations are still visible.
5. Merge the release-preparation pull request.
6. Create a GitHub release from `main` with tag `v0.4.1`.
7. Use `CHANGELOG.md` as the basis for the release notes.

This repository is not currently published to PyPI. A GitHub release is the maintained distribution marker for this milestone.
