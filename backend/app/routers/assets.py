from fastapi import APIRouter, HTTPException

from app.blockchain.adapters.asset_nft import AssetNFTAdapter
from app.blockchain.client import blockchain_client
from app.services.assets import AssetService


router = APIRouter()

asset_service = AssetService(
    AssetNFTAdapter(blockchain_client)
)


_ASSETS = [
    {
        "asset_id": "asset-001",
        "name": "Executive Access Pass",
        "asset_type": "Access Credential",
        "owner": "did:trust:alice",
        "status": "Active",
        "access_level": "Administrator",
        "policy": "Executive Access",
    },
    {
        "asset_id": "asset-002",
        "name": "Security Operations Record",
        "asset_type": "Digital Record",
        "owner": "did:trust:security",
        "status": "Protected",
        "access_level": "Security Analyst",
        "policy": "Security Operations",
    },
    {
        "asset_id": "asset-003",
        "name": "Research Dataset",
        "asset_type": "Dataset",
        "owner": "did:trust:research",
        "status": "Protected",
        "access_level": "Developer",
        "policy": "Research Access",
    },
    {
        "asset_id": "asset-004",
        "name": "Treasury Certificate",
        "asset_type": "Digital Certificate",
        "owner": "did:trust:finance",
        "status": "Active",
        "access_level": "Finance Admin",
        "policy": "Treasury Control",
    },
]


@router.get("/")
async def list_assets() -> dict:
    """Return the existing application asset catalogue."""
    return {
        "service": "assets",
        "status": "ready",
        "count": len(_ASSETS),
        "assets": _ASSETS,
    }


@router.get("/on-chain/{token_id}")
async def get_on_chain_asset(token_id: int) -> dict:
    """Retrieve an AssetNFT record from the blockchain."""
    if token_id < 0:
        raise HTTPException(
            status_code=400,
            detail="token_id must be non-negative",
        )

    try:
        asset = await asset_service.get_asset(token_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return {
        "service": "assets",
        "status": "ready",
        "source": "blockchain",
        "token_id": token_id,
        "asset": asset,
    }


@router.get("/{asset_id}")
async def get_asset(asset_id: str) -> dict:
    """Return an application-level asset from the existing catalogue."""
    asset = next(
        (
            item
            for item in _ASSETS
            if item["asset_id"] == asset_id
        ),
        None,
    )

    if asset is None:
        return {
            "service": "assets",
            "status": "not_found",
            "asset": None,
        }

    return {
        "service": "assets",
        "status": "ready",
        "asset": asset,
    }
