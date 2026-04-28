# Session Overview

Goal: add a repo-level `Taskfile.yml` that exposes `build`, `test`, `lint`, and `clean` tasks and
detects the active language/toolchain slices in this polyglot repository.

Success criteria:
- `Taskfile.yml` exists at repo root.
- The tasks cover Python, Rust, and Go where those manifests or source trees are present.
- The clean task removes generated artifacts without touching source files.
- The repo is ready to publish on a feature branch with a PR.

