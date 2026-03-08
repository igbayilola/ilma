import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { CheckoutModal } from '../../components/subscription/CheckoutModal';
import { Plan, ButtonVariant, Profile, SubscriptionTier } from '../../types';
import { Check, Star, Crown, ShieldCheck, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../services/apiClient';
import { useAuthStore } from '../../store/authStore';

const FALLBACK_PLANS: Plan[] = [
    {
        id: 'monthly',
        name: 'Mensuel',
        price: 2500,
        durationLabel: 'mois',
        features: ['Accès illimité', 'Mode hors-ligne', 'Suivi standard'],
        isPopular: false
    },
    {
        id: 'quarterly',
        name: 'Trimestriel',
        price: 6000,
        durationLabel: '3 mois',
        features: ['Accès illimité', 'Mode hors-ligne', 'Examens blancs', 'Économisez 20%'],
        isPopular: true
    },
    {
        id: 'annual',
        name: 'Annuel',
        price: 20000,
        durationLabel: 'an',
        features: ['Tout illimité', 'Priorité support', 'Badges exclusifs', 'Meilleure offre'],
        isPopular: false
    },
    {
        id: 'family',
        name: 'Famille',
        price: 30000,
        durationLabel: 'an',
        features: ['Jusqu\'à 4 enfants inclus', 'Soit 625 F/enfant/mois', 'Tableau de bord parents', 'Contrôle parental'],
        isPopular: false
    }
];

function durationLabel(days: number): string {
    if (days <= 31) return 'mois';
    if (days <= 100) return '3 mois';
    return 'an';
}

function mapBackendPlan(p: any, index: number): Plan {
    const featureList = p.features
        ? (Array.isArray(p.features) ? p.features : Object.values(p.features))
        : ['Accès illimité'];
    return {
        id: String(p.id),
        name: p.name,
        price: p.price_xof,
        durationLabel: durationLabel(p.duration_days),
        features: featureList as string[],
        isPopular: index === 1, // Second plan is "popular"
    };
}

export const PlansPage: React.FC = () => {
    const navigate = useNavigate();
    const { profiles, activeProfile, selectProfile } = useAuthStore();
    const [plans, setPlans] = useState<Plan[]>(FALLBACK_PLANS);
    const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
    const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
    const [selectedBeneficiaryId, setSelectedBeneficiaryId] = useState<string>(activeProfile?.id || '');

    // Non-premium profiles that can benefit from an upgrade
    const beneficiaryProfiles = profiles.filter(p => p.isActive && p.subscriptionTier !== SubscriptionTier.PREMIUM);

    useEffect(() => {
        apiClient.get<any[]>('/subscriptions/plans')
            .then((data) => {
                if (data && data.length > 0) {
                    setPlans(data.map(mapBackendPlan));
                }
            })
            .catch(() => {
                // Keep fallback plans on error
            });
    }, []);

    // Auto-select first beneficiary if none selected
    useEffect(() => {
        if (!selectedBeneficiaryId && beneficiaryProfiles.length > 0) {
            setSelectedBeneficiaryId(beneficiaryProfiles[0].id);
        }
    }, [beneficiaryProfiles, selectedBeneficiaryId]);

    const handleSelectPlan = (plan: Plan) => {
        // Temporarily select the beneficiary profile so CheckoutModal sends the right profile_id
        if (selectedBeneficiaryId && selectedBeneficiaryId !== activeProfile?.id) {
            selectProfile(selectedBeneficiaryId);
        }
        setSelectedPlan(plan);
        setIsCheckoutOpen(true);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 pb-10">
            <header className="text-center space-y-4 py-8">
                <div className="inline-block p-3 bg-yellow-100 rounded-full mb-2 animate-bounce-in">
                    <Crown size={32} className="text-yellow-600" />
                </div>
                <h1 className="text-3xl md:text-5xl font-extrabold text-gray-900">Devenez Premium</h1>
                <p className="text-xl text-gray-500 max-w-2xl mx-auto">
                    Débloquez tout le potentiel de ILMA. Apprenez sans limites, même sans internet.
                </p>
            </header>

            {/* Profile beneficiary selector for parents with multiple profiles */}
            {beneficiaryProfiles.length > 1 && (
                <div className="max-w-md mx-auto bg-white rounded-2xl border border-gray-200 p-4">
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                        <User size={16} className="inline mr-1.5 -mt-0.5" />
                        Abonnement pour
                    </label>
                    <div className="flex gap-3 flex-wrap justify-center">
                        {beneficiaryProfiles.map(p => (
                            <button
                                key={p.id}
                                type="button"
                                onClick={() => setSelectedBeneficiaryId(p.id)}
                                className={`flex flex-col items-center p-3 rounded-xl border-2 transition-all min-w-[80px] ${
                                    selectedBeneficiaryId === p.id
                                        ? 'border-ilma-primary bg-amber-50'
                                        : 'border-gray-100 hover:border-amber-200'
                                }`}
                            >
                                <img
                                    src={p.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${p.id}`}
                                    alt={p.displayName}
                                    className="w-10 h-10 rounded-full mb-1"
                                />
                                <span className={`text-xs font-bold ${selectedBeneficiaryId === p.id ? 'text-ilma-primary' : 'text-gray-600'}`}>
                                    {p.displayName}
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {plans.map((plan) => (
                    <Card
                        key={plan.id}
                        className={`clay-card relative flex flex-col p-6 border-2 transition-transform hover:-translate-y-2 duration-300 ${
                            plan.isPopular ? 'border-ilma-primary shadow-2xl scale-105 z-10' : 'border-gray-100'
                        }`}
                    >
                        {plan.isPopular && (
                            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-ilma-primary text-white text-xs font-bold px-4 py-1.5 rounded-full shadow-lg">
                                PLUS POPULAIRE
                            </div>
                        )}

                        <div className="mb-6 text-center">
                            <h3 className="text-lg font-bold text-gray-600 mb-2">{plan.name}</h3>
                            <div className="flex items-baseline justify-center">
                                <span className="text-3xl font-extrabold text-gray-900">{plan.price.toLocaleString()}</span>
                                <span className="text-gray-500 font-medium ml-1">F</span>
                            </div>
                            <p className="text-sm text-gray-400">/ {plan.durationLabel}</p>
                        </div>

                        <ul className="space-y-3 mb-8 flex-1">
                            {plan.features.map((feat, i) => (
                                <li key={i} className="flex items-start text-sm text-gray-600">
                                    <Check size={16} className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                                    <span>{feat}</span>
                                </li>
                            ))}
                        </ul>

                        <Button 
                            fullWidth 
                            variant={plan.isPopular ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY}
                            onClick={() => handleSelectPlan(plan)}
                            className={plan.isPopular ? 'bg-gradient-to-r from-amber-600 to-ilma-primary shadow-lg shadow-amber-500/30' : ''}
                        >
                            Choisir ce plan
                        </Button>
                    </Card>
                ))}
            </div>

            {/* Feature Comparison Table */}
            <div className="mt-12 overflow-x-auto -mx-4 px-4">
                <table className="w-full min-w-[600px] text-sm border-collapse">
                    <thead>
                        <tr className="border-b-2 border-gray-200">
                            <th className="py-3 px-4 text-left font-bold text-gray-700">Fonctionnalité</th>
                            {plans.map(p => (
                                <th key={p.id} className={`py-3 px-4 text-center font-bold ${p.isPopular ? 'text-ilma-primary' : 'text-gray-700'}`}>
                                    {p.name}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {[
                            { label: 'Exercices / jour', values: (p: Plan) => p.id === 'monthly' || p.id === 'quarterly' || p.id === 'annual' || p.id === 'family' ? 'Illimités' : '5' },
                            { label: 'Mode hors-ligne', values: (p: Plan) => p.features.some(f => f.toLowerCase().includes('hors-ligne')) ? '✓' : '—' },
                            { label: 'Micro-leçons', values: () => '✓' },
                            { label: 'Suivi parental', values: (p: Plan) => p.features.some(f => f.toLowerCase().includes('parent')) ? '✓' : '—' },
                            { label: 'Nombre d\'enfants', values: (p: Plan) => p.id === 'family' ? 'Jusqu\'à 4' : '1' },
                            { label: 'Examens blancs', values: (p: Plan) => p.features.some(f => f.toLowerCase().includes('examen')) ? '✓' : '—' },
                        ].map((row, i) => (
                            <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : ''}>
                                <td className="py-3 px-4 font-medium text-gray-700">{row.label}</td>
                                {plans.map(p => (
                                    <td key={p.id} className="py-3 px-4 text-center text-gray-600">
                                        {row.values(p)}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-12 text-center bg-gray-50 rounded-3xl p-8 border border-gray-100">
                <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-8">
                    <div className="flex items-center text-gray-600">
                        <ShieldCheck size={20} className="text-green-500 mr-2" />
                        Paiement 100% Sécurisé
                    </div>
                    <div className="flex items-center text-gray-600">
                        <Star size={20} className="text-yellow-500 mr-2" />
                        Satisfait ou remboursé
                    </div>
                </div>
            </div>

            <div className="text-center">
                 <Button variant={ButtonVariant.GHOST} onClick={() => navigate(-1)}>
                     Non merci, continuer avec la version gratuite
                 </Button>
            </div>

            <CheckoutModal 
                isOpen={isCheckoutOpen} 
                onClose={() => setIsCheckoutOpen(false)} 
                plan={selectedPlan} 
            />
        </div>
    );
};