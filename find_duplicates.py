import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from core.tools import TOOLS

args = json.load(sys.stdin)
print(json.dumps(TOOLS["find_duplicates"]["fn"](**args)))
