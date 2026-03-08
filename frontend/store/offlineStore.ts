
import { create } from 'zustand';
import { InstalledPack, StorageStats } from '../types';
import { offlineManager } from '../services/offlineManager';
import { dbService } from '../services/db';

interface OfflineState {
  installedPacks: InstalledPack[];
  storageStats: StorageStats | null;
  downloadingId: string | null;
  downloadProgress: number;
  isLoading: boolean;

  // Actions
  refreshData: () => Promise<void>;
  installPack: (packId: string) => Promise<void>;
  removePack: (packId: string) => Promise<void>;
  updatePack: (packId: string) => Promise<void>;
}

export const useOfflineStore = create<OfflineState>((set, get) => ({
  installedPacks: [],
  storageStats: null,
  downloadingId: null,
  downloadProgress: 0,
  isLoading: false,

  refreshData: async () => {
    set({ isLoading: true });
    try {
        await offlineManager.checkForUpdates();
        const packs = await dbService.getInstalledPacks();
        const stats = await offlineManager.getStorageStats();
        set({ installedPacks: packs, storageStats: stats, isLoading: false });
    } catch (e) {
        console.error("Failed to load offline data", e);
        set({ isLoading: false });
    }
  },

  installPack: async (packId: string) => {
      set({ downloadingId: packId, downloadProgress: 0 });
      try {
          // Check quota first (simplistic check)
          // In real app: check pack.size vs stats.free
          
          await offlineManager.downloadPack(packId, (pct) => {
              set({ downloadProgress: pct });
          });
          
          await get().refreshData();
      } catch (e) {
          console.error(e);
          alert("Erreur lors du téléchargement");
      } finally {
          set({ downloadingId: null, downloadProgress: 0 });
      }
  },

  removePack: async (packId: string) => {
      await offlineManager.deletePack(packId);
      await get().refreshData();
  },

  updatePack: async (packId: string) => {
      // Logic same as install for this demo (overwrite)
      await get().installPack(packId);
  }
}));
