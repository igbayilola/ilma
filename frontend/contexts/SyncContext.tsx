import React, { createContext, useContext, useEffect, useCallback } from 'react';
import { useAppStore } from '../store';
import { dbService } from '../services/db.ts';
import { syncManager } from '../services/syncManager.ts';
import { SyncStatus, SyncType } from '../types';
import { useToast } from '../components/ui/Toast';

interface SyncContextType {
  isOffline: boolean;
  syncStatus: SyncStatus;
  triggerSync: () => Promise<void>;
  enqueueAction: (type: SyncType, payload: any) => Promise<void>;
}

const SyncContext = createContext<SyncContextType | null>(null);

export const useSync = () => {
  const context = useContext(SyncContext);
  if (!context) throw new Error('useSync must be used within a SyncProvider');
  return context;
};

// Custom Hooks for specific needs
export const useOffline = () => {
    const { isOffline } = useSync();
    return isOffline;
};

export const useSyncStatus = () => {
    const { syncStatus } = useSync();
    return syncStatus;
};

export const useSyncQueue = () => {
    // We delegate queue state reading to the Zustand store for reactivity
    const { pendingSyncItems } = useAppStore();
    return pendingSyncItems;
};

export const SyncProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const {
      isOffline, setOffline,
      syncStatus, setSyncStatus,
      setPendingSyncItems
  } = useAppStore();
  const { addToast } = useToast();

  // Helper to refresh Zustand from IDB
  const refreshQueueState = useCallback(async () => {
    const items = await dbService.getQueue();
    setPendingSyncItems(items);
  }, [setPendingSyncItems]);

  // Main Sync Function
  const triggerSync = useCallback(async () => {
    if (isOffline) return;

    setSyncStatus(SyncStatus.SYNCING);
    await refreshQueueState(); // Ensure we have latest

    try {
        await syncManager.processQueue(async () => {
            // Callback after each item processed
            await refreshQueueState();
        });
        
        // Final check
        const remaining = await dbService.getQueue();
        if (remaining.length === 0) {
            setSyncStatus(SyncStatus.SYNCED);
        } else {
            // If items remain, they are likely in backoff or failed
            setSyncStatus(SyncStatus.PENDING);
        }
    } catch (e) {
        console.error("Sync Trigger Failed", e);
        setSyncStatus(SyncStatus.ERROR);
    }
  }, [isOffline, setSyncStatus, refreshQueueState]);

  // Public method to add items
  const enqueueAction = useCallback(async (type: SyncType, payload: any) => {
    await syncManager.enqueue(type, payload);
    await refreshQueueState();
    setSyncStatus(SyncStatus.PENDING);
    
    // Opportunistic sync: if online, try sending immediately
    if (!isOffline) {
        // Debounce slightly to allow UI updates
        setTimeout(() => triggerSync(), 500);
    }
  }, [isOffline, refreshQueueState, setSyncStatus, triggerSync]);

  // Network Listeners
  useEffect(() => {
    const handleOnline = () => {
        console.log("[Sync] App is Online");
        setOffline(false);
        triggerSync();
    };
    const handleOffline = () => {
        console.log("[Sync] App is Offline");
        setOffline(true);
        setSyncStatus(SyncStatus.OFFLINE);
    };

    const handleSyncError = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const count = detail?.failedCount || 1;
      addToast({
        type: 'warning',
        title: 'Synchronisation échouée',
        message: `${count} exercice(s) n'ont pas pu être envoyés. Réessaye quand tu auras du réseau.`,
        duration: 8000,
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('sync-error', handleSyncError);

    // Initial check
    if (!navigator.onLine) handleOffline();
    else handleOnline();

    // Load initial queue state
    refreshQueueState();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('sync-error', handleSyncError);
    };
  }, [setOffline, setSyncStatus, triggerSync, refreshQueueState, addToast]);

  // Periodic Sync (Every 60s if online)
  useEffect(() => {
      const interval = setInterval(() => {
          if (!isOffline && syncStatus !== SyncStatus.SYNCING) {
              triggerSync();
          }
      }, 60000);
      return () => clearInterval(interval);
  }, [isOffline, syncStatus, triggerSync]);

  return (
    <SyncContext.Provider value={{ isOffline, syncStatus, triggerSync, enqueueAction }}>
      {children}
    </SyncContext.Provider>
  );
};