import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { ButtonVariant, Profile, UserRole } from '../../types';
import { profileService } from '../../services/profileService';
import { Plus, Lock, LayoutDashboard } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { Skeleton } from '../../components/ui/Skeleton';

export const ProfileSelectorPage: React.FC = () => {
    const navigate = useNavigate();
    const { user, profiles, setProfiles, selectProfile } = useAuthStore();
    const [isLoading, setIsLoading] = useState(true);
    const [pinModal, setPinModal] = useState<Profile | null>(null);
    const [pin, setPin] = useState('');
    const [pinError, setPinError] = useState('');

    useEffect(() => {
        profileService.listProfiles()
            .then((fetchedProfiles) => {
                setProfiles(fetchedProfiles);
            })
            .catch(() => {})
            .finally(() => setIsLoading(false));
    }, [setProfiles]);

    const handleSelectProfile = async (profile: Profile) => {
        if (profile.hasPin) {
            setPinModal(profile);
            setPin('');
            setPinError('');
            return;
        }
        selectProfile(profile.id);
        navigate('/app/student/dashboard');
    };

    const handlePinSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!pinModal) return;
        const valid = await profileService.verifyPin(pinModal.id, pin);
        if (valid) {
            selectProfile(pinModal.id);
            setPinModal(null);
            navigate('/app/student/dashboard');
        } else {
            setPinError('Code PIN incorrect');
        }
    };

    const handleParentDashboard = () => {
        navigate('/app/parent/dashboard');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-sitou-surface flex items-center justify-center p-8">
                <div className="text-center space-y-6">
                    <Skeleton variant="text" className="w-48 h-8 mx-auto" />
                    <div className="flex gap-6 justify-center">
                        {[1, 2, 3].map(i => (
                            <Skeleton key={i} variant="rect" className="w-32 h-40 rounded-2xl" />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-sitou-surface flex flex-col items-center justify-center p-8">
            <div className="text-center max-w-2xl mx-auto">
                <div className="w-14 h-14 gradient-hero rounded-2xl flex items-center justify-center text-white font-bold text-2xl mx-auto mb-6 shadow-lg">
                    I
                </div>
                <h1 className="text-3xl font-extrabold text-gray-900 mb-2">
                    Qui utilise Sitou ?
                </h1>
                <p className="text-gray-500 mb-10">
                    Sélectionnez un profil pour commencer.
                </p>

                <div className="flex flex-wrap gap-6 justify-center mb-10">
                    {profiles.filter(p => p.isActive).map((profile) => (
                        <button
                            key={profile.id}
                            onClick={() => handleSelectProfile(profile)}
                            className="group flex flex-col items-center w-32 transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-sitou-primary focus:ring-offset-2 rounded-2xl p-2"
                        >
                            <div className="relative mb-3">
                                <img
                                    src={profile.avatarUrl}
                                    alt={profile.displayName}
                                    className="w-24 h-24 rounded-full object-cover border-4 border-transparent group-hover:border-sitou-primary transition-colors shadow-lg"
                                />
                                {profile.hasPin && (
                                    <div className="absolute bottom-0 right-0 bg-gray-700 text-white rounded-full p-1.5 border-2 border-white">
                                        <Lock size={12} />
                                    </div>
                                )}
                            </div>
                            <span className="font-bold text-gray-800 text-sm group-hover:text-sitou-primary transition-colors">
                                {profile.displayName}
                            </span>
                            <span className="text-[10px] text-gray-400 uppercase font-bold mt-0.5">
                                {profile.subscriptionTier === 'PREMIUM' ? 'Premium' : 'Gratuit'}
                            </span>
                        </button>
                    ))}

                    {/* Parent Dashboard tile */}
                    {user?.role === UserRole.PARENT && (
                        <button
                            onClick={handleParentDashboard}
                            className="group flex flex-col items-center w-32 transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-sitou-primary focus:ring-offset-2 rounded-2xl p-2"
                        >
                            <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center mb-3 group-hover:bg-blue-200 transition-colors shadow-lg">
                                <LayoutDashboard size={32} className="text-blue-600" />
                            </div>
                            <span className="font-bold text-gray-800 text-sm group-hover:text-blue-600 transition-colors">
                                Parents
                            </span>
                            <span className="text-[10px] text-gray-400 uppercase font-bold mt-0.5">
                                Dashboard
                            </span>
                        </button>
                    )}

                    {/* Add profile tile */}
                    <button
                        onClick={() => navigate('/select-profile/create')}
                        className="group flex flex-col items-center w-32 transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-sitou-primary focus:ring-offset-2 rounded-2xl p-2"
                    >
                        <div className="w-24 h-24 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center mb-3 group-hover:border-sitou-primary group-hover:bg-amber-50 transition-colors">
                            <Plus size={32} className="text-gray-400 group-hover:text-sitou-primary" />
                        </div>
                        <span className="font-bold text-gray-500 text-sm group-hover:text-sitou-primary transition-colors">
                            Ajouter
                        </span>
                    </button>
                </div>

                <Button
                    variant={ButtonVariant.GHOST}
                    onClick={() => useAuthStore.getState().logout()}
                    className="text-gray-400 hover:text-red-500"
                >
                    Déconnexion
                </Button>
            </div>

            {/* PIN verification modal */}
            <Modal
                isOpen={!!pinModal}
                onClose={() => setPinModal(null)}
                title={`Profil de ${pinModal?.displayName}`}
            >
                <form onSubmit={handlePinSubmit} className="space-y-4">
                    <div className="text-center mb-4">
                        <img
                            src={pinModal?.avatarUrl}
                            alt={pinModal?.displayName}
                            className="w-20 h-20 rounded-full mx-auto mb-3 shadow-lg"
                        />
                        <p className="text-sm text-gray-500">
                            Entrez le code PIN à 4 chiffres.
                        </p>
                    </div>
                    <Input
                        type="password"
                        inputMode="numeric"
                        maxLength={4}
                        placeholder="● ● ● ●"
                        value={pin}
                        onChange={e => { setPin(e.target.value.replace(/\D/g, '').slice(0, 4)); setPinError(''); }}
                        error={pinError || undefined}
                        className="text-center text-2xl tracking-[0.5em] font-mono"
                        autoFocus
                    />
                    <Button fullWidth type="submit" disabled={pin.length !== 4}>
                        Valider
                    </Button>
                </form>
            </Modal>
        </div>
    );
};
