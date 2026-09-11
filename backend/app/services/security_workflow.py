from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.indexer.events import BlockchainEvent
from app.indexer.service import indexer_service
from app.models.common import AccessCheckRequest


@dataclass
class IdentityState:
    violations: list[datetime] = field(default_factory=list)
    admin_attempts: int = 0
    suspended: bool = False


class SecurityWorkflowService:
    """Stateful demo projection built on PolicyEngine decisions and indexed events."""

    rapid_window = timedelta(seconds=60)
    medium_threshold = 3
    high_threshold = 5
    critical_threshold = 7

    def __init__(self, event_sink=None) -> None:
        self.event_sink = event_sink or indexer_service.ingest
        self.identities: dict[str, IdentityState] = {}
        self.incidents: list[dict] = []

    def reset(self) -> None:
        self.identities.clear()
        self.incidents.clear()

    def authorize(
        self,
        request: AccessCheckRequest,
        policy_allowed: bool,
        *,
        synthetic: bool = False,
    ) -> dict:
        state = self.identities.setdefault(request.did, IdentityState())
        now = datetime.now(timezone.utc)
        recent = [
            timestamp
            for timestamp in state.violations
            if now - timestamp <= self.rapid_window
        ]
        state.violations = recent

        if state.suspended:
            policy_allowed = False

        if policy_allowed:
            return {
                "identity": request.did,
                "role": request.role,
                "resource": SecurityWorkflowService._resource_label(request.resource_id),
                "action": request.action,
                "decision": "ALLOW",
                "adaptive_state": "ALLOW",
                "allowed": True,
                "suspended": False,
                "violations": len(state.violations),
            }

        state.violations.append(now)
        if request.action.upper() in {"ADMIN", "DELETE", "TRANSFER", "PRIVILEGE_ESCALATION"}:
            state.admin_attempts += 1

        violation_count = len(state.violations)
        severity, risk_score = self._risk_for(
            request.action,
            violation_count,
            state.admin_attempts,
        )
        adaptive_state = self._adaptive_state(severity)
        if severity == "Critical":
            state.suspended = True

        event_id = f"demo-{uuid4()}"
        status = "Suspended" if state.suspended else "Blocked"
        description = (
            f"{request.role} identity attempted {request.action} on "
            f"{request.resource_id}; PolicyEngine denied the request."
        )
        event = BlockchainEvent(
            event_name="AccessDenied",
            contract_address="trustmesh-policy-engine",
            transaction_hash=event_id,
            block_number=0,
            log_index=0,
            timestamp=now,
            data={
                "synthetic": synthetic,
                "attack_type": "Privilege escalation probing" if state.admin_attempts else "Unauthorized access attempt",
                "threat_type": "Rapid repeated administrative failures" if state.admin_attempts >= 2 else "Unauthorized access",
                "subject": request.did,
                "identity": request.did,
                "role": request.role,
                "resource": self._resource_label(request.resource_id),
                "resource_id": request.resource_id,
                "action": request.action,
                "decision": "DENY",
                "severity": severity,
                "risk_score": risk_score,
                "status": status,
                "adaptive_state": adaptive_state,
                "violations": violation_count,
                "reason": "PolicyEngine denied the requested action.",
                "description": description,
                "suspension_state": "Suspended" if state.suspended else "Active",
            },
        )
        self.event_sink(event)
        incident = self._record_incident(event, state, risk_score, severity)

        return {
            "identity": request.did,
            "role": request.role,
            "resource": request.resource_id,
            "action": request.action,
            "decision": "DENY",
            "adaptive_state": adaptive_state,
            "allowed": False,
            "suspended": state.suspended,
            "violations": violation_count,
            "risk_score": risk_score,
            "severity": severity,
            "event_id": event_id,
            "incident_id": incident["incident_id"],
            "status": status,
            "synthetic": synthetic,
        }

    def simulate_attack(self, request: AccessCheckRequest) -> dict:
        attempts = [
            self.authorize(request, False, synthetic=True)
            for _ in range(7)
        ]
        return {
            "mode": "SIMULATION",
            "synthetic": True,
            "attempts": attempts,
            "final": attempts[-1],
        }

    def list_incidents(self) -> list[dict]:
        return list(reversed(self.incidents))

    def graph(self) -> dict:
        nodes: dict[str, dict] = {}
        links: list[dict] = []
        seen_links: set[tuple[str, str, str]] = set()

        def node(node_id: str, label: str, node_type: str, risk: int = 0) -> None:
            current = nodes.setdefault(
                node_id,
                {"id": node_id, "label": label, "type": node_type, "risk": risk},
            )
            current["risk"] = max(current["risk"], risk)

        def link(source: str, target: str, relation: str) -> None:
            key = (source, target, relation)
            if key not in seen_links:
                seen_links.add(key)
                links.append({"source": source, "target": target, "relation": relation})

        for incident in self.incidents:
            identity = incident["identity"]
            role = incident["role"]
            resource = incident["resource"]
            event_id = incident["incident_id"]
            risk = incident["risk_score"]
            identity_node = f"identity:{identity}"
            role_node = f"role:{role}"
            resource_node = f"resource:{resource}"
            event_node = f"event:{event_id}"
            threat_node = f"threat:{event_id}"
            for args in (
                (identity_node, identity, "identity", risk),
                (role_node, role, "role", 0),
                (resource_node, resource, "resource", risk),
                (event_node, "AccessDenied", "event", risk),
                (threat_node, incident["threat_type"], "threat", risk),
            ):
                node(*args)
            link(identity_node, role_node, "assigned")
            link(role_node, resource_node, "requests")
            link(identity_node, event_node, "triggered")
            link(event_node, threat_node, "detected")
            link(threat_node, resource_node, "targets")

        return {
            "service": "trust-risk-graph",
            "status": "ready",
            "count": {"nodes": len(nodes), "links": len(links)},
            "nodes": list(nodes.values()),
            "links": links,
        }

    def copilot(self, incident: dict | None = None) -> dict:
        incident = incident or (self.list_incidents()[0] if self.incidents else None)
        if incident is None:
            return {
                "status": "ready",
                "provider": "deterministic-fallback",
                "analysis": "No TrustMesh security evidence is available yet.",
                "recommendation": "Run a controlled attack simulation to create evidence.",
            }

        return {
            "status": "ready",
            "provider": "deterministic-fallback",
            "incident_id": incident["incident_id"],
            "what_happened": (
                f"{incident['identity']} made repeated denied requests against "
                f"{incident['resource']}."
            ),
            "why_suspicious": incident["threat_type"],
            "evidence": incident["evidence"],
            "risk_explanation": f"Risk is {incident['severity']} at {incident['risk_score']}/100.",
            "recommendation": (
                "Keep the identity suspended and review the indexed audit events."
                if incident["suspended"]
                else "Apply adaptive restriction and review the indexed audit events."
            ),
        }

    @staticmethod
    def policy_simulation(request: AccessCheckRequest, simulated_decision: str) -> dict:
        return {
            "simulation": True,
            "policy_mutated": False,
            "identity": request.did,
            "role": request.role,
            "resource": request.resource_id,
            "action": request.action,
            "current_decision": "ALLOW",
            "simulated_decision": simulated_decision.upper(),
        }

    def _record_incident(
        self,
        event: BlockchainEvent,
        state: IdentityState,
        risk_score: int,
        severity: str,
    ) -> dict:
        incident = {
            "incident_id": f"INC-{uuid4().hex[:10].upper()}",
            "identity": event.data["identity"],
            "role": event.data["role"],
            "attack_type": event.data["attack_type"],
            "threat_type": event.data["threat_type"],
            "resource": event.data["resource"],
            "action": event.data["action"],
            "violations": event.data["violations"],
            "risk_score": risk_score,
            "severity": severity,
            "decision": event.data["decision"],
            "suspended": state.suspended,
            "created_at": event.timestamp.isoformat() if event.timestamp else None,
            "evidence": [
                {
                    "event_id": f"{event.transaction_hash}:{event.log_index}",
                    "event": event.event_name,
                    "reason": event.data["reason"],
                    "synthetic": event.data["synthetic"],
                }
            ],
            "timeline": [
                {"stage": "ATTACK", "timestamp": event.timestamp.isoformat()},
                {"stage": "POLICY_DENIAL", "timestamp": event.timestamp.isoformat()},
                {"stage": "AUDIT_EVENT", "timestamp": event.timestamp.isoformat()},
                {"stage": "THREAT_DETECTION", "timestamp": event.timestamp.isoformat()},
                {"stage": "RISK_ESCALATION", "timestamp": event.timestamp.isoformat()},
                {"stage": "SUSPENSION" if state.suspended else "ADAPTIVE_RESTRICTION", "timestamp": event.timestamp.isoformat()},
            ],
        }
        self.incidents.append(incident)
        return incident

    @staticmethod
    def _risk_for(action: str, violations: int, admin_attempts: int) -> tuple[str, int]:
        critical_action = action.upper() in {"PRIVILEGE_ESCALATION", "TRANSFER"}
        if violations >= 7 or (critical_action and admin_attempts >= 2):
            return "Critical", 95
        if violations >= 5 or admin_attempts >= 3:
            return "High", 85
        if violations >= 3:
            return "Medium", 55
        return "Low", 25

    @staticmethod
    def _adaptive_state(severity: str) -> str:
        return {
            "Low": "ALLOW",
            "Medium": "STEP-UP",
            "High": "DENY",
            "Critical": "DENY + SUSPEND",
        }[severity]

    @staticmethod
    def _resource_label(resource_id: str) -> str:
        return {
            "acme-employee-records": "Employee Records",
            "acme-admin-console": "Admin Console",
            "acme-documents": "Documents",
            "acme-digital-assets": "Digital Assets",
        }.get(resource_id, resource_id)


security_workflow = SecurityWorkflowService()
