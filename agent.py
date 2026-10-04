"""Runtime-neutral agent logic: result assembly and contract validation.
The contract mirrored here is documented in agent.yaml, SOUL.md and RULES.md."""
REQUIRED_FIELDS = ["type", "priority", "duplicate_of", "labels", "needs_human", "summary"]


def build_labels(issue_type, priority, duplicate_of):
    labels = [issue_type, f"priority:{priority}"]
    if duplicate_of:
        labels.append("duplicate")
    return labels


def assemble(issue, classification, priority, dup):
    """Pure function: combine tool outputs into a contract-compliant result."""
    title = issue["title"].strip()
    summary = title if len(title) <= 140 else title[:137] + "..."
    return {
        "type": classification["type"],
        "priority": priority["priority"],
        "duplicate_of": dup["duplicate_of"],
        "labels": build_labels(classification["type"], priority["priority"], dup["duplicate_of"]),
        "needs_human": classification["confidence"] < 0.5,
        "summary": summary,
    }


def validate_output(out: dict) -> list:
    """Check output against the contract in agent.yaml, SOUL.md and RULES.md. Returns a list of violations."""
    errors = [f"missing field: {f}" for f in REQUIRED_FIELDS if f not in out]
    if errors:
        return errors
    if out["type"] not in {"bug", "feature", "question", "docs"}:
        errors.append("invalid type")
    if out["priority"] not in {"P0", "P1", "P2", "P3"}:
        errors.append("invalid priority")
    if out["priority"] == "P0" and out["type"] != "bug":
        errors.append("must_not: P0 for non-bug")
    if len(out["summary"]) > 140:
        errors.append("must_not: summary > 140 chars")
    if not isinstance(out["labels"], list) or not isinstance(out["needs_human"], bool):
        errors.append("wrong field types")
    return errors
