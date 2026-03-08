import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { Download, Users, BookOpen } from 'lucide-react';
import { DataTable } from '../../components/admin/DataTable';
import { adminService, KpiDTO, QuestionStatDTO } from '../../services/adminService';

export const AdminAnalyticsPage: React.FC = () => {
    const [kpis, setKpis] = useState<KpiDTO | null>(null);
    const [questionStats, setQuestionStats] = useState<QuestionStatDTO[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            adminService.getKpis().catch(() => null),
            adminService.getQuestionStats(50).catch(() => []),
        ]).then(([k, qs]) => {
            if (k) setKpis(k);
            setQuestionStats(qs);
        }).finally(() => setIsLoading(false));
    }, []);

    const difficultQuestions = questionStats.filter(q => q.successRate < 50);

    const columns = [
        { header: 'Question', accessor: (row: any) => <span className="font-medium">{row.prompt.length > 60 ? row.prompt.substring(0, 60) + '…' : row.prompt}</span> },
        { header: 'Compétence', accessor: 'skillName' },
        {
            header: 'Taux Réussite',
            accessor: (row: any) => {
                const color = row.successRate > 80 ? 'text-green-600' : row.successRate < 50 ? 'text-red-600' : 'text-orange-600';
                return <span className={`font-bold ${color}`}>{row.successRate}%</span>;
            }
        },
        { header: 'Temps Moyen', accessor: (row: any) => `${row.avgTimeSeconds}s` },
        { header: 'Tentatives', accessor: 'totalAttempts' },
    ];

    if (isLoading) {
        return (
            <div className="space-y-8">
                <Skeleton variant="text" className="w-64 h-8" />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Skeleton variant="rect" className="h-64" />
                    <Skeleton variant="rect" className="h-64" />
                </div>
                <Skeleton variant="rect" className="h-64" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
             <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Analytics & Rapports</h1>
                    <p className="text-gray-500 text-sm">Analyse pédagogique et engagement.</p>
                </div>
                <div className="flex space-x-3">
                    <Button variant={ButtonVariant.SECONDARY} leftIcon={<Download size={18}/>} onClick={() => adminService.exportUsersCsv()}>
                        Export CSV
                    </Button>
                </div>
            </header>

            {/* Engagement Summary */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Users size={20} className="mr-2 text-ilma-primary" /> Engagement
                    </h3>
                    <div className="grid grid-cols-2 gap-6">
                        <div className="text-center p-4 bg-amber-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-ilma-primary">{kpis?.dau ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">DAU</span>
                        </div>
                        <div className="text-center p-4 bg-amber-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-amber-600">{kpis?.mau ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">MAU</span>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-green-600">{kpis?.sessionsToday ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Sessions/jour</span>
                        </div>
                        <div className="text-center p-4 bg-orange-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-orange-500">{kpis?.avgSessionScore ?? 0}%</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Score moyen</span>
                        </div>
                    </div>
                </Card>

                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <BookOpen size={20} className="mr-2 text-green-600" /> Répartition
                    </h3>
                    <div className="grid grid-cols-2 gap-6">
                        <div className="text-center p-4 bg-gray-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-gray-900">{kpis?.totalUsers ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Total utilisateurs</span>
                        </div>
                        <div className="text-center p-4 bg-gray-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-gray-900">{kpis?.totalStudents ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Élèves</span>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-purple-600">{kpis?.activeSubscriptions ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Abonnés actifs</span>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-green-600">{kpis?.mrrXof ? `${(kpis.mrrXof / 1000).toFixed(0)}k` : '0'}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">MRR (FCFA)</span>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Difficult Questions Table */}
            <div>
                <h3 className="font-bold text-lg text-gray-900 mb-4">
                    Questions Difficiles (Taux de réussite &lt; 50%)
                    {difficultQuestions.length > 0 && <span className="text-sm font-normal text-gray-500 ml-2">({difficultQuestions.length} question(s))</span>}
                </h3>
                {difficultQuestions.length === 0 ? (
                    <Card className="text-center py-8 text-gray-500">
                        Aucune question difficile détectée, ou pas encore assez de données.
                    </Card>
                ) : (
                    <DataTable
                        columns={columns}
                        data={difficultQuestions}
                    />
                )}
            </div>
        </div>
    );
};
