"""Local SVG avatar endpoint. Replaces external DiceBear calls."""
from fastapi import APIRouter, Response

from app.services.avatar_service import generate_svg

router = APIRouter(prefix="/avatars", tags=["Avatars"])


@router.get("/{seed}.svg")
async def get_avatar(seed: str):
    svg = generate_svg(seed)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "X-Content-Type-Options": "nosniff",
        },
    )
