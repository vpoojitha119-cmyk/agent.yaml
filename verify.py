"""Verification gate: runs every case on every runtime and checks
(1) contract compliance, (2) expected behavior, (3) cross-runtime equivalence.
Writes VERIFICATION.md and exits non-zero on any failure."""
import sys
import importlib
from core.agent import validate_output
from tests.cases import CASES, EXISTING

RUNTIMES = ["native", "langgraph_adapter", "tool_calling"]
LABELS = {"native": "native", "langgraph_adapter": "langgraph", "tool_calling": "tool-calling"}


def check_expect(out, expect):
    for k, v in expect.items():
        if k == "duplicate":
            if bool(out["duplicate_of"]) != v:
                return f"duplicate expected {v}"
        elif k == "short_summary":
            if len(out["summary"]) > 140:
                return "summary too long"
        elif out.get(k) != v:
            return f"{k}: expected {v}, got {out.get(k)}"
    return None


def main():
    mods = {r: importlib.import_module(f"adapters.{r}") for r in RUNTIMES}
    rows, failures = [], 0
    for case in CASES:
        outs, cells = {}, []
        for r in RUNTIMES:
            out = mods[r].run(case["issue"], EXISTING)
            outs[r] = out
            err = validate_output(out) or check_expect(out, case["expect"])
            cells.append("PASS" if not err else f"FAIL ({err})")
            failures += bool(err)
        same = all(outs[r] == outs[RUNTIMES[0]] for r in RUNTIMES)
        deterministic = mods["native"].run(case["issue"], EXISTING) == outs["native"]
        failures += (not same) + (not deterministic)
        rows.append((case["name"], cells, same, deterministic))

    header = "| Case | " + " | ".join(LABELS[r] for r in RUNTIMES) + " | Identical across runtimes | Deterministic |"
    sep = "|" + "---|" * (len(RUNTIMES) + 3)
    lines = ["# Verification Results", "", header, sep]
    for name, cells, same, det in rows:
        lines.append(f"| {name} | " + " | ".join(cells) + f" | {'YES' if same else 'NO'} | {'YES' if det else 'NO'} |")
    total = len(CASES) * (len(RUNTIMES) + 2)
    lines += ["", f"**{total - failures}/{total} checks passed.**"]
    open("VERIFICATION.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
