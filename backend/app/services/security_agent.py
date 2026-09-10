from dataclasses import dataclass

from app.indexer.events import BlockchainEvent


@dataclass(frozen=True)
class SecurityAnalysis:
    threat_detected: bool
    risk_score: int
    severity: str
    reason: str
    recommendation: str


class SecurityAgent:
    """Analyzes normalized blockchain events for security threats."""

    def analyze(self, event: BlockchainEvent) -> SecurityAnalysis:
        event_name = event.event_name.lower()
        data = event.data

        risk_score = 0
        reasons: list[str] = []
        recommendation = "No immediate action required."

        if any(
            keyword in event_name
            for keyword in (
                "denied",
                "rejected",
                "violation",
                "unauthorized",
                "failed",
            )
        ):
            risk_score += 60
            reasons.append("The event indicates a rejected or unauthorized operation.")
            recommendation = "Review the access request and verify the subject's permissions."

        if any(
            keyword in event_name
            for keyword in (
                "revoked",
                "suspended",
                "compromised",
            )
        ):
            risk_score += 30
            reasons.append("The event indicates a security-sensitive identity or access change.")
            recommendation = "Verify the change and review related activity."

        if data.get("risk") == "high":
            risk_score += 30
            reasons.append("The event contains a high-risk indicator.")

        if data.get("risk") == "critical":
            risk_score += 50
            reasons.append("The event contains a critical-risk indicator.")

        risk_score = min(risk_score, 100)

        if risk_score >= 80:
            severity = "Critical"
        elif risk_score >= 60:
            severity = "High"
        elif risk_score >= 30:
            severity = "Medium"
        else:
            severity = "Low"

        if not reasons:
            reasons.append("No known high-risk security indicators were detected.")

        return SecurityAnalysis(
            threat_detected=risk_score >= 60,
            risk_score=risk_score,
            severity=severity,
            reason=" ".join(reasons),
            recommendation=recommendation,
        )


security_agent = SecurityAgent()
