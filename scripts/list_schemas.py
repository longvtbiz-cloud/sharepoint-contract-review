import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.governance_cli import cmd_schemas


if __name__ == "__main__":
    cmd_schemas(type("Args", (), {"output": None})())
