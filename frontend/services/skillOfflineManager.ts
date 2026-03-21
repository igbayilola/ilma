/**
 * Per-skill offline content manager.
 *
 * Downloads individual skill packs (questions + lessons JSON) from the API
 * and stores them in IndexedDB. Supports delta sync, WiFi-aware prefetch,
 * and LRU cleanup.
 */
import { dbService } from './db';
import { apiClient } from './apiClient';
import { SkillPack, SkillPackData, InstalledSkillPack, StorageStats } from '../types';

export const skillOfflineManager = {

  /**
   * Fetch the list of available per-skill packs from the API.
   */
  async fetchAvailableSkillPacks(gradeLevelId?: string): Promise<SkillPack[]> {
    const params = gradeLevelId ? `?grade_level_id=${gradeLevelId}` : '';
    const data = await apiClient.get<SkillPack[]>(`/offline/packs/skills${params}`);
    return data || [];
  },

  /**
   * Download and store a single skill pack.
   */
  async downloadSkillPack(
    skillId: string,
    onProgress?: (pct: number) => void,
  ): Promise<InstalledSkillPack> {
    onProgress?.(10);

    // Fetch full pack data from API
    const packData = await apiClient.get<SkillPackData>(`/offline/packs/skills/${skillId}`);
    if (!packData) throw new Error('Pack not found');

    onProgress?.(70);

    const sizeBytes = JSON.stringify(packData).length; // approximate

    const meta: InstalledSkillPack = {
      skillId: packData.skill_id,
      skillName: packData.skill_name,
      subjectName: packData.subject_name || '',
      domainName: packData.domain_name || '',
      questionsCount: packData.questions.length,
      lessonsCount: packData.lessons.length,
      sizeBytes,
      checksum: packData.checksum,
      version: packData.generated_at,
      installedAt: Date.now(),
      lastUsedAt: Date.now(),
    };

    await dbService.saveSkillPack(meta, packData);
    onProgress?.(100);

    return meta;
  },

  /**
   * Get a skill pack's data from local storage (for offline use).
   */
  async getLocalSkillPack(skillId: string): Promise<SkillPackData | undefined> {
    const data = await dbService.getSkillPackData(skillId);
    if (data) {
      await dbService.touchSkillPack(skillId);
    }
    return data;
  },

  /**
   * Check if a skill pack is available locally.
   */
  async isSkillAvailableOffline(skillId: string): Promise<boolean> {
    const meta = await dbService.getSkillPackMeta(skillId);
    return !!meta;
  },

  /**
   * Get all installed skill packs.
   */
  async getInstalledSkillPacks(): Promise<InstalledSkillPack[]> {
    return dbService.getInstalledSkillPacks();
  },

  /**
   * Delete a skill pack to free space.
   */
  async deleteSkillPack(skillId: string): Promise<void> {
    await dbService.deleteSkillPack(skillId);
  },

  /**
   * Delta sync: check which installed packs have updates.
   */
  async checkForUpdates(): Promise<string[]> {
    const installed = await dbService.getInstalledSkillPacks();
    if (installed.length === 0) return [];

    // Find the oldest version timestamp
    const oldest = installed.reduce(
      (min, p) => (p.version < min ? p.version : min),
      installed[0].version,
    );

    try {
      const changes = await apiClient.get<Array<{ skill_id: string }>>(`/offline/packs/delta?since=${encodeURIComponent(oldest)}`);
      const changedIds = new Set((changes || []).map(c => c.skill_id));
      return installed
        .filter(p => changedIds.has(p.skillId))
        .map(p => p.skillId);
    } catch {
      return [];
    }
  },

  /**
   * Prefetch the next N skills in the student's learning path.
   * Only downloads if on WiFi (uses Network Information API).
   */
  async prefetchNextSkills(skillIds: string[], maxCount = 3): Promise<number> {
    // Check connection type (WiFi-only prefetch)
    const conn = (navigator as any).connection;
    if (conn && conn.type !== 'wifi' && conn.effectiveType !== '4g') {
      return 0;
    }

    let downloaded = 0;
    for (const skillId of skillIds.slice(0, maxCount)) {
      const existing = await dbService.getSkillPackMeta(skillId);
      if (existing) continue;

      try {
        await this.downloadSkillPack(skillId);
        downloaded++;
      } catch {
        break; // Stop on first failure (likely network issue)
      }
    }
    return downloaded;
  },

  /**
   * Get storage stats for skill packs.
   */
  async getSkillPackStats(): Promise<{ totalPacks: number; totalSizeBytes: number }> {
    const packs = await dbService.getInstalledSkillPacks();
    return {
      totalPacks: packs.length,
      totalSizeBytes: packs.reduce((sum, p) => sum + p.sizeBytes, 0),
    };
  },

  /**
   * LRU cleanup: remove oldest-used skill packs to free space.
   */
  async getCleanupCandidates(targetFreeBytes: number): Promise<InstalledSkillPack[]> {
    const packs = await dbService.getInstalledSkillPacks();
    packs.sort((a, b) => a.lastUsedAt - b.lastUsedAt);

    const candidates: InstalledSkillPack[] = [];
    let projected = 0;
    for (const pack of packs) {
      candidates.push(pack);
      projected += pack.sizeBytes;
      if (projected >= targetFreeBytes) break;
    }
    return candidates;
  },

  async confirmCleanup(skillIds: string[]): Promise<number> {
    let freed = 0;
    for (const id of skillIds) {
      const meta = await dbService.getSkillPackMeta(id);
      if (meta) {
        await dbService.deleteSkillPack(id);
        freed += meta.sizeBytes;
      }
    }
    return freed;
  },
};
