EXISTING = ["App crashes on startup with config error", "Add dark mode support", "Typo in README install section"]

CASES = [
    {"name": "crash bug", "issue": {"title": "Crash on startup when config is missing", "body": "Traceback shows exception. App cannot start."}, "expect": {"type": "bug", "priority": "P0"}},
    {"name": "regression bug", "issue": {"title": "Regression: export fails in 2.1", "body": "Export is broken since upgrade, error in logs."}, "expect": {"type": "bug", "priority": "P1"}},
    {"name": "feature request", "issue": {"title": "Please add support for YAML config", "body": "Would be nice to have this feature."}, "expect": {"type": "feature", "priority": "P2"}},
    {"name": "docs typo", "issue": {"title": "Typo in documentation", "body": "The tutorial example is wrong in the README."}, "expect": {"type": "docs", "priority": "P3"}},
    {"name": "question", "issue": {"title": "How do I enable verbose logging?", "body": "Is it possible to see more output?"}, "expect": {"type": "question", "priority": "P3"}},
    {"name": "duplicate", "issue": {"title": "App crashes on startup with config error!", "body": "crash error"}, "expect": {"type": "bug", "duplicate": True}},
    {"name": "vague input", "issue": {"title": "Hello", "body": ""}, "expect": {"needs_human": True}},
    {"name": "long title", "issue": {"title": "Bug: " + "x" * 300, "body": "error"}, "expect": {"type": "bug", "short_summary": True}},
]
