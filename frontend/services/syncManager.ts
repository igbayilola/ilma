
import { dbService } from './db';
import { apiClient } from './apiClient';
import { SyncItem, SyncType } from '../types';
import { telemetry } from './telemetry';

// Priority Map (Lower is higher priority)
export const PRIORITY_MAP: Record<SyncType, number> = {
  'exercise_attempt': 1, // Critical: User progression
  'badge_claim': 2,      // Important: Gamification
  'profile_update': 3,   // Medium
  'analytics': 4,        // Low
  'notification_read': 4 // Low
};

// Exponential Backoff Configuration
const MAX_RETRIES = 5;
const BASE_DELAY = 1000; // 1 second

// Custom event for UI notification when sync items permanently fail
const SYNC_ERROR_EVENT = 'sync-error';

// --- Failed Items Tracking ---
export interface FailedSyncItem {
  id: string;
  type: string;
  error: string;
}

// --- Resolved Conflicts Tracking ---
export interface ResolvedConflict {
  field: string;
  localValue: any;
  serverValue: any;
  kept: any;
}

let failedItems: FailedSyncItem[] = [];
let resolvedConflicts: ResolvedConflict[] = [];

// --- Conflict Resolution Strategy ---
const resolveConflict = (localItem: SyncItem, serverState: any) => {
    if (localItem.type === 'profile_update') {
        const keptXp = Math.max(serverState.xp, localItem.payload.xp);
        if (serverState.xp !== localItem.payload.xp) {
            resolvedConflicts.push({
                field: 'xp',
                localValue: localItem.payload.xp,
                serverValue: serverState.xp,
                kept: keptXp,
            });
        }
        return { ...serverState, ...localItem.payload, xp: keptXp };
    }

    if (localItem.type === 'exercise_attempt') {
        if (serverState.exercises[localItem.payload.exerciseId]) {
            const localScore = localItem.payload.score;
            const serverScore = serverState.exercises[localItem.payload.exerciseId].score;
            const bestScore = Math.max(serverScore, localScore);
            if (localScore !== serverScore) {
                resolvedConflicts.push({
                    field: `exercise.${localItem.payload.exerciseId}.score`,
                    localValue: localScore,
                    serverValue: serverScore,
                    kept: bestScore,
                });
            }
            return { ...serverState, exercises: { ...serverState.exercises, [localItem.payload.exerciseId]: { score: bestScore } } };
        }
    }

    return localItem.payload; // Default: Local overwrite
};

// Sync a single item to the server via real API calls
const syncItemToServer = async (item: SyncItem): Promise<boolean> => {
  try {
    switch (item.type) {
      case 'exercise_attempt':
        await apiClient.post(
          `/sessions/${item.payload.sessionId}/attempt`,
          item.payload
        );
        break;
      case 'profile_update':
        await apiClient.patch('/students/me/profile', item.payload);
        break;
      default:
        // badge_claim, analytics, notification_read, etc.
        await apiClient.post('/offline/sync', { events: [item.payload] });
        break;
    }
    return true;
  } catch (error: any) {
    // Network errors or 5xx should be retried; 4xx are permanent failures
    if (error?.status && error.status >= 400 && error.status < 500) {
      // Client error — log and mark as permanently failed (don't retry)
      telemetry.logError(error, { itemId: item.id, type: item.type }, 'SyncItemToServer');
      throw error;
    }
    return false;
  }
};

export const syncManager = {
  /**
   * Returns a copy of the failed sync items list
   */
  getFailedItems(): FailedSyncItem[] {
    return [...failedItems];
  },

  /**
   * Clears the failed sync items list
   */
  clearFailedItems(): void {
    failedItems = [];
  },

  /**
   * Returns a copy of the resolved conflicts list
   */
  getResolvedConflicts(): ResolvedConflict[] {
    return [...resolvedConflicts];
  },

  /**
   * Clears the resolved conflicts list
   */
  clearResolvedConflicts(): void {
    resolvedConflicts = [];
  },

  /**
   * Adds an item to the local IndexedDB queue
   */
  async enqueue(type: SyncType, payload: any): Promise<void> {
    const item: SyncItem = {
      id: crypto.randomUUID(),
      type,
      payload,
      priority: PRIORITY_MAP[type],
      timestamp: Date.now(),
      retryCount: 0
    };
    await dbService.addToQueue(item);
    telemetry.logEvent('Sync', 'Enqueue Item', type);

    // Register for Background Sync so the SW can flush the queue
    // even if the user closes the tab
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      try {
        const sw = await navigator.serviceWorker.ready;
        await (sw as any).sync.register('sync-progress');
      } catch {
        // Background Sync not supported or permission denied — silent fallback
      }
    }
  },

  /**
   * Processes the queue
   */
  async processQueue(onItemProcessed?: () => void): Promise<void> {
    const queue = await dbService.getQueue();
    
    if (queue.length === 0) return;

    const span = telemetry.startSpan('sync', 'processQueue');
    telemetry.logEvent('Sync', 'Batch Start', undefined, queue.length);

    // Sort: High priority first, then oldest first
    const sortedQueue = queue.sort((a, b) => {
      if (a.priority !== b.priority) return a.priority - b.priority;
      return a.timestamp - b.timestamp;
    });

    let successCount = 0;
    let failureCount = 0;

    for (const item of sortedQueue) {
      // Check Backoff
      const now = Date.now();
      if (item.lastAttempt) {
        const delay = Math.pow(2, item.retryCount) * BASE_DELAY;
        if (now - item.lastAttempt < delay) {
          continue;
        }
      }

      try {
        const success = await syncItemToServer(item);

        if (success) {
          await dbService.removeFromQueue(item.id);
          successCount++;
          if (onItemProcessed) onItemProcessed();
        } else {
          // Handle Failure
          item.retryCount++;
          item.lastAttempt = Date.now();
          failureCount++;
          
          if (item.retryCount > MAX_RETRIES) {
            telemetry.logError(`Sync item ${item.id} max retries reached`, { item }, 'SyncManager');
            failedItems.push({
              id: item.id,
              type: item.type,
              error: `Échec après ${MAX_RETRIES} tentatives`,
            });
            await dbService.removeFromQueue(item.id);
            // Dispatch event so the UI can show a toast
            window.dispatchEvent(new CustomEvent(SYNC_ERROR_EVENT, {
              detail: { failedCount: failedItems.length },
            }));
          } else {
            await dbService.updateQueueItem(item);
          }
          if (onItemProcessed) onItemProcessed();
        }
      } catch (error: any) {
        telemetry.logError(error, { itemId: item.id }, 'SyncManager');
        failureCount++;
      }
    }

    span.end();
    if (successCount > 0 || failureCount > 0) {
        telemetry.logEvent('Sync', 'Batch Finish', `Success: ${successCount}, Fail: ${failureCount}`);
    }
  }
};
