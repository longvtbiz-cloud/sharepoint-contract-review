let dashboardData = null;
let activeStatus = "all";
let selectedScenarioId = null;

const byId = (id) => document.getElementById(id);

function statusClass(status) {
  return `status status-${String(status || "unknown").replaceAll(" ", "_")}`;
}

function labelize(value) {
  return String(value || "Unknown").replaceAll("_", " ");
}

function setText(id, value) {
  byId(id).textContent = value;
}

function renderMetrics(data) {
  setText("scenarioCount", data.summary.scenario_count);
  setText("agentCount", data.summary.agent_count);
  setText("contractCount", data.summary.api_contract_count);
  setText("edgeCount", data.summary.topology_edge_count);
  setText("nodeCount", `${data.summary.topology_node_count} nodes`);
}

function filteredScenarios() {
  const query = byId("scenarioSearch").value.trim().toLowerCase();
  return dashboardData.scenarios.filter((scenario) => {
    const statusMatch = activeStatus === "all" || scenario.actual_workflow_status === activeStatus;
    const queryText = [
      scenario.title,
      scenario.partner_name,
      scenario.action,
      scenario.role,
      scenario.actual_workflow_status,
    ]
      .join(" ")
      .toLowerCase();
    return statusMatch && (!query || queryText.includes(query));
  });
}

function renderScenarioRows() {
  const tbody = byId("scenarioRows");
  const rows = filteredScenarios();
  byId("queueCount").textContent = `${rows.length} shown`;
  tbody.innerHTML = "";

  if (!rows.length) {
    tbody.appendChild(byId("emptyTemplate").content.cloneNode(true));
    return;
  }

  for (const scenario of rows) {
    const tr = document.createElement("tr");
    tr.className = scenario.scenario_id === selectedScenarioId ? "selected" : "";
    tr.tabIndex = 0;
    tr.innerHTML = `
      <td>
        <div class="scenario-title">${scenario.title}</div>
        <div class="subtle">${scenario.scenario_id}</div>
      </td>
      <td>${scenario.partner_name || "Unknown"}</td>
      <td>${scenario.role || "Unknown"}</td>
      <td><span class="${statusClass(scenario.actual_workflow_status)}">${labelize(scenario.actual_workflow_status)}</span></td>
      <td>${scenario.risk_level || "Hidden"}</td>
      <td>${scenario.audit_event_count}</td>
    `;
    tr.addEventListener("click", () => {
      selectedScenarioId = scenario.scenario_id;
      renderScenarioRows();
      renderTrace();
    });
    tr.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        selectedScenarioId = scenario.scenario_id;
        renderScenarioRows();
        renderTrace();
      }
    });
    tbody.appendChild(tr);
  }
}

function renderBars() {
  const container = byId("workflowBars");
  const entries = Object.entries(dashboardData.summary.workflow_counts);
  const max = Math.max(...entries.map(([, count]) => count), 1);
  container.innerHTML = entries
    .map(([status, count]) => {
      const width = Math.max(6, Math.round((count / max) * 100));
      return `
        <div class="bar-row">
          <span>${labelize(status)}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
          <strong>${count}</strong>
        </div>
      `;
    })
    .join("");
}

function renderCompactList(id, entries) {
  byId(id).innerHTML = entries
    .map(([label, value]) => `<div class="list-item"><span>${labelize(label)}</span><strong>${value}</strong></div>`)
    .join("");
}

function renderConfigHealth() {
  const validation = dashboardData.config.validation;
  const entries = Object.entries(validation).map(([mode, result]) => [
    mode,
    result.status === "ready" ? "ready" : `${result.missing.length} missing`,
  ]);
  renderCompactList("configHealth", entries);
}

function renderAgents() {
  const nodesById = new Map(dashboardData.topology.nodes.map((node) => [node.id, node]));
  byId("agentGrid").innerHTML = dashboardData.agents
    .map((agent) => {
      const node = nodesById.get(agent.id);
      return `
        <div class="agent-card">
          <strong>${agent.label}</strong>
          <span>${node ? labelize(node.kind) : "catalog only"} | owns ${agent.owns.join(", ")}</span>
        </div>
      `;
    })
    .join("");
}

function renderTrace() {
  const scenario =
    dashboardData.scenarios.find((item) => item.scenario_id === selectedScenarioId) || dashboardData.scenarios[0];
  selectedScenarioId = scenario ? scenario.scenario_id : null;
  byId("selectedScenario").textContent = scenario ? scenario.scenario_id : "None";

  const trace = scenario ? scenario.decision_trace : [];
  byId("traceList").innerHTML = trace.length
    ? trace
        .map((step) => {
          const reasons = step.reasons.length ? step.reasons.join("; ") : "No exception noted";
          return `
            <div class="trace-item ${step.status}">
              <strong>${step.sequence}. ${labelize(step.gate)}: ${labelize(step.decision)}</strong>
              <span>${labelize(step.status)} | ${reasons}</span>
            </div>
          `;
        })
        .join("")
    : `<div class="list-item"><span>No internal trace available for this visibility scope.</span></div>`;
}

function renderIntegrationSurface() {
  byId("openapiFacts").innerHTML = `
    <dt>Title</dt><dd>${dashboardData.openapi.title}</dd>
    <dt>Version</dt><dd>${dashboardData.openapi.version}</dd>
    <dt>Paths</dt><dd>${dashboardData.openapi.path_count}</dd>
  `;
  byId("schemaChips").innerHTML = dashboardData.schemas.map((schema) => `<span class="chip">${schema}</span>`).join("");
  byId("metadataPaths").innerHTML = dashboardData.openapi.metadata_paths
    .map((path) => `<div class="list-item"><span>${path}</span><strong>GET</strong></div>`)
    .join("");
}

function renderAll() {
  renderMetrics(dashboardData);
  renderScenarioRows();
  renderBars();
  renderCompactList("riskList", Object.entries(dashboardData.summary.risk_counts));
  renderConfigHealth();
  renderAgents();
  renderTrace();
  renderIntegrationSurface();
}

async function loadData() {
  const response = await fetch("./data.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to load dashboard data: ${response.status}`);
  }
  dashboardData = await response.json();
  if (!selectedScenarioId && dashboardData.scenarios.length) {
    selectedScenarioId = dashboardData.scenarios[0].scenario_id;
  }
  renderAll();
}

function wireControls() {
  byId("scenarioSearch").addEventListener("input", renderScenarioRows);
  byId("refreshButton").addEventListener("click", loadData);
  for (const tab of document.querySelectorAll(".tab")) {
    tab.addEventListener("click", () => {
      activeStatus = tab.dataset.status;
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      renderScenarioRows();
    });
  }
}

wireControls();
loadData().catch((error) => {
  byId("scenarioRows").innerHTML = `<tr><td colspan="6" class="empty">${error.message}</td></tr>`;
});
