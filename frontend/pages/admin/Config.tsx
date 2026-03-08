import React, { useState } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Input } from '../../components/ui/Input';
import { Save, Shield, Server, Coins, Check } from 'lucide-react';
import { ButtonVariant } from '../../types';
import { apiClient } from '../../services/apiClient';

const defaultConfig = {
    maintenanceMode: false,
    registrationOpen: true,
    freemiumLimit: 5,
    priceMonthly: 2500,
    promoCode: 'ILMA2024',
    minAppVersion: '1.0.5'
};

export const AdminConfigPage: React.FC = () => {
    const [config, setConfig] = useState(() => {
        const saved = localStorage.getItem('ilma_admin_config');
        return saved ? JSON.parse(saved) : defaultConfig;
    });
    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');

    const handleChange = (key: string, val: any) => {
        setConfig((prev: typeof defaultConfig) => ({ ...prev, [key]: val }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Try backend first
            await apiClient.put('/admin/config', config);
            setSaveMessage('Configuration sauvegardee');
        } catch {
            // Fallback: save to localStorage
            localStorage.setItem('ilma_admin_config', JSON.stringify(config));
            setSaveMessage('Configuration sauvegardee localement');
        } finally {
            setSaving(false);
            setTimeout(() => setSaveMessage(''), 3000);
        }
    };

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
             <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Configuration Système</h1>
                    <p className="text-gray-500 text-sm">Paramètres globaux et Feature Flags.</p>
                </div>
                <div className="flex items-center gap-3">
                    {saveMessage && (
                        <span className="text-sm text-green-600 flex items-center gap-1">
                            <Check size={16} /> {saveMessage}
                        </span>
                    )}
                    <Button leftIcon={<Save size={18}/>} onClick={handleSave} disabled={saving}>
                        {saving ? 'Sauvegarde...' : 'Sauvegarder'}
                    </Button>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Shield size={20} className="mr-2 text-ilma-primary" /> Accès & Sécurité
                    </h3>
                    <div className="space-y-2">
                         <Toggle 
                            label="Mode Maintenance" 
                            description="Bloque l'accès à tous les utilisateurs non-admin"
                            checked={config.maintenanceMode} 
                            onChange={(v) => handleChange('maintenanceMode', v)} 
                        />
                         <Toggle 
                            label="Inscriptions Ouvertes" 
                            checked={config.registrationOpen} 
                            onChange={(v) => handleChange('registrationOpen', v)} 
                        />
                         <Input 
                            label="Version Min. App"
                            value={config.minAppVersion}
                            onChange={(e) => handleChange('minAppVersion', e.target.value)}
                            className="mt-4"
                        />
                    </div>
                </Card>

                <Card>
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Coins size={20} className="mr-2 text-yellow-600" /> Monétisation
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-2">Limite Freemium (Exercices/jour)</label>
                            <div className="flex items-center space-x-2">
                                <input 
                                    type="range" min="1" max="10" step="1" 
                                    value={config.freemiumLimit}
                                    onChange={(e) => handleChange('freemiumLimit', parseInt(e.target.value))}
                                    className="flex-1"
                                />
                                <span className="font-bold w-8 text-center">{config.freemiumLimit}</span>
                            </div>
                        </div>

                        <Input 
                            label="Prix Mensuel (FCFA)"
                            type="number"
                            value={config.priceMonthly}
                            onChange={(e) => handleChange('priceMonthly', e.target.value)}
                        />

                         <Input 
                            label="Code Promo Global"
                            value={config.promoCode}
                            onChange={(e) => handleChange('promoCode', e.target.value)}
                        />
                    </div>
                </Card>

                <Card className="md:col-span-2">
                     <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                        <Server size={20} className="mr-2 text-gray-600" /> Cache & Données
                    </h3>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <div>
                            <span className="block font-bold text-gray-700">Vider le cache CDN</span>
                            <span className="text-xs text-gray-500">Force le re-téléchargement des assets pour tous les utilisateurs</span>
                        </div>
                        <Button variant={ButtonVariant.SECONDARY} size="sm">Purge Cache</Button>
                    </div>
                </Card>
            </div>
        </div>
    );
};