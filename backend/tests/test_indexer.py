from app.indexer.events import BlockchainEvent
from app.indexer.repository import EventRepository
from app.indexer.service import IndexerService


def test_event_repository_stores_event():
    repository = EventRepository()

    event = BlockchainEvent(
        event_name="TestEvent",
        contract_address="0x123",
        transaction_hash="0xabc",
        block_number=100,
        log_index=0,
        timestamp=None,
        data={"value": "test"},
    )

    repository.add(event)

    assert repository.list_events() == [event]


def test_indexer_ingests_event():
    repository = EventRepository()
    service = IndexerService(repository)

    event = BlockchainEvent(
        event_name="AccessGranted",
        contract_address="0x123",
        transaction_hash="0xabc",
        block_number=101,
        log_index=1,
        timestamp=None,
        data={"did": "did:example:alice"},
    )

    result = service.ingest(event)

    assert result == event
    assert service.get_events() == [event]


def test_repository_clear():
    repository = EventRepository()

    event = BlockchainEvent(
        event_name="TestEvent",
        contract_address="0x123",
        transaction_hash="0xabc",
        block_number=100,
        log_index=0,
        timestamp=None,
        data={},
    )

    repository.add(event)
    repository.clear()

    assert repository.list_events() == []