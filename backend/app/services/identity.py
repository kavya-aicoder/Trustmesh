from app.blockchain.adapters.did_registry import DIDRegistryAdapter


class IdentityService:
    def __init__(self, did_registry: DIDRegistryAdapter):
        self.did_registry = did_registry