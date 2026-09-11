from app.models.common import AccessCheckRequest
from app.services.security_workflow import SecurityWorkflowService


IDENTITY = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"


def request(action="ADMIN"):
    return AccessCheckRequest(
        org_id="acme-organization",
        did=IDENTITY,
        role="Employee",
        resource_id="acme-admin-console",
        action=action,
    )


def test_adaptive_risk_escalates_and_suspends_identity():
    events = []
    workflow = SecurityWorkflowService(event_sink=events.append)

    first = workflow.authorize(request("READ"), False)
    second = workflow.authorize(request("READ"), False)
    third = workflow.authorize(request("READ"), False)
    workflow.authorize(request("READ"), False)
    fifth = workflow.authorize(request("READ"), False)
    workflow.authorize(request("READ"), False)
    seventh = workflow.authorize(request("READ"), False)

    assert first["severity"] == "Low"
    assert first["adaptive_state"] == "ALLOW"
    assert second["severity"] == "Low"
    assert third["severity"] == "Medium"
    assert third["adaptive_state"] == "STEP-UP"
    assert fifth["severity"] == "High"
    assert fifth["adaptive_state"] == "DENY"
    assert seventh["severity"] == "Critical"
    assert seventh["adaptive_state"] == "DENY + SUSPEND"
    assert seventh["suspended"] is True
    assert len(events) == 7

    suspended = workflow.authorize(request(), True)
    assert suspended["allowed"] is False
    assert suspended["suspended"] is True


def test_simulation_creates_incident_graph_and_copilot_evidence():
    workflow = SecurityWorkflowService(event_sink=lambda event: None)

    result = workflow.simulate_attack(request())

    assert result["synthetic"] is True
    assert len(result["attempts"]) == 7
    assert result["final"]["suspended"] is True

    incidents = workflow.list_incidents()
    assert incidents
    assert incidents[-1]["timeline"]
    assert incidents[-1]["evidence"][0]["synthetic"] is True

    graph = workflow.graph()
    assert graph["count"]["nodes"] > 0
    assert graph["count"]["links"] > 0

    copilot = workflow.copilot()
    assert copilot["provider"] == "deterministic-fallback"
    assert copilot["incident_id"] == incidents[0]["incident_id"]
    assert copilot["recommendation"]


def test_policy_simulation_does_not_mutate_policy():
    workflow = SecurityWorkflowService(event_sink=lambda event: None)
    result = workflow.policy_simulation(request("READ"), "DENY")

    assert result["simulation"] is True
    assert result["policy_mutated"] is False
    assert workflow.list_incidents() == []
