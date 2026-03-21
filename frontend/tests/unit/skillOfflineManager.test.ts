/**
 * Tests unitaires pour le gestionnaire offline par compétence (P0-2.15).
 *
 * Couvre :
 * - Tri LRU des candidats au nettoyage
 * - Sélection de packs pour libérer un quota d'octets cible
 * - Suppression effective des packs sélectionnés
 * - Contrainte WiFi-only pour le prefetch
 * - Stockage d'un pack dans IndexedDB
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { InstalledSkillPack, SkillPackData } from '../../types';

// ── Mocks ────────────────────────────────────────────────

const mockGetInstalledSkillPacks = vi.fn();
const mockGetSkillPackMeta = vi.fn();
const mockSaveSkillPack = vi.fn();
const mockDeleteSkillPack = vi.fn();
const mockTouchSkillPack = vi.fn();
const mockGetSkillPackData = vi.fn();

vi.mock('../../services/db', () => ({
  dbService: {
    getInstalledSkillPacks: (...args: any[]) => mockGetInstalledSkillPacks(...args),
    getSkillPackMeta: (...args: any[]) => mockGetSkillPackMeta(...args),
    saveSkillPack: (...args: any[]) => mockSaveSkillPack(...args),
    deleteSkillPack: (...args: any[]) => mockDeleteSkillPack(...args),
    touchSkillPack: (...args: any[]) => mockTouchSkillPack(...args),
    getSkillPackData: (...args: any[]) => mockGetSkillPackData(...args),
  },
}));

const mockApiGet = vi.fn();

vi.mock('../../services/apiClient', () => ({
  apiClient: {
    get: (...args: any[]) => mockApiGet(...args),
  },
}));

// Import après les mocks
import { skillOfflineManager } from '../../services/skillOfflineManager';

// ── Helpers ──────────────────────────────────────────────

function makePack(overrides: Partial<InstalledSkillPack> = {}): InstalledSkillPack {
  return {
    skillId: `skill-${Math.random().toString(36).slice(2, 8)}`,
    skillName: 'Compétence test',
    subjectName: 'Mathématiques',
    domainName: 'Numération',
    questionsCount: 10,
    lessonsCount: 2,
    sizeBytes: 10_000,
    checksum: 'abc123',
    version: '2025-01-01T00:00:00Z',
    installedAt: Date.now() - 86_400_000,
    lastUsedAt: Date.now() - 86_400_000,
    ...overrides,
  };
}

function makePackData(skillId: string): SkillPackData {
  return {
    skill_id: skillId,
    skill_name: 'Compétence test',
    skill_slug: 'comp-test',
    domain_id: 'dom-1',
    domain_name: 'Numération',
    subject_id: 'sub-1',
    subject_name: 'Mathématiques',
    micro_skills: [],
    questions: [{ id: 'q1', text: 'Question test' }],
    lessons: [{ id: 'l1', title: 'Leçon test' }],
    checksum: 'abc123',
    generated_at: '2025-01-01T00:00:00Z',
  };
}

// ── Setup ────────────────────────────────────────────────

beforeEach(() => {
  vi.clearAllMocks();
});

// ── Tests : LRU cleanup ─────────────────────────────────

describe('getCleanupCandidates', () => {
  it('renvoie les packs les plus anciens en premier (tri LRU)', async () => {
    const oldest = makePack({ skillId: 'oldest', lastUsedAt: 1000 });
    const middle = makePack({ skillId: 'middle', lastUsedAt: 5000 });
    const newest = makePack({ skillId: 'newest', lastUsedAt: 9000 });

    // Ordre d'insertion volontairement mélangé
    mockGetInstalledSkillPacks.mockResolvedValue([newest, oldest, middle]);

    const candidates = await skillOfflineManager.getCleanupCandidates(100_000);

    expect(candidates[0].skillId).toBe('oldest');
    expect(candidates[1].skillId).toBe('middle');
    expect(candidates[2].skillId).toBe('newest');
  });

  it('sélectionne assez de packs pour atteindre le quota cible', async () => {
    const packs = [
      makePack({ skillId: 'p1', lastUsedAt: 1000, sizeBytes: 5_000 }),
      makePack({ skillId: 'p2', lastUsedAt: 2000, sizeBytes: 8_000 }),
      makePack({ skillId: 'p3', lastUsedAt: 3000, sizeBytes: 12_000 }),
      makePack({ skillId: 'p4', lastUsedAt: 4000, sizeBytes: 6_000 }),
    ];

    mockGetInstalledSkillPacks.mockResolvedValue(packs);

    // Besoin de libérer 12 000 octets → p1 (5k) + p2 (8k) = 13k >= 12k
    const candidates = await skillOfflineManager.getCleanupCandidates(12_000);

    expect(candidates).toHaveLength(2);
    expect(candidates[0].skillId).toBe('p1');
    expect(candidates[1].skillId).toBe('p2');
    const totalBytes = candidates.reduce((sum, c) => sum + c.sizeBytes, 0);
    expect(totalBytes).toBeGreaterThanOrEqual(12_000);
  });

  it('renvoie tous les packs si le quota dépasse la taille totale', async () => {
    const packs = [
      makePack({ skillId: 'p1', lastUsedAt: 1000, sizeBytes: 5_000 }),
      makePack({ skillId: 'p2', lastUsedAt: 2000, sizeBytes: 3_000 }),
    ];

    mockGetInstalledSkillPacks.mockResolvedValue(packs);

    const candidates = await skillOfflineManager.getCleanupCandidates(100_000);

    expect(candidates).toHaveLength(2);
  });
});

// ── Tests : confirmCleanup ──────────────────────────────

describe('confirmCleanup', () => {
  it('supprime les packs sélectionnés et renvoie les octets libérés', async () => {
    const p1 = makePack({ skillId: 'skill-a', sizeBytes: 5_000 });
    const p2 = makePack({ skillId: 'skill-b', sizeBytes: 8_000 });

    mockGetSkillPackMeta
      .mockResolvedValueOnce(p1)
      .mockResolvedValueOnce(p2);
    mockDeleteSkillPack.mockResolvedValue(undefined);

    const freed = await skillOfflineManager.confirmCleanup(['skill-a', 'skill-b']);

    expect(mockDeleteSkillPack).toHaveBeenCalledTimes(2);
    expect(mockDeleteSkillPack).toHaveBeenCalledWith('skill-a');
    expect(mockDeleteSkillPack).toHaveBeenCalledWith('skill-b');
    expect(freed).toBe(13_000);
  });

  it('ignore les packs déjà supprimés (meta introuvable)', async () => {
    mockGetSkillPackMeta.mockResolvedValue(undefined);
    mockDeleteSkillPack.mockResolvedValue(undefined);

    const freed = await skillOfflineManager.confirmCleanup(['inexistant']);

    expect(mockDeleteSkillPack).not.toHaveBeenCalled();
    expect(freed).toBe(0);
  });
});

// ── Tests : prefetchNextSkills ──────────────────────────

describe('prefetchNextSkills', () => {
  it('respecte la contrainte WiFi-only et ne télécharge pas sur réseau lent', async () => {
    // Simuler une connexion cellulaire lente
    Object.defineProperty(navigator, 'connection', {
      value: { type: 'cellular', effectiveType: '2g' },
      writable: true,
      configurable: true,
    });

    const result = await skillOfflineManager.prefetchNextSkills(['s1', 's2']);

    expect(result).toBe(0);
    expect(mockApiGet).not.toHaveBeenCalled();
  });

  it('télécharge sur WiFi', async () => {
    Object.defineProperty(navigator, 'connection', {
      value: { type: 'wifi', effectiveType: '4g' },
      writable: true,
      configurable: true,
    });

    // Pas encore installé
    mockGetSkillPackMeta.mockResolvedValue(undefined);
    // Le pack renvoyé par l'API
    mockApiGet.mockResolvedValue(makePackData('skill-new'));
    mockSaveSkillPack.mockResolvedValue(undefined);

    const result = await skillOfflineManager.prefetchNextSkills(['skill-new']);

    expect(result).toBe(1);
    expect(mockSaveSkillPack).toHaveBeenCalledTimes(1);
  });

  it('ne re-télécharge pas un pack déjà installé', async () => {
    Object.defineProperty(navigator, 'connection', {
      value: { type: 'wifi', effectiveType: '4g' },
      writable: true,
      configurable: true,
    });

    // Pack déjà installé
    mockGetSkillPackMeta.mockResolvedValue(makePack({ skillId: 'already-installed' }));

    const result = await skillOfflineManager.prefetchNextSkills(['already-installed']);

    expect(result).toBe(0);
    expect(mockApiGet).not.toHaveBeenCalled();
  });

  it('télécharge quand effectiveType est 4g (même sans type wifi)', async () => {
    Object.defineProperty(navigator, 'connection', {
      value: { type: 'cellular', effectiveType: '4g' },
      writable: true,
      configurable: true,
    });

    mockGetSkillPackMeta.mockResolvedValue(undefined);
    mockApiGet.mockResolvedValue(makePackData('skill-4g'));
    mockSaveSkillPack.mockResolvedValue(undefined);

    const result = await skillOfflineManager.prefetchNextSkills(['skill-4g']);

    expect(result).toBe(1);
  });

  it('respecte maxCount pour limiter les téléchargements', async () => {
    Object.defineProperty(navigator, 'connection', {
      value: { type: 'wifi', effectiveType: '4g' },
      writable: true,
      configurable: true,
    });

    mockGetSkillPackMeta.mockResolvedValue(undefined);
    mockApiGet.mockImplementation((url: string) => {
      const id = url.split('/').pop();
      return Promise.resolve(makePackData(id!));
    });
    mockSaveSkillPack.mockResolvedValue(undefined);

    const result = await skillOfflineManager.prefetchNextSkills(
      ['s1', 's2', 's3', 's4', 's5'],
      2,
    );

    expect(result).toBe(2);
    expect(mockSaveSkillPack).toHaveBeenCalledTimes(2);
  });
});

// ── Tests : downloadSkillPack ───────────────────────────

describe('downloadSkillPack', () => {
  it('télécharge et stocke un pack dans IndexedDB', async () => {
    const packData = makePackData('skill-dl');
    mockApiGet.mockResolvedValue(packData);
    mockSaveSkillPack.mockResolvedValue(undefined);

    const result = await skillOfflineManager.downloadSkillPack('skill-dl');

    // Vérifie que saveSkillPack a été appelé avec les bonnes données
    expect(mockSaveSkillPack).toHaveBeenCalledTimes(1);

    const [savedMeta, savedData] = mockSaveSkillPack.mock.calls[0];
    expect(savedMeta.skillId).toBe('skill-dl');
    expect(savedMeta.questionsCount).toBe(1);
    expect(savedMeta.lessonsCount).toBe(1);
    expect(savedMeta.checksum).toBe('abc123');
    expect(savedMeta.sizeBytes).toBeGreaterThan(0);
    expect(savedData).toEqual(packData);

    // Vérifie le retour
    expect(result.skillId).toBe('skill-dl');
    expect(result.skillName).toBe('Compétence test');
    expect(result.installedAt).toBeGreaterThan(0);
    expect(result.lastUsedAt).toBeGreaterThan(0);
  });

  it('appelle le callback de progression', async () => {
    mockApiGet.mockResolvedValue(makePackData('skill-progress'));
    mockSaveSkillPack.mockResolvedValue(undefined);

    const onProgress = vi.fn();
    await skillOfflineManager.downloadSkillPack('skill-progress', onProgress);

    // Le callback doit être appelé à 10%, 70% et 100%
    expect(onProgress).toHaveBeenCalledWith(10);
    expect(onProgress).toHaveBeenCalledWith(70);
    expect(onProgress).toHaveBeenCalledWith(100);
  });

  it('lève une erreur si le pack est introuvable', async () => {
    mockApiGet.mockResolvedValue(null);

    await expect(
      skillOfflineManager.downloadSkillPack('inexistant'),
    ).rejects.toThrow('Pack not found');
  });
});
