import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Button } from '../../components/ui/Button';
import { Toggle } from '../../components/ui/Toggle';
import { Input } from '../../components/ui/Input';
import { Bell, Clock, Flame, Trophy, FileText, ArrowLeft, Save, Sun, Moon, Monitor, Volume2, Wifi, Smartphone } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ButtonVariant } from '../../types';
import { useThemeStore } from '../../store/themeStore';
import { pushService } from '../../services/pushService';

export const StudentSettingsPage: React.FC = () => {
    const navigate = useNavigate();
    const { theme, setTheme } = useThemeStore();

    // Mock State
    const [prefs, setPrefs] = useState({
        streakAlerts: true,
        badgeAlerts: true,
        reportAlerts: false,
        dailyReminder: true,
        reminderTime: '17:00'
    });

    // Data saver mode
    const [dataSaver, setDataSaver] = useState(() => localStorage.getItem('sitou_data_saver') === 'true');

    const toggleDataSaver = () => {
      const newValue = !dataSaver;
      setDataSaver(newValue);
      localStorage.setItem('sitou_data_saver', String(newValue));
      document.documentElement.classList.toggle('data-saver', newValue);
    };

    // Sound feedback
    const [soundEnabled, setSoundEnabled] = useState(() => localStorage.getItem('sitou_sound') !== 'false');

    const toggleSound = () => {
      const newValue = !soundEnabled;
      setSoundEnabled(newValue);
      localStorage.setItem('sitou_sound', String(newValue));
    };

    // Push notification state
    const [pushSupported] = useState(() => pushService.isSupported());
    const [pushEnabled, setPushEnabled] = useState(() => pushService.isSubscribed());
    const [pushLoading, setPushLoading] = useState(false);

    const togglePush = async () => {
        setPushLoading(true);
        try {
            if (pushEnabled) {
                await pushService.unsubscribe();
                setPushEnabled(false);
            } else {
                const ok = await pushService.subscribe();
                setPushEnabled(ok);
            }
        } finally {
            setPushLoading(false);
        }
    };

    const update = (key: string, value: any) => {
        setPrefs(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        // Mock save
        navigate(-1);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <header className="flex items-center space-x-4">
                <button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-100 rounded-full">
                    <ArrowLeft size={24} className="text-gray-600" />
                </button>
                <div>
                    <h1 className="text-2xl font-extrabold text-gray-900">Préférences</h1>
                    <p className="text-gray-500 text-sm">Gère tes notifications et rappels.</p>
                </div>
            </header>

            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-amber-100 rounded-lg mr-3 text-sitou-primary">
                        <Bell size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Notifications</h2>
                        <p className="text-sm text-gray-500">Choisis ce que tu veux recevoir.</p>
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="flex items-center py-2">
                        <Flame size={20} className="text-sitou-orange mr-3" />
                        <div className="flex-1">
                             <Toggle 
                                label="Série en danger" 
                                description="Alerte quand tu risques de perdre ta série"
                                checked={prefs.streakAlerts} 
                                onChange={(v) => update('streakAlerts', v)} 
                            />
                        </div>
                    </div>
                    <div className="flex items-center py-2">
                        <Trophy size={20} className="text-yellow-500 mr-3" />
                        <div className="flex-1">
                             <Toggle 
                                label="Nouveaux Badges" 
                                description="Quand tu débloques une récompense"
                                checked={prefs.badgeAlerts} 
                                onChange={(v) => update('badgeAlerts', v)} 
                            />
                        </div>
                    </div>
                    <div className="flex items-center py-2">
                        <FileText size={20} className="text-blue-500 mr-3" />
                        <div className="flex-1">
                             <Toggle 
                                label="Bilan Hebdo" 
                                description="Résumé de tes progrès chaque semaine"
                                checked={prefs.reportAlerts} 
                                onChange={(v) => update('reportAlerts', v)} 
                            />
                        </div>
                    </div>
                </div>
            </Card>

            {/* Push Notifications */}
            {pushSupported && (
                <Card>
                    <div className="flex items-center mb-6">
                        <div className="p-2 bg-blue-100 rounded-lg mr-3 text-blue-600">
                            <Smartphone size={24} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">Notifications Push</h2>
                            <p className="text-sm text-gray-500">Reçois des alertes même quand l'app est fermée.</p>
                        </div>
                    </div>
                    <label className="flex items-center justify-between cursor-pointer">
                        <span className="text-sm font-medium text-gray-700">
                            {pushLoading ? 'Activation...' : pushEnabled ? 'Notifications activées' : 'Activer les notifications'}
                        </span>
                        <button
                            role="switch"
                            aria-checked={pushEnabled}
                            onClick={togglePush}
                            disabled={pushLoading}
                            className={`relative w-12 h-7 rounded-full transition-colors ${pushEnabled ? 'bg-sitou-primary' : 'bg-gray-300'} ${pushLoading ? 'opacity-50' : ''}`}
                        >
                            <span className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform ${pushEnabled ? 'translate-x-5' : ''}`} />
                        </button>
                    </label>
                </Card>
            )}

            <Card>
                 <div className="flex items-center mb-6">
                    <div className="p-2 bg-green-100 rounded-lg mr-3 text-green-600">
                        <Clock size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Rappels quotidiens</h2>
                        <p className="text-sm text-gray-500">Pour ne pas oublier de t'entraîner.</p>
                    </div>
                </div>

                <Toggle 
                    label="Activer le rappel" 
                    checked={prefs.dailyReminder} 
                    onChange={(v) => update('dailyReminder', v)} 
                />

                {prefs.dailyReminder && (
                    <div className="mt-4 animate-slide-down">
                        <Input 
                            type="time" 
                            label="Heure du rappel" 
                            value={prefs.reminderTime} 
                            onChange={(e) => update('reminderTime', e.target.value)}
                        />
                         <p className="text-xs text-gray-400 mt-2">
                            Les notifications sont automatiquement désactivées entre 21h et 7h (Mode calme).
                        </p>
                    </div>
                )}
            </Card>

            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-purple-100 rounded-lg mr-3 text-purple-600 dark:bg-purple-900 dark:text-purple-300">
                        <Moon size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Apparence</h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Choisis le thème de l'application.</p>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                    {([
                        { value: 'light' as const, label: 'Clair', icon: <Sun size={20} /> },
                        { value: 'dark' as const, label: 'Sombre', icon: <Moon size={20} /> },
                        { value: 'system' as const, label: 'Système', icon: <Monitor size={20} /> },
                    ]).map((opt) => (
                        <button
                            key={opt.value}
                            onClick={() => setTheme(opt.value)}
                            className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-colors ${
                                theme === opt.value
                                    ? 'border-sitou-primary bg-sitou-primary-light dark:bg-amber-900/30 text-sitou-primary'
                                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 text-gray-600 dark:text-gray-400'
                            }`}
                        >
                            {opt.icon}
                            <span className="text-sm font-medium">{opt.label}</span>
                        </button>
                    ))}
                </div>
            </Card>

            {/* Data Saver */}
            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-blue-100 rounded-lg mr-3 text-blue-600">
                        <Wifi size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Économie de données</h2>
                        <p className="text-sm text-gray-500">Réduit la consommation de données en désactivant les images non essentielles et les animations.</p>
                    </div>
                </div>
                <label className="flex items-center justify-between cursor-pointer">
                    <span className="text-sm font-medium text-gray-700">Mode économie</span>
                    <button
                      role="switch"
                      aria-checked={dataSaver}
                      onClick={toggleDataSaver}
                      className={`relative w-12 h-7 rounded-full transition-colors ${dataSaver ? 'bg-sitou-primary' : 'bg-gray-300'}`}
                    >
                      <span className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform ${dataSaver ? 'translate-x-5' : ''}`} />
                    </button>
                </label>
            </Card>

            {/* Sound Feedback */}
            <Card>
                <div className="flex items-center mb-6">
                    <div className="p-2 bg-pink-100 rounded-lg mr-3 text-pink-600">
                        <Volume2 size={24} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">Sons</h2>
                        <p className="text-sm text-gray-500">Joue un son lors des bonnes et mauvaises réponses.</p>
                    </div>
                </div>
                <label className="flex items-center justify-between cursor-pointer">
                    <span className="text-sm font-medium text-gray-700">Activer les sons</span>
                    <button
                      role="switch"
                      aria-checked={soundEnabled}
                      onClick={toggleSound}
                      className={`relative w-12 h-7 rounded-full transition-colors ${soundEnabled ? 'bg-sitou-primary' : 'bg-gray-300'}`}
                    >
                      <span className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full shadow transition-transform ${soundEnabled ? 'translate-x-5' : ''}`} />
                    </button>
                </label>
            </Card>

            <div className="flex justify-end pt-4">
                <Button onClick={handleSave} leftIcon={<Save size={18}/>}>
                    Enregistrer
                </Button>
            </div>
        </div>
    );
};