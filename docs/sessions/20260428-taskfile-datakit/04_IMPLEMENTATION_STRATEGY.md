# Implementation Strategy

Approach:
- Keep the Taskfile at repo root so it is discoverable from every language slice.
- Use inline shell conditionals to probe for manifests and source files at runtime.
- Keep each task idempotent and safe to run on a checkout that only contains a subset of the
  polyglot tree.

Rationale:
- The repo is not single-language, so a static one-toolchain Taskfile would be misleading.
- Runtime detection keeps the automation usable even if one ecosystem is temporarily absent.

