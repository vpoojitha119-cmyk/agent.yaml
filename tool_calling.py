"""Runtime 3: LLM tool-calling protocol (Anthropic / OpenAI style).

Exports the core tools as provider-ready schemas and dispatches tool calls the way
an LLM runtime would. A scripted 'planner' stands in for the model so the
adapter is testable offline. To use a real model, replace `plan()` with an API call
that returns tool_use blocks; dispatch() stays the same."""
from core.tools import TOOLS
from core.agent import assemble


def anthropic_tool_specs():
    return [{"name": n, "description": t["description"], "input_schema": t["parameters"]} for n, t in TOOLS.items()]


def openai_tool_specs():
    return [{"type": "function", "function": {"name": n, "description": t["description"], "parameters": t["parameters"]}}
            for n, t in TOOLS.items()]


def dispatch(name: str, args: dict) -> dict:
    if name not in TOOLS:
        raise ValueError(f"unknown tool: {name}")
    return TOOLS[name]["fn"](**args)


def plan(issue, existing_titles):
    """Stand-in for a model: yields tool calls, receiving earlier results."""
    body = issue.get("body", "")
    c = yield ("classify_issue", {"title": issue["title"], "body": body})
    p = yield ("estimate_priority", {"issue_type": c["type"], "title": issue["title"], "body": body})
    d = yield ("find_duplicates", {"title": issue["title"], "existing_titles": existing_titles or []})
    return c, p, d


def run(issue: dict, existing_titles: list = None) -> dict:
    gen = plan(issue, existing_titles)
    results = []
    call = next(gen)
    try:
        while True:
            out = dispatch(*call)
            results.append(out)
            call = gen.send(out)
    except StopIteration:
        pass
    c, p, d = results
    return assemble(issue, c, p, d)
