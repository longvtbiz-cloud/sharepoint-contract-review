import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.governance_cli import cmd_openapi


if __name__ == "__main__":
    cmd_openapi(type("Args", (), {"output": None})())
