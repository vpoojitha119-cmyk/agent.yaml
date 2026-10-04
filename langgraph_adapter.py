"""Runtime 2: LangGraph. Nodes only call core tools; no business logic here."""
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from core.tools import TOOLS
from core.agent import assemble


class State(TypedDict, total=False):
    issue: dict
    existing_titles: list
    classification: dict
    priority: dict
    dup: dict
    result: Any


def _classify(s):
    i = s["issue"]
    return {"classification": TOOLS["classify_issue"]["fn"](i["title"], i.get("body", ""))}


def _prioritize(s):
    i = s["issue"]
    return {"priority": TOOLS["estimate_priority"]["fn"](s["classification"]["type"], i["title"], i.get("body", ""))}


def _dedupe(s):
    return {"dup": TOOLS["find_duplicates"]["fn"](s["issue"]["title"], s.get("existing_titles"))}


def _finish(s):
    return {"result": assemble(s["issue"], s["classification"], s["priority"], s["dup"])}


def _build():
    g = StateGraph(State)
    g.add_node("classify", _classify)
    g.add_node("prioritize", _prioritize)
    g.add_node("dedupe", _dedupe)
    g.add_node("finish", _finish)
    g.set_entry_point("classify")
    g.add_edge("classify", "prioritize")
    g.add_edge("prioritize", "dedupe")
    g.add_edge("dedupe", "finish")
    g.add_edge("finish", END)
    return g.compile()


_GRAPH = _build()


def run(issue: dict, existing_titles: list = None) -> dict:
    return _GRAPH.invoke({"issue": issue, "existing_titles": existing_titles or []})["result"]
