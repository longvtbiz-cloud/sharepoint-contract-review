import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.schemas import list_schemas


if __name__ == "__main__":
    print(json.dumps({"schemas": list_schemas()}, indent=2, ensure_ascii=False))
