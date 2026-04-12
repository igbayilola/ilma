import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Input } from '../../components/ui/Input';
import { Bell, Moon, Smartphone, Mail, VolumeX, AlertTriangle, Trash2, Shield } from 'lucide-react';
import { ButtonVariant } from '../../types';
import { useAuthStore } from '../../store/authStore';
import { apiClient } from '../../services/apiClient';

export const ParentSettingsPage: React.FC = () => {
    const { user, logout } = useAuthStore();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    // Mock State
    const [settings, setSettings] = useState({
        pushEnabled: true,
        emailEnabled: true,
        smsEnabled: false,
        quietHoursEnabled: true,
        quietStart: '21:00',
        quietEnd: '07:00',
        alertInactivity: true,
        alertBadges: true,
        alertGoals: true
    });

    const update = (key: string, value: any) => {
        setSettings(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="space-y-6 max-w-2xl mx-auto">
            <header>
                <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2">Paramètres Famille</h1>
                <p className="text-gray-500">Gérez les notifications et le bien-être numérique.</p>
            </header>

            {/* Quiet Hours */}
            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-indigo-100 rounded-lg mr-3 text-indigo-600">
                        <Moon size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Heures Calmes</h2>
                        <p className="text-sm text-gray-500">Pendant ces heures, l'application ne sera pas accessible pour les enfants.</p>
                    </div>
                </div>

                <Toggle 
                    label="Activer le mode nuit" 
                    checked={settings.quietHoursEnabled} 
                    onChange={(v) => update('quietHoursEnabled', v)} 
                />

                {settings.quietHoursEnabled && (
                    <div className="grid grid-cols-2 gap-4 mt-4 animate-fade-in">
                        <Input 
                            type="time" 
                            label="Début" 
                            value={settings.quietStart} 
                            onChange={(e) => update('quietStart', e.target.value)}
                        />
                        <Input 
                            type="time" 
                            label="Fin" 
                            value={settings.quietEnd} 
                            onChange={(e) => update('quietEnd', e.target.value)}
                        />
                    </div>
                )}
            </Card>

            {/* Notifications Channels */}
            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-blue-100 rounded-lg mr-3 text-sitou-primary">
                        <Bell size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Canaux de notification</h2>
                        <p className="text-sm text-gray-500">Comment souhaitez-vous être informé ?</p>
                    </div>
                </div>

                <div className="space-y-1">
                    <Toggle 
                        label="Notifications Push" 
                        description="Sur votre téléphone"
                        checked={settings.pushEnabled} 
                        onChange={(v) => update('pushEnabled', v)} 
                    />
                    <Toggle 
                        label="Email" 
                        description="Récapitulatifs hebdomadaires"
                        checked={settings.emailEnabled} 
                        onChange={(v) => update('emailEnabled', v)} 
                    />
                    <Toggle 
                        label="SMS" 
                        description="Alertes critiques uniquement"
                        checked={settings.smsEnabled} 
                        onChange={(v) => update('smsEnabled', v)} 
                    />
                </div>
            </Card>

             {/* Alerts Configuration */}
             <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-orange-100 rounded-lg mr-3 text-orange-600">
                        <AlertTriangle size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Types d'alertes</h2>
                        <p className="text-sm text-gray-500">Choisissez les événements importants.</p>
                    </div>
                </div>

                <div className="space-y-1">
                    <Toggle 
                        label="Inactivité prolongée" 
                        description="Si l'enfant ne se connecte pas pendant 3 jours"
                        checked={settings.alertInactivity} 
                        onChange={(v) => update('alertInactivity', v)} 
                    />
                    <Toggle 
                        label="Nouveaux Badges" 
                        description="Quand un enfant débloque une réussite"
                        checked={settings.alertBadges} 
                        onChange={(v) => update('alertBadges', v)} 
                    />
                     <Toggle 
                        label="Objectifs atteints" 
                        checked={settings.alertGoals} 
                        onChange={(v) => update('alertGoals', v)} 
                    />
                </div>
            </Card>

            {/* Legal */}
            <Card>
                <div className="flex items-center mb-4">
                    <div className="p-2 bg-green-100 rounded-lg mr-3 text-green-600">
                        <Shield size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Données personnelles</h2>
                    </div>
                </div>
                <Link
                    to="/legal/privacy"
                    className="text-sm text-sitou-primary underline"
                >
                    Consulter la politique de confidentialité
                </Link>
            </Card>

            {/* Delete Account */}
            <Card>
                <div className="flex items-center mb-4">
                    <div className="p-2 bg-red-100 rounded-lg mr-3 text-red-600">
                        <Trash2 size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Supprimer mon compte</h2>
                        <p className="text-sm text-gray-500">Cette action est irréversible. Toutes les données seront supprimées après 30 jours.</p>
                    </div>
                </div>

                {!showDeleteConfirm ? (
                    <Button
                        variant={'outline' as ButtonVariant}
                        className="text-red-600 border-red-300 hover:bg-red-50 w-full"
                        onClick={() => setShowDeleteConfirm(true)}
                    >
                        Supprimer mon compte et mes données
                    </Button>
                ) : (
                    <div className="space-y-3 p-4 bg-red-50 rounded-xl">
                        <p className="text-sm font-medium text-red-800">
                            Confirmez-vous la suppression de votre compte et de tous les profils enfants associés ?
                        </p>
                        <div className="flex gap-3">
                            <Button
                                variant={'outline' as ButtonVariant}
                                className="flex-1"
                                onClick={() => setShowDeleteConfirm(false)}
                            >
                                Annuler
                            </Button>
                            <Button
                                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                                isLoading={isDeleting}
                                onClick={async () => {
                                    setIsDeleting(true);
                                    try {
                                        await apiClient.delete(`/auth/me`);
                                        logout();
                                    } catch {
                                        setIsDeleting(false);
                                        setShowDeleteConfirm(false);
                                    }
                                }}
                            >
                                Confirmer la suppression
                            </Button>
                        </div>
                    </div>
                )}
            </Card>

            <div className="flex justify-end pt-4">
                <Button className="w-full md:w-auto">
                    Enregistrer les modifications
                </Button>
            </div>
        </div>
    );
};

