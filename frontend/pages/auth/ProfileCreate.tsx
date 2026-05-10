import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { profileService } from '../../services/profileService';
import { contentService, GradeLevelDTO } from '../../services/contentService';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { ButtonVariant } from '../../types';
import { ArrowLeft, GraduationCap, Lock } from 'lucide-react';
import { avatarUrl as buildAvatarUrl } from '../../utils/avatar';

const AVATAR_SEEDS = [
    'Aisha', 'Kofi', 'Amina', 'Yao', 'Fatou',
    'Kwame', 'Adjoa', 'Moussa', 'Awa', 'Ibrahim',
    'Nana', 'Oumar',
];

export const ProfileCreatePage: React.FC = () => {
    const navigate = useNavigate();
    const { setProfiles } = useAuthStore();
    const [name, setName] = useState('');
    const [selectedAvatar, setSelectedAvatar] = useState(AVATAR_SEEDS[0]);
    const [gradeLevelId, setGradeLevelId] = useState('');
    const [gradeLevels, setGradeLevels] = useState<GradeLevelDTO[]>([]);
    const [usePin, setUsePin] = useState(false);
    const [pin, setPin] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        contentService.listGradeLevels().then(setGradeLevels).catch(() => {});
    }, []);

    const avatarUrl = buildAvatarUrl(selectedAvatar);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setIsSubmitting(true);
        setError('');

        try {
            await profileService.createProfile({
                displayName: name.trim(),
                avatarUrl,
                pin: usePin && pin.length === 4 ? pin : undefined,
                gradeLevelId: gradeLevelId || undefined,
            });

            // Refresh profiles list
            const profiles = await profileService.listProfiles();
            setProfiles(profiles);

            navigate('/select-profile');
        } catch (err: any) {
            setError(err.message || 'Erreur lors de la création du profil');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-sitou-surface flex items-center justify-center p-6">
            <div className="w-full max-w-md">
                <button
                    onClick={() => navigate('/select-profile')}
                    className="flex items-center text-gray-500 hover:text-gray-800 mb-6 transition-colors"
                >
                    <ArrowLeft size={20} className="mr-2" />
                    Retour
                </button>

                <div className="bg-white rounded-3xl shadow-xl p-8">
                    <h1 className="text-2xl font-extrabold text-gray-900 mb-2">
                        Nouveau profil
                    </h1>
                    <p className="text-gray-500 text-sm mb-6">
                        Créez un profil pour votre enfant.
                    </p>

                    {error && (
                        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl font-medium mb-4">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Avatar picker */}
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3">
                                Avatar
                            </label>
                            <div className="flex items-center gap-4 mb-3">
                                <img
                                    src={avatarUrl}
                                    alt="Avatar sélectionné"
                                    loading="eager"
                                    decoding="async"
                                    width={80}
                                    height={80}
                                    className="w-20 h-20 rounded-full border-4 border-sitou-primary shadow-lg"
                                />
                                <div className="flex-1">
                                    <div className="flex flex-wrap gap-2">
                                        {AVATAR_SEEDS.map((seed) => (
                                            <button
                                                key={seed}
                                                type="button"
                                                onClick={() => setSelectedAvatar(seed)}
                                                className={`w-10 h-10 rounded-full border-2 transition-all ${
                                                    selectedAvatar === seed
                                                        ? 'border-sitou-primary scale-110'
                                                        : 'border-transparent hover:border-gray-300'
                                                }`}
                                            >
                                                <img
                                                    src={buildAvatarUrl(seed)}
                                                    alt={seed}
                                                    loading="lazy"
                                                    decoding="async"
                                                    width={40}
                                                    height={40}
                                                    className="w-full h-full rounded-full"
                                                />
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <Input
                            label="Prénom de l'enfant"
                            placeholder="ex: Aïcha"
                            value={name}
                            onChange={e => setName(e.target.value)}
                            required
                        />

                        {/* Grade level */}
                        {gradeLevels.length > 0 && (
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1.5">
                                    <GraduationCap size={16} className="inline mr-1.5 -mt-0.5" />
                                    Classe
                                </label>
                                <select
                                    value={gradeLevelId}
                                    onChange={e => setGradeLevelId(e.target.value)}
                                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-sitou-primary/20 focus:border-sitou-primary text-sm bg-white"
                                >
                                    <option value="">— Choisir la classe —</option>
                                    {gradeLevels.map(g => (
                                        <option key={g.id} value={g.id}>{g.name}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {/* PIN toggle */}
                        <div className="bg-gray-50 rounded-xl p-4">
                            <label className="flex items-center justify-between cursor-pointer">
                                <div className="flex items-center">
                                    <Lock size={18} className="text-gray-400 mr-3" />
                                    <div>
                                        <span className="font-bold text-sm text-gray-700">Code PIN</span>
                                        <p className="text-xs text-gray-400">Protection par code à 4 chiffres</p>
                                    </div>
                                </div>
                                <input
                                    type="checkbox"
                                    checked={usePin}
                                    onChange={e => { setUsePin(e.target.checked); if (!e.target.checked) setPin(''); }}
                                    className="w-5 h-5 accent-sitou-primary"
                                />
                            </label>
                            {usePin && (
                                <div className="mt-3">
                                    <Input
                                        type="password"
                                        inputMode="numeric"
                                        maxLength={4}
                                        placeholder="● ● ● ●"
                                        value={pin}
                                        onChange={e => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                                        className="text-center text-xl tracking-[0.5em] font-mono"
                                    />
                                </div>
                            )}
                        </div>

                        <div className="pt-2 space-y-3">
                            <Button
                                fullWidth
                                type="submit"
                                isLoading={isSubmitting}
                                disabled={!name.trim() || (usePin && pin.length !== 4)}
                            >
                                Créer le profil
                            </Button>
                            <Button
                                fullWidth
                                variant={ButtonVariant.GHOST}
                                onClick={() => navigate('/select-profile')}
                            >
                                Annuler
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
