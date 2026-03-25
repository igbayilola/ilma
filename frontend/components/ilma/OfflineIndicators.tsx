import React, { useState, useEffect } from 'react';
import { CloudOff, RefreshCw, CheckCircle2, Cloud, AlertCircle } from 'lucide-react';
import { useAppStore } from '../../store';
import { SyncStatus } from '../../types';
import { syncManager } from '../../services/syncManager';

export const OfflineBanner: React.FC = () => {
  const { isOffline } = useAppStore();

  if (!isOffline) return null;

  return (
    <div className="w-full bg-gray-800 text-white px-4 py-3 flex items-center justify-center shadow-md animate-slide-down relative z-50">
      <CloudOff className="w-5 h-5 mr-3 text-gray-400" />
      <span className="font-medium text-sm md:text-base">
        Mode hors-ligne — votre progression est sauvegardée localement.
      </span>
    </div>
  );
};

export const SyncCounter: React.FC = () => {
  const { pendingSyncItems, syncStatus, isOffline } = useAppStore();
  const count = pendingSyncItems.length;
  const [failedCount, setFailedCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFailedCount(syncManager.getFailedItems().length);
    }, 2000);
    setFailedCount(syncManager.getFailedItems().length);
    return () => clearInterval(interval);
  }, []);

  const onRetryFailed = async () => {
    const failed = syncManager.getFailedItems();
    for (const item of failed) {
      await syncManager.enqueue(item.type as any, {});
    }
    syncManager.clearFailedItems();
    setFailedCount(0);
  };

  if (count === 0 && syncStatus === SyncStatus.SYNCED && failedCount === 0) {
    return (
      <div className="flex items-center text-sitou-green text-sm font-medium" title="Tout est synchronisé">
        <CheckCircle2 className="w-5 h-5" />
      </div>
    );
  }

  if (isOffline) {
      return (
        <div className="flex items-center bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200">
             <CloudOff className="w-4 h-4 text-gray-500 mr-2" />
             <span className="text-xs font-bold text-gray-600">{count} à sync</span>
        </div>
      )
  }

  return (
    <div className="flex items-center gap-1">
      <div className="flex items-center bg-sitou-primary-light px-3 py-1.5 rounded-full border border-amber-200">
        {syncStatus === SyncStatus.SYNCING ? (
          <RefreshCw className="w-4 h-4 text-sitou-primary mr-2 animate-spin" />
        ) : (
          <Cloud className="w-4 h-4 text-sitou-primary mr-2" />
        )}
        <span className="text-xs font-bold text-sitou-primary">
          {syncStatus === SyncStatus.SYNCING ? 'Synchronisation...' : `${count} à envoyer`}
        </span>
      </div>
      {failedCount > 0 && (
        <button
          onClick={onRetryFailed}
          className="ml-2 inline-flex items-center gap-1 text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded-full hover:bg-red-100 transition-colors"
          title="Réessayer la synchronisation"
        >
          <AlertCircle size={12} />
          {failedCount} échoué{failedCount > 1 ? 's' : ''}
        </button>
      )}
    </div>
  );
};