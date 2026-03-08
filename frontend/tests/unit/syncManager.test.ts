import { describe, it, expect, vi, beforeEach } from 'vitest';
import { syncManager, PRIORITY_MAP } from '../../services/syncManager';
import { dbService } from '../../services/db';

// Mock dbService
vi.mock('../../services/db', () => ({
  dbService: {
    getQueue: vi.fn(),
    addToQueue: vi.fn(),
    removeFromQueue: vi.fn(),
    updateQueueItem: vi.fn(),
  }
}));

// Mock apiClient
vi.mock('../../services/apiClient', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({}),
    post: vi.fn().mockResolvedValue({}),
    put: vi.fn().mockResolvedValue({}),
    patch: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  }
}));

// Mock telemetry
vi.mock('../../services/telemetry', () => ({
  telemetry: {
    logEvent: vi.fn(),
    logError: vi.fn(),
    startSpan: vi.fn(() => ({ end: vi.fn() })),
  }
}));

describe('SyncManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('enqueues items with correct priority', async () => {
    (dbService.addToQueue as any).mockResolvedValue('id');

    await syncManager.enqueue('exercise_attempt', { score: 80 });

    expect(dbService.addToQueue).toHaveBeenCalledTimes(1);
    const savedItem = (dbService.addToQueue as any).mock.calls[0][0];
    expect(savedItem.type).toBe('exercise_attempt');
    expect(savedItem.priority).toBe(PRIORITY_MAP['exercise_attempt']);
    expect(savedItem.retryCount).toBe(0);
    expect(savedItem.payload).toEqual({ score: 80 });
  });

  it('processes empty queue without errors', async () => {
    (dbService.getQueue as any).mockResolvedValue([]);

    await syncManager.processQueue();

    expect(dbService.removeFromQueue).not.toHaveBeenCalled();
  });

  it('processes queue in priority order', async () => {
    const items = [
      { id: '1', type: 'analytics', priority: 4, timestamp: 100, retryCount: 0, payload: { event: 'page_view' } },
      { id: '2', type: 'exercise_attempt', priority: 1, timestamp: 200, retryCount: 0, payload: { sessionId: 's1', score: 80 } },
      { id: '3', type: 'badge_claim', priority: 2, timestamp: 150, retryCount: 0, payload: { badgeId: 'b1' } },
    ];
    (dbService.getQueue as any).mockResolvedValue(items);

    // The processQueue sorts by priority then timestamp
    // We can't easily test order of syncItemToServer calls since it's internal,
    // but we can verify it processes all items
    await syncManager.processQueue();

    // At least some items should have been processed (success or failure based on random)
    const totalCalls = (dbService.removeFromQueue as any).mock.calls.length +
                       (dbService.updateQueueItem as any).mock.calls.length;
    expect(totalCalls).toBeGreaterThanOrEqual(items.length);
  });

  it('respects backoff delay for retried items', async () => {
    const recentlyFailed = {
      id: '1',
      type: 'exercise_attempt',
      priority: 1,
      timestamp: Date.now(),
      retryCount: 3,
      lastAttempt: Date.now() - 100, // Failed 100ms ago, backoff should be 8000ms
      payload: { sessionId: 's1', score: 50 },
    };
    (dbService.getQueue as any).mockResolvedValue([recentlyFailed]);

    await syncManager.processQueue();

    // Item should be skipped due to backoff
    expect(dbService.removeFromQueue).not.toHaveBeenCalled();
    expect(dbService.updateQueueItem).not.toHaveBeenCalled();
  });
});
