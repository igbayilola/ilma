import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import { Users, TrendingUp, DollarSign, AlertTriangle, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { adminService, KpiDTO } from '../../services/adminService';

const AdminStatCard = ({ title, value, icon, color }: any) => (
    <Card className="flex flex-col justify-between h-32 relative overflow-hidden">
        <div className="flex justify-between items-start z-10">
            <div>
                <p className="text-sm font-bold text-gray-500 uppercase tracking-wide">{title}</p>
                <h3 className="text-2xl font-extrabold text-gray-900 mt-1">{value}</h3>
            </div>
            <div className={`p-2 rounded-lg ${color} text-white shadow-md`}>
                {icon}
            </div>
        </div>
        {/* Decor */}
        <div className={`absolute -bottom-4 -right-4 w-24 h-24 rounded-full opacity-10 ${color}`}></div>
    </Card>
);

export const AdminDashboard: React.FC = () => {
    const [kpis, setKpis] = useState<KpiDTO | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        adminService.getKpis()
            .then(setKpis)
            .catch(() => setKpis(null))
            .finally(() => setIsLoading(false));
    }, []);

    const formatNumber = (n: number) => {
        if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
        if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
        return String(n);
    };

    if (isLoading) {
        return (
            <div className="space-y-8">
                <Skeleton variant="text" className="w-64 h-8" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[1,2,3,4].map(i => <Skeleton key={i} variant="rect" className="h-32" />)}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <header>
                <h1 className="text-2xl font-extrabold text-gray-900">Tableau de bord</h1>
                <p className="text-gray-500">Vue d'ensemble de la performance de la plateforme.</p>
            </header>

            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <AdminStatCard
                    title="Utilisateurs Totaux"
                    value={formatNumber(kpis?.totalUsers ?? 0)}
                    icon={<Users size={20} />}
                    color="bg-blue-600"
                />
                <AdminStatCard
                    title="Revenus Mensuels"
                    value={`${formatNumber(kpis?.mrrXof ?? 0)} F`}
                    icon={<DollarSign size={20} />}
                    color="bg-green-600"
                />
                <AdminStatCard
                    title="Abonnés Actifs"
                    value={formatNumber(kpis?.activeSubscriptions ?? 0)}
                    icon={<TrendingUp size={20} />}
                    color="bg-purple-600"
                />
                <AdminStatCard
                    title="Sessions Aujourd'hui"
                    value={String(kpis?.sessionsToday ?? 0)}
                    icon={<Activity size={20} />}
                    color="bg-orange-500"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Engagement Metrics */}
                <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-gray-800 flex items-center">
                            <Activity size={20} className="mr-2 text-ilma-primary" /> Métriques d'engagement
                        </h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="text-center">
                            <span className="block text-3xl font-extrabold text-ilma-primary">{kpis?.dau ?? 0}</span>
                            <span className="text-xs text-gray-500 uppercase font-bold">DAU</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-3xl font-extrabold text-amber-600">{kpis?.mau ?? 0}</span>
                            <span className="text-xs text-gray-500 uppercase font-bold">MAU</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-3xl font-extrabold text-green-600">{kpis?.totalStudents ?? 0}</span>
                            <span className="text-xs text-gray-500 uppercase font-bold">Élèves</span>
                        </div>
                        <div className="text-center">
                            <span className="block text-3xl font-extrabold text-orange-500">{kpis?.avgSessionScore ?? 0}%</span>
                            <span className="text-xs text-gray-500 uppercase font-bold">Score Moyen</span>
                        </div>
                    </div>
                </div>

                {/* Quick Status */}
                <div className="space-y-6">
                    <Card>
                        <h3 className="font-bold text-gray-800 mb-4">État du Système</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">Base de données</span>
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">Opérationnel</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">API Paiements</span>
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">Opérationnel</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-600">Stockage Fichiers</span>
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold">Opérationnel</span>
                            </div>
                        </div>
                    </Card>

                    <Card className="bg-gradient-to-br from-ilma-primary to-amber-800 text-white border-none">
                        <h3 className="font-bold mb-2">Résumé</h3>
                        <p className="text-amber-100 text-sm mb-2">
                            {kpis?.dau ?? 0} utilisateur(s) actif(s) aujourd'hui, {kpis?.activeSubscriptions ?? 0} abonné(s).
                        </p>
                    </Card>
                </div>
            </div>
        </div>
    );
};
