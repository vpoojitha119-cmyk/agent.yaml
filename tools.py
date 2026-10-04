"""Framework-free tools. Plain functions + JSON-schema descriptions.
Nothing here imports any agent framework."""
import difflib
import re

TYPE_KEYWORDS = {
    "bug": ["crash", "error", "exception", "fails", "broken", "traceback", "regression", "bug", "not working"],
    "feature": ["feature", "support for", "would be nice", "please add", "enhancement", "proposal", "add support"],
    "docs": ["docs", "documentation", "typo", "readme", "tutorial", "example is wrong"],
    "question": ["how do i", "how to", "question", "is it possible", "why does", "?"],
}
URGENT = ["data loss", "security", "vulnerability", "production down", "crash on startup", "cannot start"]


def classify_issue(title: str, body: str = "") -> dict:
    text = f"{title} {body}".lower()
    scores = {t: sum(text.count(k) for k in kws) for t, kws in TYPE_KEYWORDS.items()}
    total = sum(scores.values())
    if total == 0:
        return {"type": "question", "confidence": 0.2}
    best = max(sorted(scores), key=lambda t: scores[t])
    return {"type": best, "confidence": round(scores[best] / total, 2)}


def estimate_priority(issue_type: str, title: str, body: str = "") -> dict:
    text = f"{title} {body}".lower()
    if issue_type == "bug":
        if any(u in text for u in URGENT):
            return {"priority": "P0"}
        return {"priority": "P1" if "regression" in text or "crash" in text else "P2"}
    if issue_type == "feature":
        return {"priority": "P2"}
    return {"priority": "P3"}


def find_duplicates(title: str, existing_titles: list = None, threshold: float = 0.75) -> dict:
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    best, best_score = None, 0.0
    for other in existing_titles or []:
        score = difflib.SequenceMatcher(None, norm(title), norm(other)).ratio()
        if score > best_score:
            best, best_score = other, score
    return {"duplicate_of": best if best_score >= threshold else None, "similarity": round(best_score, 2)}


TOOLS = {
    "classify_issue": {
        "fn": classify_issue,
        "description": "Classify a GitHub issue as bug, feature, question or docs, with a confidence score.",
        "parameters": {
            "type": "object",
            "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
            "required": ["title"],
        },
    },
    "estimate_priority": {
        "fn": estimate_priority,
        "description": "Estimate priority P0-P3 from issue type and text.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string", "enum": ["bug", "feature", "question", "docs"]},
                "title": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["issue_type", "title"],
        },
    },
    "find_duplicates": {
        "fn": find_duplicates,
        "description": "Check whether an issue title closely matches an existing issue title.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "existing_titles": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title"],
        },
    },
}
