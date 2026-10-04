# triage-bot: a portable agent passport

A GitHub issue triage agent that runs **unchanged on three runtimes** and proves it with a verification gate.

> Build once. Verify everywhere. Prove your agent can travel.

## What it does
Given an issue (title, body) and a list of existing issue titles, it returns:
`type`, `priority`, `duplicate_of`, `labels`, `needs_human`, `summary`.

## Architecture

```
agent.yaml            <- GitAgent manifest (REQUIRED by the Agent Passport)
SOUL.md               <- identity: role, tone, boundaries
RULES.md              <- behavior contract: must / must not
tools/*.yaml + *.py   <- declarative tool definitions (call the same core functions)
core/
  tools.py            <- plain-Python tools + JSON schemas (no framework imports)
  agent.py            <- result assembly + contract validator
adapters/             <- thin wrappers, NO business logic
  native.py           <- plain Python (reference)
  langgraph_adapter.py<- LangGraph StateGraph
  tool_calling.py     <- Anthropic/OpenAI tool-call protocol
tests/cases.py        <- shared test cases
verify.py             <- runs all cases on all runtimes -> VERIFICATION.md
```

**Design rule:** all decisions live in `core/`. An adapter may only (a) call tools and (b) pass results to `assemble()`. Porting to a new framework means writing one small file.

## Identity and behavior contract (`agent.yaml`, `SOUL.md`, `RULES.md`)
- **Identity:** role, tone, boundaries (never closes issues, never invents facts, flags uncertainty).
- **Contract:** required output fields, `must` and `must_not` rules, enforced in code by `validate_output()`.
- **Key rules:** deterministic for identical input; `needs_human=true` when confidence < 0.5; never P0 for non-bugs; summary <= 140 chars.

## Tool design
Three single-purpose tools, each with a JSON schema usable directly as an Anthropic `input_schema` or OpenAI `parameters`:
`classify_issue`, `estimate_priority`, `find_duplicates`.

## Run it
```bash
pip install -r requirements.txt
python verify.py
```
Exit code is non-zero if any check fails. Results are written to `VERIFICATION.md`.

## Verification
For every case and every runtime, `verify.py` checks: contract compliance, expected behavior, identical output across runtimes, and determinism. Current result: **40/40 pass** (see `VERIFICATION.md`).

## Add a new runtime (e.g. CrewAI, AutoGen)
1. Create `adapters/<name>.py` exposing `run(issue, existing_titles) -> dict`.
2. Call tools from `core.tools.TOOLS`, then `core.agent.assemble`.
3. Add the module name to `RUNTIMES` in `verify.py` and re-run.

## Honest limitations
- Tools are rule-based (keywords, difflib similarity), chosen so results are deterministic and verifiable offline. An LLM-backed classifier can replace `classify_issue` without touching any adapter.
- `tool_calling.py` uses a scripted planner in place of a live model. `dispatch()` and the exported schemas are the real integration surface.
- CrewAI and AutoGen adapters are not included, because only verified runtimes are claimed.

## Third-party components
- `langgraph` (MIT), used only in `adapters/langgraph_adapter.py`.
