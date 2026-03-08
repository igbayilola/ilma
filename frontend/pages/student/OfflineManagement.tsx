
import React, { useEffect, useState, useRef } from 'react';
import { Card, Badge } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { ButtonVariant } from '../../types';
import { useOfflineStore } from '../../store/offlineStore';
import { AVAILABLE_PACKS, offlineManager } from '../../services/offlineManager';
import { Cloud, Download, Trash2, Database, AlertCircle, CheckCircle2, RefreshCw, HardDrive } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const formatBytes = (bytes: number, decimals = 2) => {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
};

export const OfflineManagementPage: React.FC = () => {
    const { 
        installedPacks, 
        storageStats, 
        downloadingId, 
        downloadProgress, 
        refreshData, 
        installPack, 
        removePack,
        updatePack
    } = useOfflineStore();
    const navigate = useNavigate();

    const [downloadStartTime, setDownloadStartTime] = useState<number>(0);
    const [estimatedTime, setEstimatedTime] = useState<string>('');
    const prevDownloadingId = useRef<string | null>(null);

    // LRU cleanup confirmation
    const [cleanupCandidates, setCleanupCandidates] = useState<Array<{ id: string; name: string; size: number; lastUsed: Date }>>([]);
    const [showCleanupModal, setShowCleanupModal] = useState(false);

    // Track when a download starts to record the start time
    useEffect(() => {
        if (downloadingId && downloadingId !== prevDownloadingId.current) {
            setDownloadStartTime(Date.now());
            setEstimatedTime('');
        }
        if (!downloadingId) {
            setEstimatedTime('');
        }
        prevDownloadingId.current = downloadingId;
    }, [downloadingId]);

    // Calculate estimated time remaining as progress updates
    useEffect(() => {
        if (!downloadingId || downloadProgress <= 0 || downloadStartTime === 0) return;
        const elapsed = (Date.now() - downloadStartTime) / 1000; // seconds
        if (elapsed < 0.5) return; // wait a bit before estimating
        const rate = downloadProgress / elapsed; // % per second
        if (rate <= 0) return;
        const remaining = (100 - downloadProgress) / rate; // seconds remaining
        if (remaining < 60) {
            setEstimatedTime(`~${Math.ceil(remaining)}s restantes`);
        } else {
            setEstimatedTime(`~${Math.ceil(remaining / 60)}min restantes`);
        }
    }, [downloadProgress, downloadingId, downloadStartTime]);

    const [availablePacks, setAvailablePacks] = useState(AVAILABLE_PACKS);

    useEffect(() => {
        offlineManager.fetchAvailablePacks().then(packs => {
            setAvailablePacks(packs);
        });
        refreshData();
    }, [refreshData]);

    // Check if storage is above 80% and suggest cleanup
    useEffect(() => {
        if (!storageStats || storageStats.percentUsed < 80) return;
        const targetFree = storageStats.quota * 0.3; // free 30% of quota
        offlineManager.getCleanupCandidates(targetFree).then(candidates => {
            if (candidates.length > 0) {
                setCleanupCandidates(candidates);
                setShowCleanupModal(true);
            }
        }).catch(() => {});
    }, [storageStats]);

    const handleConfirmCleanup = async () => {
        await offlineManager.confirmCleanup(cleanupCandidates.map(c => c.id));
        setShowCleanupModal(false);
        setCleanupCandidates([]);
        refreshData();
    };

    const getPackStatus = (id: string) => {
        const installed = installedPacks.find(p => p.id === id);
        if (installed) {
            if (installed.isUpdateAvailable) return 'UPDATE';
            return 'INSTALLED';
        }
        if (downloadingId === id) return 'DOWNLOADING';
        return 'AVAILABLE';
    };

    return (
        <div className="space-y-6 max-w-4xl mx-auto pb-10">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900 flex items-center">
                        <Cloud size={28} className="mr-3 text-ilma-primary" />
                        Gestion Hors-Ligne
                    </h1>
                    <p className="text-gray-500">Gérez le contenu téléchargé sur votre appareil.</p>
                </div>
                <Button variant={ButtonVariant.GHOST} onClick={() => navigate(-1)}>
                    Retour
                </Button>
            </header>

            {/* Storage Usage Card */}
            {storageStats && (
                <Card className="bg-gradient-to-r from-gray-50 to-white">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-gray-800 flex items-center">
                            <HardDrive size={20} className="mr-2 text-gray-600" /> Stockage Appareil
                        </h3>
                        <span className="text-xs font-bold bg-gray-200 px-2 py-1 rounded text-gray-600">
                             {formatBytes(storageStats.used)} utilisés / {formatBytes(storageStats.quota)}
                        </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-4 mb-2 overflow-hidden">
                        <div 
                            className={`h-full rounded-full transition-all duration-1000 ${storageStats.percentUsed > 80 ? 'bg-red-500' : 'bg-ilma-primary'}`} 
                            style={{ width: `${storageStats.percentUsed}%` }} 
                        />
                    </div>
                    <div className="text-right text-xs text-gray-400">
                        {storageStats.percentUsed.toFixed(1)}% utilisé
                    </div>
                </Card>
            )}

            {/* Packs List */}
            <div className="grid grid-cols-1 gap-4">
                {availablePacks.map(pack => {
                    const status = getPackStatus(pack.id);
                    const localPack = installedPacks.find(p => p.id === pack.id);

                    return (
                        <Card key={pack.id} className="flex flex-col md:flex-row md:items-center p-4">
                            {/* Icon/Thumbnail */}
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mr-4 flex-shrink-0 ${status === 'INSTALLED' ? 'bg-green-100 text-green-600' : 'bg-amber-50 text-amber-500'}`}>
                                <Database size={24} />
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0 mb-4 md:mb-0">
                                <div className="flex items-center space-x-2">
                                    <h3 className="font-bold text-gray-900 truncate">{pack.title}</h3>
                                    {status === 'INSTALLED' && <CheckCircle2 size={16} className="text-green-500" />}
                                    {status === 'UPDATE' && <Badge label="Mise à jour" color="orange" size="sm" />}
                                </div>
                                <p className="text-sm text-gray-500 mb-1">{pack.description}</p>
                                <div className="flex items-center text-xs text-gray-400 space-x-3">
                                    <span>v{pack.version}</span>
                                    <span>•</span>
                                    <span>{formatBytes(pack.size)}</span>
                                    <span>•</span>
                                    <span>{pack.itemsCount} éléments</span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="w-full md:w-auto md:pl-4 flex items-center justify-end">
                                {status === 'DOWNLOADING' && (
                                    <div className="w-full md:w-48">
                                        <div className="flex justify-between text-xs mb-1">
                                            <span className="font-bold text-ilma-primary">Téléchargement...</span>
                                            <span>{Math.round(downloadProgress)}%</span>
                                        </div>
                                        <div className="w-full bg-gray-100 rounded-full h-2">
                                            <div className="bg-ilma-primary h-full rounded-full transition-all duration-300" style={{ width: `${downloadProgress}%` }} />
                                        </div>
                                        {estimatedTime && (
                                            <div className="text-xs text-gray-400 mt-1 text-right">{estimatedTime}</div>
                                        )}
                                    </div>
                                )}

                                {status === 'AVAILABLE' && (
                                    <Button 
                                        size="sm" 
                                        leftIcon={<Download size={16}/>} 
                                        onClick={() => installPack(pack.id)}
                                        disabled={!!downloadingId}
                                    >
                                        Télécharger
                                    </Button>
                                )}

                                {status === 'UPDATE' && (
                                    <Button 
                                        size="sm" 
                                        variant={ButtonVariant.PRIMARY}
                                        leftIcon={<RefreshCw size={16}/>} 
                                        onClick={() => updatePack(pack.id)}
                                        disabled={!!downloadingId}
                                    >
                                        Mettre à jour
                                    </Button>
                                )}

                                {status === 'INSTALLED' && (
                                    <Button 
                                        size="sm" 
                                        variant={ButtonVariant.DANGER}
                                        leftIcon={<Trash2 size={16}/>} 
                                        onClick={() => {
                                            if(confirm('Supprimer ce pack ?')) removePack(pack.id);
                                        }}
                                        className="bg-red-50 text-red-600 hover:bg-red-100 border-none shadow-none"
                                    >
                                        Supprimer
                                    </Button>
                                )}
                            </div>
                        </Card>
                    );
                })}
            </div>
            
            <div className="bg-amber-50 p-4 rounded-xl flex items-start">
                <AlertCircle className="text-amber-500 mr-3 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-sm text-amber-800">
                    <strong>Note:</strong> Le système vous demandera confirmation avant de supprimer les anciens packs si l'espace devient critique.
                </p>
            </div>

            {/* LRU Cleanup Confirmation Modal */}
            <Modal isOpen={showCleanupModal} onClose={() => setShowCleanupModal(false)} title="Espace presque plein">
                <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                        L'espace de stockage est presque plein. Voulez-vous supprimer les packs suivants (non utilisés récemment) ?
                    </p>
                    <ul className="space-y-2">
                        {cleanupCandidates.map(c => (
                            <li key={c.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                                <div>
                                    <p className="font-medium text-gray-800 text-sm">{c.name}</p>
                                    <p className="text-xs text-gray-400">
                                        Non utilisé depuis {Math.round((Date.now() - c.lastUsed.getTime()) / (1000 * 60 * 60 * 24))} jours — {formatBytes(c.size)}
                                    </p>
                                </div>
                                <Trash2 size={16} className="text-gray-300" />
                            </li>
                        ))}
                    </ul>
                    <div className="flex gap-3 pt-2">
                        <Button fullWidth variant={ButtonVariant.DANGER} onClick={handleConfirmCleanup}>
                            Supprimer
                        </Button>
                        <Button fullWidth variant={ButtonVariant.GHOST} onClick={() => setShowCleanupModal(false)}>
                            Garder
                        </Button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};
