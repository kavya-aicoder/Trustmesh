
from fastapi import APIRouter

from app.indexer.events import BlockchainEvent
from app.services.security import security_service
from app.services.security_agent import security_agent
from app.services.security_repository import security_finding_repository
from app.indexer.service import indexer_service

router = APIRouter()


def serialize_event(event) -> dict:
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "severity": event.severity,
        "subject": event.subject,
        "resource": event.resource,
        "status": event.status,
        "description": event.description,
    }


@router.get("/")
async def get_security_center() -> dict:
    events = security_service.list_events()

    return {
        "service": "security",
        "status": "ready",
        "summary": security_service.get_summary(),
        "events": [
            serialize_event(event)
            for event in events
        ],
    }


@router.get("/events")
async def list_security_events() -> dict:
    events = security_service.list_events()

    return {
        "service": "security",
        "status": "ready",
        "count": len(events),
        "events": [
            serialize_event(event)
            for event in events
        ],
    }


@router.post("/analyze")
async def analyze_security_event(event: BlockchainEvent) -> dict:
    analysis = security_agent.analyze(event)

    return {
        "service": "security-agent",
        "status": "analyzed",
        "event": {
            "event_name": event.event_name,
            "contract_address": event.contract_address,
            "transaction_hash": event.transaction_hash,
            "block_number": event.block_number,
            "log_index": event.log_index,
            "timestamp": event.timestamp,
            "data": event.data,
        },
        "analysis": {
            "threat_detected": analysis.threat_detected,
            "risk_score": analysis.risk_score,
            "severity": analysis.severity,
            "reason": analysis.reason,
            "recommendation": analysis.recommendation,
        },
    }

@router.get("/findings")
async def list_security_findings() -> dict:
    findings = security_finding_repository.list_findings()

    return {
        "service": "security-agent",
        "status": "ready",
        "count": len(findings),
        "findings": [
            {
                "event_id": finding.event_id,
                "event_name": finding.event_name,
                "threat_detected": finding.threat_detected,
                "risk_score": finding.risk_score,
                "severity": finding.severity,
                "reason": finding.reason,
                "recommendation": finding.recommendation,
            }
            for finding in findings
        ],
    }

@router.post("/events/ingest")
async def ingest_security_event(event: BlockchainEvent) -> dict:
    stored_event = indexer_service.ingest(event)
    analysis = security_agent.analyze(stored_event)

    return {
        "service": "security-agent",
        "status": "ingested",
        "event": {
            "event_name": stored_event.event_name,
            "contract_address": stored_event.contract_address,
            "transaction_hash": stored_event.transaction_hash,
            "block_number": stored_event.block_number,
            "log_index": stored_event.log_index,
            "timestamp": stored_event.timestamp,
            "data": stored_event.data,
        },
        "analysis": {
            "threat_detected": analysis.threat_detected,
            "risk_score": analysis.risk_score,
            "severity": analysis.severity,
            "reason": analysis.reason,
            "recommendation": analysis.recommendation,
        },
    }