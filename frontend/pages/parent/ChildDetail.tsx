import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Card, Badge } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Tabs } from '../../components/ui/Tabs';
import { Skeleton } from '../../components/ui/Skeleton';
import { ButtonVariant } from '../../types';
import { ArrowLeft, Clock, CheckCircle2, XCircle, TrendingUp, AlertTriangle } from 'lucide-react';
import { parentService, ChildDTO } from '../../services/parentService';
import { progressService, SkillProgressDTO } from '../../services/progressService';

export const ChildDetailPage: React.FC = () => {
    const { childId } = useParams<{ childId: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('overview');
    const [child, setChild] = useState<ChildDTO | null>(null);
    const [skillProgress, setSkillProgress] = useState<SkillProgressDTO[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!childId) return;
        Promise.all([
            parentService.listChildren(),
            progressService.getStudentProgress(childId).catch(() => []),
        ]).then(([children, progress]) => {
            const found = children.find(c => c.id === childId);
            setChild(found || null);
            setSkillProgress(progress);
        }).catch(() => {})
          .finally(() => setIsLoading(false));
    }, [childId]);

    if (isLoading) {
        return (
            <div className="space-y-6">
                <Skeleton variant="text" className="w-64 h-8" />
                <Skeleton variant="rect" className="h-64" />
            </div>
        );
    }

    const strengths = skillProgress.filter(s => s.score >= 80).map(s => s.skillName);
    const weaknesses = skillProgress.filter(s => s.score > 0 && s.score < 50).map(s => s.skillName);

    return (
        <div className="space-y-6">
            <Link to="/app/parent/dashboard" className="inline-flex items-center gap-2 text-gray-500 hover:text-ilma-primary transition-colors mb-4">
              <ArrowLeft size={18} />
              <span className="text-sm font-medium">Retour au tableau de bord</span>
            </Link>
            <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center space-x-3">
                    <img src={child?.avatar || ''} className="w-12 h-12 rounded-full border border-gray-200" alt="Avatar"/>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{child?.name || 'Enfant'}</h1>
                        <p className="text-xs text-gray-500">Niveau {child?.level || 1}</p>
                    </div>
                </div>
                <div className="ml-auto">
                    <Button variant={ButtonVariant.SECONDARY} size="sm" onClick={() => navigate(`/app/parent/goals/${childId}`)}>
                        Objectifs
                    </Button>
                </div>
            </div>

            <Tabs
                tabs={[
                    { id: 'overview', label: "Vue d'ensemble" },
                    { id: 'history', label: 'Compétences' },
                    { id: 'weaknesses', label: 'Points clés' }
                ]}
                activeTab={activeTab}
                onChange={setActiveTab}
            />

            {activeTab === 'overview' && (
                <div className="space-y-6 animate-fade-in">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <Card className="md:col-span-2">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                                <Clock size={18} className="mr-2 text-ilma-primary" /> Progression par compétence
                            </h3>
                            {skillProgress.length === 0 ? (
                                <p className="text-gray-500 text-center py-8">Aucune donnée de progression.</p>
                            ) : (
                                <div className="space-y-3">
                                    {skillProgress.slice(0, 6).map(sp => (
                                        <div key={sp.skillId} className="flex items-center space-x-3">
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-800 truncate">{sp.skillName}</p>
                                            </div>
                                            <div className="w-24 bg-gray-100 h-2 rounded-full overflow-hidden">
                                                <div className="bg-ilma-primary h-full rounded-full" style={{ width: `${sp.score}%` }} />
                                            </div>
                                            <span className="text-sm font-bold text-gray-600 w-10 text-right">{sp.score}%</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </Card>

                        <div className="space-y-4">
                            <Card className="bg-green-50 border-green-100">
                                <h4 className="text-green-800 font-bold mb-1">Forces</h4>
                                <div className="flex flex-wrap gap-2">
                                    {strengths.length > 0 ? strengths.slice(0, 3).map(s => <Badge key={s} label={s} color="green" size="sm" />) : <span className="text-sm text-gray-500">--</span>}
                                </div>
                            </Card>
                            <Card className="bg-red-50 border-red-100">
                                <h4 className="text-red-800 font-bold mb-1">À renforcer</h4>
                                <div className="flex flex-wrap gap-2">
                                    {weaknesses.length > 0 ? weaknesses.slice(0, 3).map(s => <Badge key={s} label={s} color="red" size="sm" />) : <span className="text-sm text-gray-500">--</span>}
                                </div>
                            </Card>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'history' && (
                <div className="space-y-4 animate-fade-in">
                    {skillProgress.length === 0 ? (
                        <p className="text-center text-gray-500 py-12">Aucune donnée de compétences.</p>
                    ) : skillProgress.map((sp) => (
                        <Card key={sp.skillId} className="flex items-center p-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${sp.score >= 50 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                {sp.score >= 50 ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
                            </div>
                            <div className="flex-1">
                                <h4 className="font-bold text-gray-900">{sp.skillName}</h4>
                                <p className="text-xs text-gray-500">{sp.totalAttempts} tentative(s)</p>
                            </div>
                            <div className="text-right">
                                <span className={`font-bold text-lg ${sp.score >= 80 ? 'text-green-600' : sp.score >= 50 ? 'text-orange-500' : 'text-red-500'}`}>
                                    {sp.score}%
                                </span>
                            </div>
                        </Card>
                    ))}
                </div>
            )}

             {activeTab === 'weaknesses' && (
                <div className="animate-fade-in flex flex-col items-center justify-center py-12 text-center">
                    <div className="bg-yellow-50 p-6 rounded-full mb-4">
                        <AlertTriangle size={48} className="text-yellow-500" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Analyse détaillée</h3>
                    {weaknesses.length > 0 ? (
                        <p className="text-gray-500 max-w-md mt-2">
                            Votre enfant rencontre des difficultés en <span className="font-bold">{weaknesses.join(', ')}</span>.
                            Nous recommandons de revoir ces compétences ensemble.
                        </p>
                    ) : (
                        <p className="text-gray-500 max-w-md mt-2">
                            Pas encore assez de données pour une analyse détaillée.
                        </p>
                    )}
                    <Button className="mt-6" leftIcon={<TrendingUp size={18}/>}>
                        Voir les recommandations
                    </Button>
                </div>
            )}
        </div>
    );
};
