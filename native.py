"""Runtime 1: plain Python. The reference implementation."""
from core.tools import classify_issue, estimate_priority, find_duplicates
from core.agent import assemble


def run(issue: dict, existing_titles: list = None) -> dict:
    c = classify_issue(issue["title"], issue.get("body", ""))
    p = estimate_priority(c["type"], issue["title"], issue.get("body", ""))
    d = find_duplicates(issue["title"], existing_titles)
    return assemble(issue, c, p, d)
