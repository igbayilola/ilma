import React from 'react';
import { useSync, useSyncQueue } from '../contexts/SyncContext';
import { Button } from '../components/ui/Button';
import { Card, Badge } from '../components/ui/Cards';
import { RefreshCw, Database, Plus, Trash2 } from 'lucide-react';
import { dbService } from '../services/db';
import { ButtonVariant } from '../types';

export const DebugSyncPage: React.FC = () => {
  const { triggerSync, enqueueAction, isOffline, syncStatus } = useSync();
  const queue = useSyncQueue();

  const handleClearDB = async () => {
    // Warning: Quick hack to clear queue
    const items = await dbService.getQueue();
    for(const item of items) {
        await dbService.removeFromQueue(item.id);
    }
    triggerSync(); // Forces refresh
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Debug Synchronisation</h1>
        <div className="flex space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${isOffline ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {isOffline ? 'OFFLINE' : 'ONLINE'}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700">
                {syncStatus}
            </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
            <h3 className="text-lg font-bold mb-4 flex items-center"><Database className="mr-2"/> Actions</h3>
            <div className="space-y-2">
                <Button fullWidth onClick={() => triggerSync()} leftIcon={<RefreshCw size={18}/>}>
                    Forcer Synchro Manuelle
                </Button>
                <Button fullWidth variant={ButtonVariant.SECONDARY} onClick={() => enqueueAction('exercise_attempt', { exerciseId: 'ex123', score: 90 })} leftIcon={<Plus size={18}/>}>
                    Add Attempt (+1 High Prio)
                </Button>
                <Button fullWidth variant={ButtonVariant.SECONDARY} onClick={() => enqueueAction('badge_claim', { badgeId: 'b_math' })} leftIcon={<Plus size={18}/>}>
                    Add Badge (+2 Med Prio)
                </Button>
                 <Button fullWidth variant={ButtonVariant.SECONDARY} onClick={() => enqueueAction('analytics', { event: 'view_page' })} leftIcon={<Plus size={18}/>}>
                    Add Analytics (+4 Low Prio)
                </Button>
                <Button fullWidth variant={ButtonVariant.DANGER} onClick={handleClearDB} leftIcon={<Trash2 size={18}/>}>
                    Vider IndexedDB
                </Button>
            </div>
        </Card>

        <Card>
             <h3 className="text-lg font-bold mb-4">File d'attente (IndexedDB)</h3>
             {queue.length === 0 ? (
                 <p className="text-gray-400 italic">La file d'attente est vide.</p>
             ) : (
                 <div className="space-y-3 max-h-60 overflow-y-auto">
                     {queue.map(item => (
                         <div key={item.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-sm">
                             <div className="flex justify-between items-start">
                                 <span className="font-bold text-gray-700">{item.type}</span>
                                 <Badge 
                                    label={`P${item.priority}`} 
                                    color={item.priority === 1 ? 'red' : item.priority === 4 ? 'gray' : 'blue'} 
                                    size="sm"
                                />
                             </div>
                             <div className="text-xs text-gray-500 mt-1">
                                 ID: {item.id.slice(0, 8)}...<br/>
                                 Retries: {item.retryCount}
                             </div>
                         </div>
                     ))}
                 </div>
             )}
        </Card>
      </div>

      <div className="bg-amber-50 p-4 rounded-xl text-xs text-amber-800 font-mono">
          <p>NOTE: Pour tester le comportement offline, utilisez les DevTools du navigateur (Network &gt; Offline) ou le bouton Toggle Offline du Dashboard, puis ajoutez des actions.</p>
      </div>
    </div>
  );
};