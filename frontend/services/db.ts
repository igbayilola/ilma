
import { openDB, DBSchema, IDBPDatabase } from 'idb';
import { SyncItem, InstalledPack } from '../types';

interface IlmaDB extends DBSchema {
  syncQueue: {
    key: string;
    value: SyncItem;
    indexes: { 'by-priority': number };
  };
  userData: {
    key: string;
    value: any;
  };
  contentCache: {
    key: string;
    value: any;
  };
  contentPacks: {
    key: string;
    value: InstalledPack;
    indexes: { 'by-lastUsed': number };
  };
}

const DB_NAME = 'ilma-db';
const DB_VERSION = 2; // Bumped version

export const initDB = async (): Promise<IDBPDatabase<IlmaDB>> => {
  return openDB<IlmaDB>(DB_NAME, DB_VERSION, {
    upgrade(db, oldVersion, newVersion, transaction) {
      // v1 Stores
      if (oldVersion < 1) {
        if (!db.objectStoreNames.contains('syncQueue')) {
          const store = db.createObjectStore('syncQueue', { keyPath: 'id' });
          store.createIndex('by-priority', 'priority');
        }
        if (!db.objectStoreNames.contains('userData')) {
          db.createObjectStore('userData', { keyPath: 'key' });
        }
        if (!db.objectStoreNames.contains('contentCache')) {
          db.createObjectStore('contentCache', { keyPath: 'id' });
        }
      }

      // v2 Migration: Content Packs for Offline Management
      if (oldVersion < 2) {
        if (!db.objectStoreNames.contains('contentPacks')) {
           const store = db.createObjectStore('contentPacks', { keyPath: 'id' });
           store.createIndex('by-lastUsed', 'lastUsedAt');
        }
      }
    },
  });
};

export const dbService = {
  async getQueue(): Promise<SyncItem[]> {
    const db = await initDB();
    return db.getAll('syncQueue');
  },

  async addToQueue(item: SyncItem): Promise<string> {
    const db = await initDB();
    await db.put('syncQueue', item);
    return item.id;
  },

  async removeFromQueue(id: string): Promise<void> {
    const db = await initDB();
    await db.delete('syncQueue', id);
  },

  async updateQueueItem(item: SyncItem): Promise<void> {
    const db = await initDB();
    await db.put('syncQueue', item);
  },

  async saveUserData(key: string, data: any): Promise<void> {
    const db = await initDB();
    await db.put('userData', { key, value: data });
  },

  async getUserData(key: string): Promise<any | undefined> {
    const db = await initDB();
    const result = await db.get('userData', key);
    return result?.value;
  },

  // --- Content Pack Methods ---
  
  async getInstalledPacks(): Promise<InstalledPack[]> {
    const db = await initDB();
    return db.getAll('contentPacks');
  },

  async savePack(pack: InstalledPack): Promise<void> {
    const db = await initDB();
    await db.put('contentPacks', pack);
  },

  async deletePack(id: string): Promise<void> {
    const db = await initDB();
    await db.delete('contentPacks', id);
    // In a real app, this would also delete the associated contentCache items
  },

  async touchPack(id: string): Promise<void> {
    const db = await initDB();
    const pack = await db.get('contentPacks', id);
    if (pack) {
        pack.lastUsedAt = Date.now();
        await db.put('contentPacks', pack);
    }
  },

  async putContentCache(packId: string, resourceId: string, data: any): Promise<void> {
    const db = await initDB();
    await db.put('contentCache', { id: `${packId}:${resourceId}`, packId, resourceId, ...data });
  },

  async getContentCache(packId: string, resourceId: string): Promise<any | undefined> {
    const db = await initDB();
    return db.get('contentCache', `${packId}:${resourceId}`);
  },
};
