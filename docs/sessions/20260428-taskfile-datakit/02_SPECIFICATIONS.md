# Specifications

Taskfile requirements:
- Provide top-level `build`, `test`, `lint`, and `clean` tasks.
- Detect the repo's active language slices from manifests or source files.
- Run the relevant commands for Python, Rust, and Go when present.
- Avoid failing on absent ecosystems.

Acceptance criteria:
- `task build`, `task test`, `task lint`, and `task clean` are all defined.
- Python commands use `uv` when available and fall back to the direct tools.
- Rust commands use Cargo workspace commands.
- Go commands only run when Go source files are present.

