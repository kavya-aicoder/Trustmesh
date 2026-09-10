from app.indexer.events import BlockchainEvent
from app.services.security_agent import security_agent


def make_event(
    event_name: str,
    data: dict | None = None,
) -> BlockchainEvent:
    return BlockchainEvent(
        event_name=event_name,
        contract_address="0x123",
        transaction_hash="0xabc",
        block_number=100,
        log_index=0,
        timestamp=None,
        data=data or {},
    )


def test_allows_normal_event():
    result = security_agent.analyze(
        make_event("AccessGranted")
    )

    assert result.threat_detected is False
    assert result.risk_score == 0
    assert result.severity == "Low"


def test_detects_rejected_access():
    result = security_agent.analyze(
        make_event("AccessDenied")
    )

    assert result.threat_detected is True
    assert result.risk_score == 60
    assert result.severity == "High"
    assert "rejected" in result.reason.lower()


def test_detects_high_risk_event():
    result = security_agent.analyze(
        make_event(
            "AccessDenied",
            {"risk": "high"},
        )
    )

    assert result.threat_detected is True
    assert result.risk_score == 90
    assert result.severity == "Critical"


def test_detects_critical_risk_event():
    result = security_agent.analyze(
        make_event(
            "AccessGranted",
            {"risk": "critical"},
        )
    )

    assert result.threat_detected is False
    assert result.risk_score == 50
    assert result.severity == "Medium"


def test_risk_score_is_capped_at_100():
    result = security_agent.analyze(
        make_event(
            "UnauthorizedAccessRevoked",
            {"risk": "critical"},
        )
    )

    assert result.risk_score == 100
    assert result.severity == "Critical"
