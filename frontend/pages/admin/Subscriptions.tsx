import React, { useState, useEffect, useCallback } from 'react';
import { DataTable } from '../../components/admin/DataTable';
import { Badge } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { Download } from 'lucide-react';
import { adminService, PaymentDTO, KpiDTO } from '../../services/adminService';

export const AdminSubsPage: React.FC = () => {
    const [payments, setPayments] = useState<PaymentDTO[]>([]);
    const [kpis, setKpis] = useState<KpiDTO | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const loadPayments = useCallback(async (p: number) => {
        setIsLoading(true);
        try {
            const result = await adminService.listPayments(p, 50);
            setPayments(result.items);
            setTotalPages(result.totalPages);
            setPage(result.page);
        } catch {
            setPayments([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        Promise.all([
            loadPayments(1),
            adminService.getKpis().then(setKpis).catch(() => null),
        ]);
    }, [loadPayments]);

    const formatDate = (iso?: string) => {
        if (!iso) return '—';
        return new Date(iso).toLocaleDateString('fr-FR');
    };

    const formatAmount = (n: number) => n.toLocaleString('fr-FR');

    const columns = [
        { header: 'ID', accessor: (row: any) => <span className="font-mono text-xs">{row.id.substring(0, 8)}</span> },
        { header: 'Utilisateur', accessor: 'userName', className: 'font-bold' },
        {
            header: 'Montant',
            accessor: (row: any) => <span className="font-bold">{formatAmount(row.amountXof)} FCFA</span>
        },
        { header: 'Provider', accessor: (row: any) => <span className="text-xs text-gray-500 uppercase">{row.provider}</span> },
        {
            header: 'Statut',
            accessor: (row: any) => {
                const color = row.status === 'completed' ? 'green' : row.status === 'failed' ? 'red' : row.status === 'refunded' ? 'gray' : 'orange';
                return <Badge label={row.status} color={color} size="sm" />;
            }
        },
        { header: 'Date', accessor: (row: any) => formatDate(row.createdAt) },
    ];

    if (isLoading && payments.length === 0) {
        return (
            <div className="space-y-6">
                <Skeleton variant="text" className="w-64 h-8" />
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {[1,2,3,4].map(i => <Skeleton key={i} variant="rect" className="h-20" />)}
                </div>
                <Skeleton variant="rect" className="h-64" />
            </div>
        );
    }

    return (
        <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Abonnements & Transactions</h1>
                    <p className="text-gray-500 text-sm">Suivi financier et gestion des souscriptions.</p>
                </div>
                <Button variant={ButtonVariant.SECONDARY} leftIcon={<Download size={18}/>} onClick={() => adminService.exportUsersCsv()}>
                    Export CSV
                </Button>
            </header>

            {/* Financial Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div className="p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
                    <span className="text-xs text-gray-500 uppercase font-bold">Revenu Mensuel</span>
                    <div className="text-2xl font-extrabold text-gray-900 mt-1">
                        {kpis ? `${formatAmount(kpis.mrrXof)} F` : '—'}
                    </div>
                </div>
                <div className="p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
                    <span className="text-xs text-gray-500 uppercase font-bold">Abonnés Actifs</span>
                    <div className="text-2xl font-extrabold text-ilma-primary mt-1">
                        {kpis?.activeSubscriptions ?? '—'}
                    </div>
                </div>
                <div className="p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
                    <span className="text-xs text-gray-500 uppercase font-bold">Utilisateurs Totaux</span>
                    <div className="text-2xl font-extrabold text-blue-600 mt-1">
                        {kpis?.totalUsers ?? '—'}
                    </div>
                </div>
                <div className="p-4 bg-white border border-gray-200 rounded-xl shadow-sm">
                    <span className="text-xs text-gray-500 uppercase font-bold">Élèves</span>
                    <div className="text-2xl font-extrabold text-green-600 mt-1">
                        {kpis?.totalStudents ?? '—'}
                    </div>
                </div>
            </div>

            <DataTable
                columns={columns}
                data={payments}
                pagination={{
                    currentPage: page,
                    totalPages,
                    onPageChange: (p: number) => loadPayments(p),
                }}
            />
        </div>
    );
};
