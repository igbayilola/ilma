"""Local SVG avatar generator. Replaces DiceBear (external dep, leaks profile IDs)."""
from __future__ import annotations

import hashlib

# Palettes inspired by Béninois flag and traditional textiles. Every seed maps to one
# combination; output stays under ~1KB and is deterministic, so caches are safe.
_BG_PALETTE = [
    "#FFCD42", "#F4A261", "#E76F51", "#2A9D8F", "#264653",
    "#E63946", "#457B9D", "#1D3557", "#06A77D", "#D62828",
]
_SKIN_PALETTE = [
    "#8D5524", "#C68642", "#E0AC69", "#A47148", "#6F4E37",
]
_HAIR_PALETTE = [
    "#1A1A1A", "#2C2C2C", "#3D2B1F", "#000000",
]


def _pick(palette: list[str], offset: int, byte: int) -> str:
    return palette[byte % len(palette)]


def generate_svg(seed: str, size: int = 128) -> str:
    """Return a deterministic SVG string for the given seed.

    The seed is hashed; bytes drive palette selection and minor face geometry.
    Output is intentionally minimal — no animations, no external refs.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    bg = _pick(_BG_PALETTE, 0, digest[0])
    skin = _pick(_SKIN_PALETTE, 1, digest[1])
    hair = _pick(_HAIR_PALETTE, 2, digest[2])

    # Eye spacing and mouth curvature varied slightly per seed
    eye_dx = 22 + (digest[3] % 6)
    mouth_curve = 6 + (digest[4] % 6)
    has_smile = digest[5] % 2 == 0

    cx = size // 2
    cy = size // 2

    mouth_path = (
        f"M {cx - 12} {cy + 18} Q {cx} {cy + 18 + mouth_curve} {cx + 12} {cy + 18}"
        if has_smile
        else f"M {cx - 12} {cy + 22} L {cx + 12} {cy + 22}"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="avatar">'
        f'<rect width="{size}" height="{size}" rx="{size // 2}" fill="{bg}"/>'
        # Hair (top half-circle)
        f'<path d="M {cx - 38} {cy - 4} Q {cx} {cy - 60} {cx + 38} {cy - 4} Z" fill="{hair}"/>'
        # Face
        f'<circle cx="{cx}" cy="{cy + 4}" r="32" fill="{skin}"/>'
        # Eyes
        f'<circle cx="{cx - eye_dx // 2}" cy="{cy - 2}" r="3" fill="#1A1A1A"/>'
        f'<circle cx="{cx + eye_dx // 2}" cy="{cy - 2}" r="3" fill="#1A1A1A"/>'
        # Mouth
        f'<path d="{mouth_path}" stroke="#1A1A1A" stroke-width="2" fill="none" stroke-linecap="round"/>'
        f"</svg>"
    )


def avatar_path(seed: str) -> str:
    """Canonical relative path used by the API and the frontend helper."""
    safe = seed[:24] if seed else "default"
    return f"/api/v1/avatars/{safe}.svg"
