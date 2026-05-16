import React, { useState, useEffect, useCallback } from 'react';
import { DataTable } from '../../components/admin/DataTable';
import { Skeleton } from '../../components/ui/Skeleton';
import { Badge } from '../../components/ui/Cards';
import { AlertTriangle, AlertCircle, Phone, Calendar, TrendingDown, Download, Send, Loader2 } from 'lucide-react';
import { adminService, AtRiskLevel, AtRiskStudentDTO } from '../../services/adminService';

type RowWithId = AtRiskStudentDTO & { id: string };

const PAGE_SIZE = 50;

const riskBadge = (level: AtRiskStudentDTO['riskLevel']) => {
    if (level === 'high') {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-100 text-red-700 text-xs font-bold">
                <AlertCircle size={12} /> Élevé
            </span>
        );
    }
    if (level === 'medium') {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 text-xs font-bold">
                <AlertTriangle size={12} /> Modéré
            </span>
        );
    }
    return <Badge label="Faible" color="gray" size="sm" />;
};

const formatDate = (iso: string | null): string => {
    if (!iso) return '—';
    try {
        return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
        return '—';
    }
};

export const AdminAtRiskPage: React.FC = () => {
    const [minLevel, setMinLevel] = useState<AtRiskLevel>('medium');
    const [rows, setRows] = useState<RowWithId[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [smsBusy, setSmsBusy] = useState<Set<string>>(new Set());
    const [toast, setToast] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const load = useCallback(async (p: number, level: AtRiskLevel) => {
        setIsLoading(true);
        try {
            const result = await adminService.listAtRisk(level, p, PAGE_SIZE);
            setRows(result.items.map(r => ({ ...r, id: r.profileId })));
            setTotalPages(result.totalPages || 1);
            setTotal(result.total);
            setPage(result.page);
        } catch {
            setRows([]);
            setTotal(0);
            setTotalPages(1);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => { load(1, minLevel); }, [load, minLevel]);

    const handleExportCsv = () => {
        adminService.exportAtRiskCsv(minLevel);
    };

    const handleSendSms = async (row: RowWithId) => {
        if (!row.parentPhone) return;
        const childName = row.displayName;
        if (!window.confirm(`Envoyer un SMS au parent de ${childName} maintenant ?`)) return;
        setSmsBusy(prev => new Set(prev).add(row.profileId));
        try {
            await adminService.sendInactivitySms(row.profileId);
            setToast({ type: 'success', text: `SMS envoyé au parent de ${childName}.` });
        } catch (err: any) {
            const msg = err?.message?.includes('NOTIFICATION_THROTTLED')
                ? 'Limite SMS quotidienne atteinte pour ce parent.'
                : err?.message?.includes('NOT_AT_RISK')
                ? 'Ce profil n\'est plus classé à risque (recharger).'
                : err?.message?.includes('NO_PARENT_PHONE')
                ? 'Aucun téléphone parent disponible.'
                : err?.message || 'Erreur lors de l\'envoi.';
            setToast({ type: 'error', text: msg });
        } finally {
            setSmsBusy(prev => {
                const next = new Set(prev);
                next.delete(row.profileId);
                return next;
            });
            setTimeout(() => setToast(null), 4000);
        }
    };

    const counts = {
        high: rows.filter(r => r.riskLevel === 'high').length,
        medium: rows.filter(r => r.riskLevel === 'medium').length,
    };

    const columns = [
        {
            header: 'Élève',
            accessor: (row: RowWithId) => (
                <div>
                    <div className="font-bold text-gray-900">{row.displayName}</div>
                    {row.gradeLevel && (
                        <div className="text-xs text-gray-500">{row.gradeLevel}</div>
                    )}
                </div>
            ),
        },
        {
            header: 'Risque',
            accessor: (row: RowWithId) => riskBadge(row.riskLevel),
        },
        {
            header: 'Inactivité',
            accessor: (row: RowWithId) => (
                <span className="inline-flex items-center gap-1 text-sm text-gray-700">
                    <Calendar size={14} className="text-gray-400" />
                    {row.daysInactive} j
                </span>
            ),
        },
        {
            header: 'Score moyen',
            accessor: (row: RowWithId) => {
                const color = row.avgScore < 30 ? 'text-red-600' : row.avgScore < 40 ? 'text-amber-600' : 'text-gray-700';
                return (
                    <span className={`inline-flex items-center gap-1 text-sm font-semibold ${color}`}>
                        <TrendingDown size={14} className="text-gray-400" />
                        {row.avgScore.toFixed(1)}%
                    </span>
                );
            },
        },
        {
            header: 'Dernière session',
            accessor: (row: RowWithId) => (
                <span className="text-sm text-gray-600">{formatDate(row.lastCompletedAt)}</span>
            ),
        },
        {
            header: 'Parent',
            accessor: (row: RowWithId) => (
                row.parentPhone ? (
                    <a
                        href={`tel:${row.parentPhone}`}
                        className="inline-flex items-center gap-1 text-sitou-primary hover:underline text-sm"
                    >
                        <Phone size={14} /> {row.parentPhone}
                    </a>
                ) : (
                    <span className="text-xs text-gray-400">aucun parent lié</span>
                )
            ),
        },
        {
            header: 'Action suggérée',
            accessor: (row: RowWithId) => (
                <span className="text-sm text-gray-700">{row.suggestedAction || '—'}</span>
            ),
        },
        {
            header: '',
            accessor: (row: RowWithId) => {
                const busy = smsBusy.has(row.profileId);
                const disabled = !row.parentPhone || busy;
                return (
                    <button
                        type="button"
                        onClick={() => handleSendSms(row)}
                        disabled={disabled}
                        title={
                            !row.parentPhone
                                ? 'Pas de téléphone parent'
                                : 'Envoyer un SMS au parent maintenant'
                        }
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold bg-sitou-primary text-white hover:bg-amber-600 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                        {busy ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                        SMS
                    </button>
                );
            },
        },
    ];

    if (isLoading && rows.length === 0) {
        return (
            <div className="space-y-6">
                <Skeleton variant="text" className="w-72 h-8" />
                <Skeleton variant="rect" className="h-96" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <header className="flex items-start justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
                        <AlertTriangle className="text-amber-600" size={26} />
                        Élèves à risque
                    </h1>
                    <p className="text-gray-500 text-sm">
                        Détection unifiée : inactivité ≥ 3 j ou score moyen &lt; 40 %. Même formule que l'alerte SMS parent (cron quotidien 11:30 UTC).
                    </p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                    <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-xl p-1 shadow-sm">
                        {(['medium', 'high'] as AtRiskLevel[]).map(level => (
                            <button
                                key={level}
                                type="button"
                                onClick={() => setMinLevel(level)}
                                aria-pressed={minLevel === level}
                                className={
                                    'px-3 py-1.5 rounded-lg text-sm font-bold transition-colors ' +
                                    (minLevel === level
                                        ? 'bg-sitou-primary text-white'
                                        : 'text-gray-600 hover:bg-gray-50')
                                }
                            >
                                {level === 'high' ? 'Élevé uniquement' : 'Modéré + Élevé'}
                            </button>
                        ))}
                    </div>
                    <button
                        type="button"
                        onClick={handleExportCsv}
                        disabled={total === 0}
                        className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-bold bg-white border border-gray-200 text-gray-700 hover:border-sitou-primary hover:text-sitou-primary disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
                    >
                        <Download size={14} />
                        Export CSV
                    </button>
                </div>
            </header>

            {toast && (
                <div
                    role="status"
                    className={`px-4 py-2 rounded-xl text-sm font-medium ${
                        toast.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}
                >
                    {toast.text}
                </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white border border-gray-200 rounded-xl p-4">
                    <p className="text-xs font-bold text-gray-500 uppercase">Total affiché</p>
                    <p className="text-2xl font-extrabold text-gray-900">{total}</p>
                </div>
                <div className="bg-white border border-red-100 rounded-xl p-4">
                    <p className="text-xs font-bold text-red-600 uppercase">Risque élevé (page)</p>
                    <p className="text-2xl font-extrabold text-red-700">{counts.high}</p>
                </div>
                <div className="bg-white border border-amber-100 rounded-xl p-4">
                    <p className="text-xs font-bold text-amber-600 uppercase">Risque modéré (page)</p>
                    <p className="text-2xl font-extrabold text-amber-700">{counts.medium}</p>
                </div>
            </div>

            <DataTable<RowWithId>
                columns={columns}
                data={rows}
                pagination={
                    totalPages > 1
                        ? {
                            currentPage: page,
                            totalPages,
                            onPageChange: p => load(p, minLevel),
                        }
                        : undefined
                }
            />
        </div>
    );
};
