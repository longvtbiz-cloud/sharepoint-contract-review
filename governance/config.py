import os
from copy import deepcopy
from typing import Any


CONFIG_VARIABLES: list[dict[str, Any]] = [
    {
        "name": "GREENNODE_CLIENT_ID",
        "group": "agentbase",
        "required_for": ["deploy", "runtime"],
        "secret": False,
        "description": "GreenNode IAM service account client ID.",
    },
    {
        "name": "GREENNODE_CLIENT_SECRET",
        "group": "agentbase",
        "required_for": ["deploy", "runtime"],
        "secret": True,
        "description": "GreenNode IAM service account client secret.",
    },
    {
        "name": "GREENNODE_AGENT_IDENTITY",
        "group": "agentbase",
        "required_for": [],
        "secret": False,
        "description": "Optional AgentBase identity ID for deployed runtime operations.",
    },
    {
        "name": "LLM_API_KEY",
        "group": "llm",
        "required_for": ["ai_summary"],
        "secret": True,
        "description": "API key for an OpenAI-compatible LLM provider.",
    },
    {
        "name": "LLM_BASE_URL",
        "group": "llm",
        "required_for": ["ai_summary"],
        "secret": False,
        "description": "Base URL for an OpenAI-compatible LLM provider.",
    },
    {
        "name": "LLM_MODEL",
        "group": "llm",
        "required_for": ["ai_summary"],
        "secret": False,
        "description": "Model name used by the AI summary agent.",
    },
    {
        "name": "MEMORY_ID",
        "group": "memory",
        "required_for": ["agentbase_memory"],
        "secret": False,
        "description": "AgentBase memory store ID for LangGraph checkpointing and long-term memory.",
    },
    {
        "name": "MEMORY_STRATEGY_ID",
        "group": "memory",
        "required_for": [],
        "secret": False,
        "default": "default",
        "description": "Memory namespace strategy ID.",
    },
]


def list_config_variables() -> list[dict[str, Any]]:
    return deepcopy(CONFIG_VARIABLES)


def validate_environment(mode: str, environ: dict[str, str] | None = None) -> dict[str, Any]:
    values = os.environ if environ is None else environ
    missing = [
        variable["name"]
        for variable in CONFIG_VARIABLES
        if mode in variable["required_for"] and not values.get(variable["name"])
    ]
    return {
        "mode": mode,
        "status": "ready" if not missing else "missing_required_values",
        "missing": missing,
    }
