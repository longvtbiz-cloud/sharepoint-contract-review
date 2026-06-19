import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.scenarios import list_scenarios


if __name__ == "__main__":
    print(json.dumps({"scenarios": list_scenarios()}, indent=2, ensure_ascii=False))
