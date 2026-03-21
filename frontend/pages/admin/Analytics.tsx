import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { Download, Users, BookOpen, Mail, TrendingUp, Target, Share2, Bell, AlertTriangle } from 'lucide-react';
import { DataTable } from '../../components/admin/DataTable';
import {
    adminService,
    KpiDTO,
    QuestionStatDTO,
    DigestStatsDTO,
    EngagementDTO,
    RetentionCohortDTO,
    ConversionDTO,
    ViralityDTO,
    NotificationStatsDTO,
} from '../../services/adminService';

/* ── Retention cell color helper ── */
function retentionColor(val: number | null): string {
    if (val === null) return 'text-gray-400 bg-gray-50';
    if (val >= 40) return 'text-green-700 bg-green-100';
    if (val >= 20) return 'text-orange-700 bg-orange-100';
    return 'text-red-700 bg-red-100';
}

/* ── Simple bar component for funnel ── */
const FunnelBar: React.FC<{ stage: string; count: number; rate: number; maxCount: number }> = ({ stage, count, rate, maxCount }) => {
    const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
    return (
        <div className="flex items-center gap-3 py-2">
            <div className="w-44 text-sm font-medium text-gray-700 shrink-0">{stage}</div>
            <div className="flex-1 bg-gray-100 rounded-full h-7 relative overflow-hidden">
                <div
                    className="bg-ilma-primary h-7 rounded-full transition-all duration-500"
                    style={{ width: `${Math.max(pct, 2)}%` }}
                />
                <span className="absolute inset-0 flex items-center justify-center text-xs font-bold text-gray-800">
                    {count}
                </span>
            </div>
            <span className="w-16 text-right text-sm font-bold text-gray-600">{rate}%</span>
        </div>
    );
};

/* ── Mini sparkline (pure CSS bar chart for 30d DAU) ── */
const MiniChart: React.FC<{ data: { date: string; dau: number }[] }> = ({ data }) => {
    const max = Math.max(...data.map(d => d.dau), 1);
    return (
        <div className="flex items-end gap-px h-24 mt-2" role="img" aria-label="DAU sur 30 jours">
            {data.map((d, i) => (
                <div
                    key={i}
                    className="flex-1 bg-ilma-primary/70 hover:bg-ilma-primary rounded-t transition-colors"
                    style={{ height: `${Math.max((d.dau / max) * 100, 2)}%` }}
                    title={`${d.date}: ${d.dau} actifs`}
                />
            ))}
        </div>
    );
};

export const AdminAnalyticsPage: React.FC = () => {
    const [kpis, setKpis] = useState<KpiDTO | null>(null);
    const [questionStats, setQuestionStats] = useState<QuestionStatDTO[]>([]);
    const [digestStats, setDigestStats] = useState<DigestStatsDTO | null>(null);
    const [engagement, setEngagement] = useState<EngagementDTO | null>(null);
    const [retention, setRetention] = useState<RetentionCohortDTO[]>([]);
    const [conversion, setConversion] = useState<ConversionDTO | null>(null);
    const [virality, setVirality] = useState<ViralityDTO | null>(null);
    const [notifStats, setNotifStats] = useState<NotificationStatsDTO | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            adminService.getKpis().catch(() => null),
            adminService.getQuestionStats(50).catch(() => []),
            adminService.getDigestStats().catch(() => null),
            adminService.getEngagement().catch(() => null),
            adminService.getRetention().catch(() => []),
            adminService.getConversion().catch(() => null),
            adminService.getVirality().catch(() => null),
            adminService.getNotificationStats().catch(() => null),
        ]).then(([k, qs, ds, eng, ret, conv, vir, ns]) => {
            if (k) setKpis(k);
            setQuestionStats(qs);
            if (ds) setDigestStats(ds);
            if (eng) setEngagement(eng);
            setRetention(ret);
            if (conv) setConversion(conv);
            if (vir) setVirality(vir);
            if (ns) setNotifStats(ns);
        }).finally(() => setIsLoading(false));
    }, []);

    const difficultQuestions = questionStats.filter(q => q.successRate < 50);

    const columns = [
        { header: 'Question', accessor: (row: any) => <span className="font-medium">{row.prompt.length > 60 ? row.prompt.substring(0, 60) + '\u2026' : row.prompt}</span> },
        { header: 'Comp\u00e9tence', accessor: 'skillName' },
        {
            header: 'Taux R\u00e9ussite',
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

    const maxFunnelCount = conversion?.stages?.[0]?.count ?? 1;

    return (
        <div className="space-y-8">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Analytics & Rapports</h1>
                    <p className="text-gray-500 text-sm">Analyse p\u00e9dagogique, engagement et croissance.</p>
                </div>
                <div className="flex space-x-3">
                    <Button variant={ButtonVariant.SECONDARY} leftIcon={<Download size={18}/>} onClick={() => adminService.exportUsersCsv()}>
                        Export CSV
                    </Button>
                </div>
            </header>

            {/* ── ANALYTICS.1: Engagement ── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Users size={20} className="mr-2 text-ilma-primary" /> Engagement
                    </h3>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="text-center p-4 bg-amber-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-ilma-primary">{engagement?.dau ?? kpis?.dau ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">DAU</span>
                        </div>
                        <div className="text-center p-4 bg-blue-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-blue-600">{engagement?.wau ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">WAU</span>
                        </div>
                        <div className="text-center p-4 bg-amber-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-amber-600">{engagement?.mau ?? kpis?.mau ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">MAU</span>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-green-600">{((engagement?.stickiness ?? 0) * 100).toFixed(1)}%</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">DAU/MAU</span>
                        </div>
                    </div>
                    {engagement?.timeSeries && engagement.timeSeries.length > 0 && (
                        <div>
                            <p className="text-xs text-gray-400 font-bold uppercase mb-1">DAU - 30 derniers jours</p>
                            <MiniChart data={engagement.timeSeries} />
                        </div>
                    )}
                </Card>

                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <BookOpen size={20} className="mr-2 text-green-600" /> R\u00e9partition
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-gray-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-gray-900">{kpis?.totalUsers ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Total utilisateurs</span>
                        </div>
                        <div className="text-center p-4 bg-gray-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-gray-900">{kpis?.totalStudents ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">\u00c9l\u00e8ves</span>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-purple-600">{kpis?.activeSubscriptions ?? 0}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Abonn\u00e9s actifs</span>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-green-600">{kpis?.mrrXof ? `${(kpis.mrrXof / 1000).toFixed(0)}k` : '0'}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">MRR (FCFA)</span>
                        </div>
                    </div>
                </Card>
            </div>

            {/* ── ANALYTICS.2: Retention ── */}
            {retention.length > 0 && (
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <TrendingUp size={20} className="mr-2 text-indigo-600" /> R\u00e9tention par cohorte
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b-2 border-gray-200">
                                    <th className="text-left py-2 px-3 text-gray-600">Semaine</th>
                                    <th className="text-center py-2 px-3 text-gray-600">Taille</th>
                                    <th className="text-center py-2 px-3 text-gray-600">J+1</th>
                                    <th className="text-center py-2 px-3 text-gray-600">J+7</th>
                                    <th className="text-center py-2 px-3 text-gray-600">J+14</th>
                                    <th className="text-center py-2 px-3 text-gray-600">J+30</th>
                                </tr>
                            </thead>
                            <tbody>
                                {retention.map((c, i) => (
                                    <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-2 px-3 font-medium text-gray-700">{c.cohortWeek}</td>
                                        <td className="py-2 px-3 text-center text-gray-600">{c.cohortSize}</td>
                                        {(['d1', 'd7', 'd14', 'd30'] as const).map(d => (
                                            <td key={d} className="py-2 px-3 text-center">
                                                <span className={`inline-block px-2 py-1 rounded font-bold text-xs ${retentionColor(c[d])}`}>
                                                    {c[d] !== null ? `${c[d]}%` : '\u2014'}
                                                </span>
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </Card>
            )}

            {/* ── ANALYTICS.3: Conversion Funnel ── */}
            {conversion && conversion.stages.length > 0 && (
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Target size={20} className="mr-2 text-rose-600" /> Entonnoir de conversion
                    </h3>
                    <div className="space-y-1">
                        {conversion.stages.map((s, i) => (
                            <FunnelBar
                                key={i}
                                stage={s.stage}
                                count={s.count}
                                rate={s.conversionRate}
                                maxCount={maxFunnelCount}
                            />
                        ))}
                    </div>
                </Card>
            )}

            {/* ── ANALYTICS.4: Virality ── */}
            {virality && (
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Share2 size={20} className="mr-2 text-teal-600" /> Viralit\u00e9 & K-factor
                    </h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="text-center p-4 bg-teal-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-teal-700">{virality.kFactor}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">K-factor</span>
                        </div>
                        <div className="text-center p-4 bg-blue-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-blue-600">{virality.challengesThisMonth}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">D\u00e9fis ce mois</span>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-purple-600">{virality.invitationsPerUser}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Invit./utilisateur</span>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl">
                            <span className="block text-3xl font-extrabold text-green-600">{virality.newUsersThisMonth}</span>
                            <span className="text-xs text-gray-500 font-bold uppercase">Nouveaux ce mois</span>
                        </div>
                    </div>
                </Card>
            )}

            {/* ── Notification Delivery Monitoring ── */}
            {notifStats && (
                <>
                    <Card>
                        <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                            <Bell size={20} className="mr-2 text-orange-600" /> Suivi des notifications
                        </h3>
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                            <div className="text-center p-4 bg-orange-50 rounded-xl">
                                <span className="block text-3xl font-extrabold text-orange-700">{notifStats.total24h}</span>
                                <span className="text-xs text-gray-500 font-bold uppercase">Envoyees (24h)</span>
                            </div>
                            <div className="text-center p-4 bg-green-50 rounded-xl">
                                <span className="block text-3xl font-extrabold text-green-600">
                                    {notifStats.total30d > 0
                                        ? `${((notifStats.byChannel.reduce((sum, c) => sum + c.deliveredCount, 0) / notifStats.total30d) * 100).toFixed(1)}%`
                                        : '0%'}
                                </span>
                                <span className="text-xs text-gray-500 font-bold uppercase">Taux de livraison (30j)</span>
                            </div>
                            <div className="text-center p-4 bg-red-50 rounded-xl">
                                <span className="block text-3xl font-extrabold text-red-600">
                                    {notifStats.total30d > 0
                                        ? `${((notifStats.byChannel.reduce((sum, c) => sum + c.failedCount, 0) / notifStats.total30d) * 100).toFixed(1)}%`
                                        : '0%'}
                                </span>
                                <span className="text-xs text-gray-500 font-bold uppercase">Taux d'echec (30j)</span>
                            </div>
                        </div>

                        {/* Channel breakdown table */}
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b-2 border-gray-200">
                                        <th className="text-left py-2 px-3 text-gray-600">Canal</th>
                                        <th className="text-center py-2 px-3 text-gray-600">Envoyees</th>
                                        <th className="text-center py-2 px-3 text-gray-600">Livrees</th>
                                        <th className="text-center py-2 px-3 text-gray-600">Echouees</th>
                                        <th className="text-center py-2 px-3 text-gray-600">Taux d'echec</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {notifStats.byChannel.map((ch, i) => {
                                        const channelLabel = ch.channel === 'in_app' ? 'In-App' : ch.channel === 'sms' ? 'SMS' : 'Push';
                                        return (
                                            <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                                                <td className="py-2 px-3 font-medium text-gray-700">{channelLabel}</td>
                                                <td className="py-2 px-3 text-center text-gray-600">{ch.sentCount}</td>
                                                <td className="py-2 px-3 text-center text-green-600 font-bold">{ch.deliveredCount}</td>
                                                <td className="py-2 px-3 text-center text-red-600 font-bold">{ch.failedCount}</td>
                                                <td className="py-2 px-3 text-center">
                                                    <span className={`inline-block px-2 py-1 rounded text-xs font-bold ${ch.failureRate > 5 ? 'bg-red-100 text-red-700' : ch.failureRate > 0 ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}`}>
                                                        {ch.failureRate}%
                                                    </span>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </Card>

                    {/* Top errors */}
                    {notifStats.topErrors.length > 0 && (
                        <Card>
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                                <AlertTriangle size={20} className="mr-2 text-red-500" /> Top 5 erreurs de notification
                            </h3>
                            <div className="space-y-2">
                                {notifStats.topErrors.map((err, i) => (
                                    <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                                        <span className="text-sm text-gray-700 flex-1 truncate mr-4">{err.error}</span>
                                        <span className="text-sm font-bold text-red-700 whitespace-nowrap">{err.count} fois</span>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    )}
                </>
            )}

            {/* ── Digest SMS Stats ── */}
            <Card>
                <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                    <Mail size={20} className="mr-2 text-blue-600" /> Digests SMS Hebdomadaires
                </h3>
                <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-xl">
                        <span className="block text-3xl font-extrabold text-blue-700">{digestStats?.totalAllTime ?? 0}</span>
                        <span className="text-xs text-gray-500 font-bold uppercase">Total envoy\u00e9s</span>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-xl">
                        <span className="block text-3xl font-extrabold text-green-600">{digestStats?.digestsThisWeek ?? 0}</span>
                        <span className="text-xs text-gray-500 font-bold uppercase">Cette semaine</span>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-xl">
                        <span className="block text-3xl font-extrabold text-gray-600">{digestStats?.digestsLastWeek ?? 0}</span>
                        <span className="text-xs text-gray-500 font-bold uppercase">Semaine derni\u00e8re</span>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-xl">
                        <span className="block text-3xl font-extrabold text-purple-600">{digestStats?.uniqueParentsReached ?? 0}</span>
                        <span className="text-xs text-gray-500 font-bold uppercase">Parents atteints</span>
                    </div>
                    <div className="text-center p-4 bg-amber-50 rounded-xl">
                        <span className="block text-3xl font-extrabold text-amber-600">{digestStats?.avgChildrenPerDigest ?? 0}</span>
                        <span className="text-xs text-gray-500 font-bold uppercase">Enfants/parent</span>
                    </div>
                </div>
            </Card>

            {/* ── Difficult Questions Table ── */}
            <div>
                <h3 className="font-bold text-lg text-gray-900 mb-4">
                    Questions Difficiles (Taux de r\u00e9ussite &lt; 50%)
                    {difficultQuestions.length > 0 && <span className="text-sm font-normal text-gray-500 ml-2">({difficultQuestions.length} question(s))</span>}
                </h3>
                {difficultQuestions.length === 0 ? (
                    <Card className="text-center py-8 text-gray-500">
                        Aucune question difficile d\u00e9tect\u00e9e, ou pas encore assez de donn\u00e9es.
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
