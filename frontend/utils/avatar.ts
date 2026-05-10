// Local SVG avatar URL helper. Replaces DiceBear (external dep, leaks profile IDs).
// Backend route: GET /api/v1/avatars/{seed}.svg — see backend/app/services/avatar_service.py.

const env = (import.meta as any).env;
const API_BASE = env?.VITE_API_URL || '/api/v1';

export function avatarUrl(seed: string | null | undefined): string {
    const safe = (seed || 'default').slice(0, 24);
    return `${API_BASE}/avatars/${encodeURIComponent(safe)}.svg`;
}
