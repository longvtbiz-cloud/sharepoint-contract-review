import json
import os
import operator
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, TypedDict

from dotenv import load_dotenv
from greennode_agentbase import GreenNodeAgentBaseApp, PingStatus, RequestContext
from greennode_agentbase.memory import MemoryClient
from greennode_agentbase.memory.models import MemoryRecordSearchRequest
from greennode_agent_bridge import AgentBaseMemoryEvents
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.config import get_config
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from governance.agents.audit import build_audit_event
from governance.agents.contract_review import prepare_contract_review
from governance.agents.dd import evaluate_dd_gate
from governance.agents.intake import normalize_ticket
from governance.agents.negotiation import build_negotiation_plan
from governance.agents.partner_portal import build_partner_portal_plan
from governance.agents.rbac import evaluate_access, sanitize_response
from governance.agents.sharepoint import build_sharepoint_plan
from governance.agents.termination import build_termination_plan
from governance.contracts import all_api_contracts

load_dotenv()

app = GreenNodeAgentBaseApp()

MEMORY_ID = os.environ.get("MEMORY_ID", "")
MEMORY_STRATEGY_ID = os.environ.get("MEMORY_STRATEGY_ID", "default")

LLM_MODEL = os.environ.get("LLM_MODEL", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

checkpointer = AgentBaseMemoryEvents(memory_id=MEMORY_ID) if MEMORY_ID else None
memory_client = MemoryClient() if MEMORY_ID else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_actor_id() -> str:
    config = get_config()
    return config["configurable"].get("actor_id", "default")


def _build_namespace(actor_id: str) -> str:
    return f"/strategies/{MEMORY_STRATEGY_ID}/actors/{actor_id}"


@tool
def remember_governance_fact(fact: str) -> str:
    """Store a governance fact for the current actor."""
    if not memory_client or not MEMORY_ID:
        return "Memory is not configured."
    namespace = _build_namespace(_get_actor_id())
    memory_client.insert_memory_records_directly(
        id=MEMORY_ID,
        namespace=namespace,
        request=[fact],
    )
    return f"Remembered: {fact}"


@tool
def recall_governance_context(query: str) -> str:
    """Search governance memory for facts relevant to a query."""
    if not memory_client or not MEMORY_ID:
        return "Memory is not configured."
    namespace = _build_namespace(_get_actor_id())
    results = memory_client.search_memory_records(
        id=MEMORY_ID,
        namespace=namespace,
        request=MemoryRecordSearchRequest(query=query, limit=10),
    )
    if not results:
        return "No relevant memories found."
    return "\n".join(f"- {result.memory} (score: {result.score:.2f})" for result in results)


class GovernanceState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    ticket: dict[str, Any]
    access_result: dict[str, Any]
    dd_result: dict[str, Any]
    review_plan: dict[str, Any]
    sharepoint_plan: dict[str, Any]
    negotiation_plan: dict[str, Any]
    partner_portal_plan: dict[str, Any]
    termination_plan: dict[str, Any]
    audit_events: Annotated[list[dict[str, Any]], operator.add]
    status: Literal["draft", "blocked", "ready_for_review", "reviewer_selection_incomplete"]


def intake_agent(state: GovernanceState) -> GovernanceState:
    payload = _latest_json_payload(state)
    ticket = normalize_ticket(payload)
    audit = build_audit_event(
        actor=payload.get("actor", "system"),
        role=payload.get("role", "BIZ_OWNER"),
        action="ticket.normalized",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={},
        after=ticket,
        source=payload.get("source", "api"),
    )
    return {"ticket": ticket, "audit_events": [audit], "status": "draft"}


def rbac_agent(state: GovernanceState) -> GovernanceState:
    payload = _latest_json_payload(state)
    ticket = state["ticket"]
    access_result = evaluate_access(payload, ticket)
    audit = build_audit_event(
        actor=access_result["actor"],
        role=access_result["role"],
        action="rbac.access_evaluated",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={},
        after=access_result,
        source=payload.get("source", "api"),
    )
    status = "draft" if access_result["allowed"] else "blocked"
    return {"access_result": access_result, "audit_events": [audit], "status": status}


def dd_gate_agent(state: GovernanceState) -> GovernanceState:
    ticket = state["ticket"]
    dd_result = evaluate_dd_gate(ticket)
    audit = build_audit_event(
        actor=ticket["created_by"],
        role="DD_REVIEWER",
        action="dd.gate_evaluated",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={"dd_status": ticket.get("dd_status")},
        after=dd_result,
        source="automation",
    )
    status = "ready_for_review" if dd_result["contract_review_allowed"] else "blocked"
    return {"dd_result": dd_result, "audit_events": [audit], "status": status}


def contract_review_agent(state: GovernanceState) -> GovernanceState:
    ticket = state["ticket"]
    review_plan = prepare_contract_review(ticket, state["dd_result"])
    audit = build_audit_event(
        actor=ticket["created_by"],
        role="LEGAL_ADMIN",
        action="contract.review_plan_prepared",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={},
        after=review_plan,
        source="automation",
    )
    status = "ready_for_review" if review_plan["status"] == "Ready" else "reviewer_selection_incomplete"
    return {"review_plan": review_plan, "audit_events": [audit], "status": status}


def sharepoint_agent(state: GovernanceState) -> GovernanceState:
    ticket = state["ticket"]
    sharepoint_plan = build_sharepoint_plan(ticket)
    audit = build_audit_event(
        actor=ticket["created_by"],
        role="SYSTEM",
        action="sharepoint.folder_plan_prepared",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={},
        after=sharepoint_plan,
        source="automation",
    )
    return {"sharepoint_plan": sharepoint_plan, "audit_events": [audit]}


def lifecycle_agent(state: GovernanceState) -> GovernanceState:
    ticket = state["ticket"]
    plans = {
        "negotiation_plan": build_negotiation_plan(ticket),
        "partner_portal_plan": build_partner_portal_plan(ticket),
        "termination_plan": build_termination_plan(ticket),
    }
    active_plans = {key: value for key, value in plans.items() if value}
    if not active_plans:
        return {}

    audit = build_audit_event(
        actor=ticket["created_by"],
        role="SYSTEM",
        action="lifecycle.plans_prepared",
        object_type="ticket",
        object_id=ticket["ticket_id"],
        before={},
        after=active_plans,
        source="automation",
    )
    return {**active_plans, "audit_events": [audit]}


def access_denied_agent(state: GovernanceState) -> GovernanceState:
    access_result = state["access_result"]
    return {
        "messages": [
            SystemMessage(
                content=(
                    "Access denied by RBAC policy: "
                    f"{access_result.get('denied_reason', 'No reason provided.')}"
                )
            )
        ],
        "status": "blocked",
    }


def ai_summary_agent(state: GovernanceState) -> GovernanceState:
    if not LLM_MODEL or not LLM_BASE_URL or not LLM_API_KEY:
        return {
            "messages": [
                SystemMessage(
                    content=(
                        "LLM is not configured. Governance workflow completed with deterministic "
                        "agents only."
                    )
                )
            ]
        }

    llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
    llm_with_tools = llm.bind_tools([remember_governance_fact, recall_governance_context])
    prompt = {
        "ticket": state.get("ticket", {}),
        "dd_result": state.get("dd_result", {}),
        "review_plan": state.get("review_plan", {}),
        "sharepoint_plan": state.get("sharepoint_plan", {}),
        "negotiation_plan": state.get("negotiation_plan", {}),
        "partner_portal_plan": state.get("partner_portal_plan", {}),
        "termination_plan": state.get("termination_plan", {}),
        "access_result": state.get("access_result", {}),
    }
    response = llm_with_tools.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Governance Orchestrator for an Enterprise Partner Governance "
                    "Platform. Summarize the current workflow state, blockers, and next action."
                )
            ),
            HumanMessage(content=json.dumps(prompt, ensure_ascii=False)),
        ]
    )
    return {"messages": [response]}


def route_after_dd(state: GovernanceState) -> str:
    if state["dd_result"]["contract_review_allowed"]:
        return "contract_review_agent"
    return "sharepoint_agent"


def route_after_rbac(state: GovernanceState) -> str:
    if state["access_result"]["allowed"]:
        return "dd_gate_agent"
    return "access_denied_agent"


def _latest_json_payload(state: GovernanceState) -> dict[str, Any]:
    for message in reversed(state.get("messages", [])):
        content = getattr(message, "content", "")
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return {"message": content}
            if isinstance(parsed, dict):
                return parsed
    return {}


graph_builder = StateGraph(GovernanceState)
graph_builder.add_node("intake_agent", intake_agent)
graph_builder.add_node("rbac_agent", rbac_agent)
graph_builder.add_node("dd_gate_agent", dd_gate_agent)
graph_builder.add_node("contract_review_agent", contract_review_agent)
graph_builder.add_node("sharepoint_agent", sharepoint_agent)
graph_builder.add_node("lifecycle_agent", lifecycle_agent)
graph_builder.add_node("access_denied_agent", access_denied_agent)
graph_builder.add_node("ai_summary_agent", ai_summary_agent)
graph_builder.add_node("tools", ToolNode([remember_governance_fact, recall_governance_context]))

graph_builder.add_edge(START, "intake_agent")
graph_builder.add_edge("intake_agent", "rbac_agent")
graph_builder.add_conditional_edges(
    "rbac_agent",
    route_after_rbac,
    {
        "dd_gate_agent": "dd_gate_agent",
        "access_denied_agent": "access_denied_agent",
    },
)
graph_builder.add_edge("access_denied_agent", "ai_summary_agent")
graph_builder.add_conditional_edges(
    "dd_gate_agent",
    route_after_dd,
    {
        "contract_review_agent": "contract_review_agent",
        "sharepoint_agent": "sharepoint_agent",
    },
)
graph_builder.add_edge("contract_review_agent", "sharepoint_agent")
graph_builder.add_edge("sharepoint_agent", "lifecycle_agent")
graph_builder.add_edge("lifecycle_agent", "ai_summary_agent")
graph_builder.add_conditional_edges("ai_summary_agent", tools_condition)
graph_builder.add_edge("tools", "ai_summary_agent")
graph_builder.add_edge("ai_summary_agent", END)

graph = graph_builder.compile(checkpointer=checkpointer) if checkpointer else graph_builder.compile()


@app.entrypoint
def handler(payload: dict, context: RequestContext) -> dict:
    if MEMORY_ID and (not context.user_id or not context.session_id):
        return {
            "status": "error",
            "error": (
                "Missing required headers: X-GreenNode-AgentBase-User-Id and "
                "X-GreenNode-AgentBase-Session-Id are required when MEMORY_ID is configured."
            ),
        }

    message = payload if isinstance(payload, dict) else {"message": str(payload)}
    config = {
        "configurable": {
            "thread_id": context.session_id or f"local-{_utc_now()}",
            "actor_id": context.user_id or payload.get("created_by", "local-user"),
        }
    }
    result = graph.invoke({"messages": [HumanMessage(content=json.dumps(message, ensure_ascii=False))]}, config)

    response = {
        "status": "success",
        "ticket": result.get("ticket"),
        "access_result": result.get("access_result"),
        "dd_result": result.get("dd_result"),
        "review_plan": result.get("review_plan"),
        "sharepoint_plan": result.get("sharepoint_plan"),
        "negotiation_plan": result.get("negotiation_plan"),
        "partner_portal_plan": result.get("partner_portal_plan"),
        "termination_plan": result.get("termination_plan"),
        "audit_events": result.get("audit_events", []),
        "api_contracts": all_api_contracts(),
        "workflow_status": result.get("status"),
        "ai_summary": result["messages"][-1].content if result.get("messages") else None,
        "timestamp": _utc_now(),
    }
    return sanitize_response(response, result.get("access_result"))


@app.ping
def health_check() -> PingStatus:
    return PingStatus.HEALTHY


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
