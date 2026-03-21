import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Input } from '../../components/ui/Input';
import { Save, Shield, Server, Coins, Check, AlertCircle, Loader2, Tag, Crosshair, Award } from 'lucide-react';
import { ButtonVariant } from '../../types';
import { apiClient } from '../../services/apiClient';

interface ConfigEntry {
    value: any;
    category: string;
    label: string;
    description: string;
    value_type: string;
}

type GroupedConfig = Record<string, Record<string, ConfigEntry>>;

const CATEGORY_META: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
    system: { label: 'Accès & Système', icon: <Shield size={20} />, color: 'text-ilma-primary' },
    subscription: { label: 'Monétisation', icon: <Coins size={20} />, color: 'text-yellow-600' },
    scoring: { label: 'Scoring (SmartScore)', icon: <Crosshair size={20} />, color: 'text-blue-600' },
    badges: { label: 'Badges', icon: <Award size={20} />, color: 'text-purple-600' },
    anti_cheat: { label: 'Anti-Triche', icon: <Shield size={20} />, color: 'text-red-600' },
    registration: { label: 'Inscription', icon: <Server size={20} />, color: 'text-green-600' },
    marketing: { label: 'Marketing', icon: <Tag size={20} />, color: 'text-pink-600' },
};

export const AdminConfigPage: React.FC = () => {
    const [grouped, setGrouped] = useState<GroupedConfig>({});
    const [editedValues, setEditedValues] = useState<Record<string, any>>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await apiClient.get<GroupedConfig>('/admin/config');
            setGrouped(data);
            // Initialize edited values from current values
            const initial: Record<string, any> = {};
            for (const entries of Object.values(data)) {
                for (const [key, entry] of Object.entries(entries)) {
                    initial[key] = entry.value;
                }
            }
            setEditedValues(initial);
        } catch (err: any) {
            setError('Impossible de charger la configuration');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (key: string, value: any) => {
        setEditedValues(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = async () => {
        setSaving(true);
        setError('');
        try {
            await apiClient.put('/admin/config/bulk', editedValues);
            setSaveMessage('Configuration sauvegardée');
            // Reload to get fresh data
            await loadConfig();
        } catch (err: any) {
            setError(err?.message || 'Erreur lors de la sauvegarde');
        } finally {
            setSaving(false);
            setTimeout(() => setSaveMessage(''), 3000);
        }
    };

    const renderInput = (key: string, entry: ConfigEntry) => {
        const value = editedValues[key] ?? entry.value;
        const vtype = entry.value_type;

        if (vtype === 'bool') {
            return (
                <Toggle
                    label={entry.label}
                    description={entry.description}
                    checked={value === true || value === 'true'}
                    onChange={(v) => handleChange(key, v)}
                />
            );
        }

        if (vtype === 'int') {
            return (
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">{entry.label}</label>
                    {entry.description && <p className="text-xs text-gray-400 mb-2">{entry.description}</p>}
                    <input
                        type="number"
                        value={value}
                        onChange={(e) => handleChange(key, parseInt(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-ilma-primary/20 focus:border-ilma-primary"
                    />
                </div>
            );
        }

        if (vtype === 'float') {
            return (
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">{entry.label}</label>
                    {entry.description && <p className="text-xs text-gray-400 mb-2">{entry.description}</p>}
                    <input
                        type="number"
                        step="0.01"
                        value={value}
                        onChange={(e) => handleChange(key, parseFloat(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-ilma-primary/20 focus:border-ilma-primary"
                    />
                </div>
            );
        }

        if (vtype === 'json') {
            const display = typeof value === 'string' ? value : JSON.stringify(value);
            return (
                <div>
                    <label className="block text-sm font-bold text-gray-700 mb-1">{entry.label}</label>
                    {entry.description && <p className="text-xs text-gray-400 mb-2">{entry.description}</p>}
                    <textarea
                        value={display}
                        onChange={(e) => {
                            try {
                                handleChange(key, JSON.parse(e.target.value));
                            } catch {
                                // Keep raw string while user is typing
                                handleChange(key, e.target.value);
                            }
                        }}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono focus:ring-2 focus:ring-ilma-primary/20 focus:border-ilma-primary"
                    />
                </div>
            );
        }

        // Default: string
        return (
            <Input
                label={entry.label}
                value={typeof value === 'string' ? value : String(value)}
                onChange={(e) => handleChange(key, e.target.value)}
            />
        );
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <Loader2 size={32} className="animate-spin text-ilma-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Configuration Système</h1>
                    <p className="text-gray-500 text-sm">Paramètres globaux de l'application.</p>
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

            {error && (
                <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl font-medium flex items-center gap-2">
                    <AlertCircle size={16} /> {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(grouped).map(([category, entries]) => {
                    const meta = CATEGORY_META[category] || { label: category, icon: <Server size={20} />, color: 'text-gray-600' };
                    return (
                        <Card key={category}>
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                                <span className={`mr-2 ${meta.color}`}>{meta.icon}</span> {meta.label}
                            </h3>
                            <div className="space-y-4">
                                {Object.entries(entries).map(([key, entry]) => (
                                    <div key={key}>
                                        {renderInput(key, entry)}
                                    </div>
                                ))}
                            </div>
                        </Card>
                    );
                })}
            </div>

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
    );
};
