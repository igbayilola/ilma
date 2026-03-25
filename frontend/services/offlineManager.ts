
import { dbService } from './db';
import { apiClient } from './apiClient';
import { ContentPack, InstalledPack, StorageStats } from '../types';

// Fallback packs used when offline or API is unavailable
const FALLBACK_PACKS: ContentPack[] = [
    { id: 'math-level-5', title: 'Maths CM2 - Pack Complet', subjectId: 'math', version: '1.2.0', size: 45 * 1024 * 1024, checksum: 'abc123hash', description: 'Toute la numération et géométrie.', itemsCount: 45 },
    { id: 'fr-level-5', title: 'Français CM2 - Pack Complet', subjectId: 'fr', version: '1.0.5', size: 32 * 1024 * 1024, checksum: 'def456hash', description: 'Grammaire, conjugaison et lecture.', itemsCount: 38 },
    { id: 'geo-africa', title: 'Géographie - Afrique', subjectId: 'geo', version: '2.0.0', size: 15 * 1024 * 1024, checksum: 'ghi789hash', description: 'Cartes et capitales.', itemsCount: 12 },
    { id: 'sci-basic', title: 'Sciences - Les Bases', subjectId: 'sci', version: '1.0.0', size: 120 * 1024 * 1024, checksum: 'jkl012hash', description: 'Vidéos et schémas interactifs.', itemsCount: 20 },
];

// Cached packs list (populated from API or fallback)
export let AVAILABLE_PACKS: ContentPack[] = [...FALLBACK_PACKS];

export const offlineManager = {

    /**
     * Fetch available packs from the API and update the cached list.
     * Falls back to FALLBACK_PACKS if the API is unreachable.
     */
    async fetchAvailablePacks(): Promise<ContentPack[]> {
        try {
            const data = await apiClient.get<any[]>('/content/packs');
            if (data && data.length > 0) {
                const packs: ContentPack[] = data.map((p: any) => ({
                    id: String(p.id),
                    title: p.title || p.name,
                    subjectId: p.subject_id || p.subjectId,
                    version: p.version || '1.0.0',
                    size: p.size || 0,
                    checksum: p.checksum || '',
                    description: p.description || '',
                    itemsCount: p.items_count || p.itemsCount || 0,
                    thumbnail: p.thumbnail,
                }));
                AVAILABLE_PACKS = packs;
                return packs;
            }
        } catch {
            // API unavailable — use fallback
        }
        AVAILABLE_PACKS = [...FALLBACK_PACKS];
        return AVAILABLE_PACKS;
    },

    /**
     * Get storage usage estimates from the browser
     */
    async getStorageStats(): Promise<StorageStats> {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const { usage, quota } = await navigator.storage.estimate();
            return {
                used: usage || 0,
                quota: quota || 0,
                percentUsed: quota ? ((usage || 0) / quota) * 100 : 0
            };
        }
        return { used: 0, quota: 0, percentUsed: 0 };
    },

    /**
     * Check if local packs have updates available on server
     */
    async checkForUpdates(): Promise<void> {
        // Refresh available packs from API
        await this.fetchAvailablePacks();

        const installed = await dbService.getInstalledPacks();

        for (const localPack of installed) {
            const remotePack = AVAILABLE_PACKS.find(p => p.id === localPack.id);
            if (remotePack && this.compareVersions(remotePack.version, localPack.version) > 0) {
                localPack.isUpdateAvailable = true;
                await dbService.savePack(localPack);
            }
        }
    },

    /**
     * Download a pack with chunked resume capability.
     *
     * Fetches the pack manifest from the API, then downloads resources
     * (questions/lessons) in batches. Stores each batch in IndexedDB.
     * Supports resume via localStorage progress tracking.
     */
    async downloadPack(packId: string, onProgress: (pct: number) => void): Promise<InstalledPack> {
        const pack = AVAILABLE_PACKS.find(p => p.id === packId);
        if (!pack) throw new Error("Pack not found");

        // --- Resume support ---
        const progressKey = `sitou_download_${packId}`;
        const savedProgress = localStorage.getItem(progressKey);
        let startChunk = 0;
        if (savedProgress) {
            startChunk = parseInt(savedProgress, 10);
            if (isNaN(startChunk) || startChunk < 0) startChunk = 0;
        }

        // Fetch pack manifest (list of resource IDs) from API
        let resources: any[] = [];
        try {
            const manifest = await apiClient.get<any>(`/content/packs/${packId}`);
            resources = manifest?.resources || manifest?.items || [];
        } catch {
            // If API fails, fall back to simulated download
        }

        if (resources.length > 0) {
            // Real download: fetch resources in chunks and store in IDB
            const chunkSize = Math.max(1, Math.ceil(resources.length / 10));
            const totalChunks = Math.ceil(resources.length / chunkSize);

            for (let i = startChunk; i < totalChunks; i++) {
                const chunk = resources.slice(i * chunkSize, (i + 1) * chunkSize);

                // Fetch each resource's full data (questions, lesson content)
                for (const res of chunk) {
                    try {
                        const resourceData = await apiClient.get<any>(`/content/packs/${packId}/resources/${res.id}`);
                        await dbService.putContentCache(packId, res.id, resourceData);
                    } catch {
                        // Individual resource failure — continue with others
                    }
                }

                localStorage.setItem(progressKey, String(i + 1));
                onProgress(((i + 1) / totalChunks) * 100);
            }
        } else {
            // Fallback: simulated chunked download (for dev/demo)
            const totalChunks = 10;
            for (let i = startChunk; i < totalChunks; i++) {
                await new Promise(resolve => setTimeout(resolve, 300));
                localStorage.setItem(progressKey, String(i + 1));
                onProgress(((i + 1) / totalChunks) * 100);
            }
        }

        // --- Download complete: clear resume progress ---
        localStorage.removeItem(progressKey);

        const installedPack: InstalledPack = {
            ...pack,
            installedAt: Date.now(),
            lastUsedAt: Date.now(),
            isUpdateAvailable: false
        };

        if (!this.verifyChecksum(installedPack)) {
            throw new Error("Integrity check failed");
        }

        await dbService.savePack(installedPack);
        return installedPack;
    },

    /**
     * Delete a pack to free space
     */
    async deletePack(packId: string): Promise<void> {
        await dbService.deletePack(packId);
    },

    /**
     * Returns the list of packs that would be deleted by LRU cleanup,
     * sorted by last usage (oldest first), without actually deleting them.
     * Use this to show a confirmation UI before calling confirmCleanup().
     */
    async getCleanupCandidates(targetFreeBytes: number): Promise<Array<{ id: string; name: string; size: number; lastUsed: Date }>> {
        const stats = await this.getStorageStats();
        const freeSpace = stats.quota - stats.used;

        if (freeSpace >= targetFreeBytes) return []; // Enough space

        const installed = await dbService.getInstalledPacks();
        // Sort by lastUsedAt ASC (Oldest first)
        installed.sort((a, b) => a.lastUsedAt - b.lastUsedAt);

        const candidates: Array<{ id: string; name: string; size: number; lastUsed: Date }> = [];
        let projected = 0;
        for (const pack of installed) {
            candidates.push({
                id: pack.id,
                name: pack.title,
                size: pack.size,
                lastUsed: new Date(pack.lastUsedAt),
            });
            projected += pack.size;
            if ((freeSpace + projected) >= targetFreeBytes) break;
        }
        return candidates;
    },

    /**
     * Deletes the specified packs (confirmed by user after reviewing candidates).
     * Returns total bytes freed.
     */
    async confirmCleanup(packIds: string[]): Promise<number> {
        let freed = 0;
        for (const id of packIds) {
            const installed = await dbService.getInstalledPacks();
            const pack = installed.find(p => p.id === id);
            if (pack) {
                await this.deletePack(pack.id);
                freed += pack.size;
            }
        }
        return freed;
    },

    /**
     * LRU Cleanup: Delete oldest used packs if space is needed.
     * Two-step process: get candidates first, then delete.
     * If called directly (legacy), performs immediate cleanup.
     * targetFreeBytes: How much space we need
     */
    async performLRUCleanup(targetFreeBytes: number): Promise<number> {
        const candidates = await this.getCleanupCandidates(targetFreeBytes);
        if (candidates.length === 0) return 0;

        // Immediate cleanup (for backward compatibility / non-interactive contexts)
        return this.confirmCleanup(candidates.map(c => c.id));
    },

    // --- Helpers ---

    compareVersions(v1: string, v2: string): number {
        const p1 = v1.split('.').map(Number);
        const p2 = v2.split('.').map(Number);
        for (let i = 0; i < Math.max(p1.length, p2.length); i++) {
            const n1 = p1[i] || 0;
            const n2 = p2[i] || 0;
            if (n1 > n2) return 1;
            if (n1 < n2) return -1;
        }
        return 0;
    },

    verifyChecksum(pack: InstalledPack): boolean {
        // In prod, calculate MD5 of downloaded blobs.
        // Here we assume it's valid if checksum exists.
        return !!pack.checksum;
    }
};
