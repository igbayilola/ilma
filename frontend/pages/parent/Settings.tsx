import React, { useState } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Input } from '../../components/ui/Input';
import { Bell, Moon, Smartphone, Mail, VolumeX, AlertTriangle } from 'lucide-react';
import { ButtonVariant } from '../../types';

export const ParentSettingsPage: React.FC = () => {
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

            <div className="flex justify-end pt-4">
                <Button className="w-full md:w-auto">
                    Enregistrer les modifications
                </Button>
            </div>
        </div>
    );
};

