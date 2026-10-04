# Rules

## Must
- Return every output field on every run.
- Set `needs_human` to true when classification confidence is below 0.5.
- Produce identical output for identical input (deterministic).
- Use only the declared tools: classify_issue, estimate_priority, find_duplicates.

## Must Not
- Return priority P0 for any issue that is not a bug.
- Return a summary longer than 140 characters.
- Close, delete, or modify issues.
- Fabricate details that are absent from the issue text.

## Verification
These rules are enforced in code by `core/agent.py::validate_output` and checked
across all runtimes by `verify.py`.
