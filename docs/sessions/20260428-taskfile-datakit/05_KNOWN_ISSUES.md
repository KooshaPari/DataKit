# Known Issues

- The current checkout has no Go source files, so the Go branches of the Taskfile will skip until
  those packages exist.
- The Python tasks assume `uv` is available for the best path; without it, they fall back to the
  locally installed `build`, `pytest`, `ruff`, and `mypy` commands.
- `task lint` currently fails on pre-existing Ruff issues in `python/db-kit` (module naming,
  `B904`, and a few unused-import/style findings).
