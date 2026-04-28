# Research

Repo layout and command references:
- `README.md` describes the project as polyglot: Python, Go, and Rust.
- `python/db-kit/pyproject.toml` defines Python lint/test tooling with `ruff`, `mypy`, and `pytest`.
- `rust/Cargo.toml` defines a workspace with `cargo build`, `cargo test`, and `cargo clippy`.
- `go/go.work` is present, but there are no Go packages or `.go` files in the current checkout.
- `task --version` is available locally, so the Taskfile can be validated with the installed Task CLI.

Implementation choice:
- Use runtime detection inside the Taskfile instead of hardcoding a single language.
- Skip ecosystems that are not present in the checkout.

