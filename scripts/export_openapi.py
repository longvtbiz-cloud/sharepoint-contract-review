import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governance.openapi import build_openapi_spec


if __name__ == "__main__":
    print(json.dumps(build_openapi_spec(), indent=2, ensure_ascii=False))
