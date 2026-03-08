import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { ButtonVariant } from '../../types';
import { useNavigate } from 'react-router-dom';
import { Lock, Star, CheckCircle2, Zap, MessageSquare, Loader2 } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { apiClient } from '../../services/apiClient';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PaywallModal: React.FC<PaywallModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { user, activeProfile, profiles } = useAuthStore();
  const isChildProfile = user?.role === 'parent' && activeProfile;
  const [parentNotifState, setParentNotifState] = useState<'idle' | 'sending' | 'sent' | 'no-parent'>('idle');

  const handleUpgrade = () => {
    onClose();
    navigate('/app/subscription/plans');
  };

  const handleSendToParent = async () => {
    setParentNotifState('sending');
    try {
      const displayName = activeProfile?.displayName || user?.name || 'Votre enfant';
      await apiClient.post('/notifications', {
        type: 'SUBSCRIPTION_REQUEST',
        title: 'Demande d\'abonnement',
        message: `${displayName} a terminé ses exercices gratuits. Abonnez-vous pour continuer l'apprentissage.`,
        channel: 'sms',
      });
      setParentNotifState('sent');
    } catch {
      // If no parent linked or notification fails
      setParentNotifState('no-parent');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="">
      <div className="text-center">
        <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6 relative animate-bounce-in">
          <Lock size={40} className="text-yellow-600" />
          <div className="absolute -top-1 -right-1 bg-ilma-primary text-white rounded-full p-1.5 border-2 border-white">
             <Star size={12} fill="currentColor" />
          </div>
        </div>

        <h2 className="text-2xl font-extrabold text-gray-900 mb-2">Limite quotidienne atteinte</h2>
        <p className="text-gray-500 mb-6">
          Tu as terminé tes <span className="font-bold text-gray-800">5 exercices gratuits</span> pour aujourd'hui. Reviens demain ou passe à la vitesse supérieure !
        </p>

        <div className="bg-gray-50 rounded-2xl p-4 mb-6 text-left border border-gray-100">
            <h4 className="font-bold text-gray-700 mb-3 flex items-center">
                <Zap size={16} className="mr-2 text-ilma-orange fill-current" /> Avec Premium :
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center"><CheckCircle2 size={16} className="text-green-500 mr-2"/> Exercices illimités</li>
                <li className="flex items-center"><CheckCircle2 size={16} className="text-green-500 mr-2"/> Accès à toutes les matières</li>
                <li className="flex items-center"><CheckCircle2 size={16} className="text-green-500 mr-2"/> Mode hors-ligne complet</li>
                <li className="flex items-center"><CheckCircle2 size={16} className="text-green-500 mr-2"/> Examens blancs</li>
            </ul>
        </div>

        <div className="space-y-3">
            <Button fullWidth onClick={handleUpgrade} className="bg-gradient-to-r from-ilma-orange to-yellow-500 border-none shadow-lg shadow-yellow-500/30">
                Débloquer l'illimité
            </Button>
            {!isChildProfile && parentNotifState === 'idle' && (
              <button
                onClick={handleSendToParent}
                className="w-full py-3 text-sm font-medium text-ilma-primary hover:bg-ilma-primary-light rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <MessageSquare size={16} />
                Envoyer à mes parents
              </button>
            )}
            {parentNotifState === 'sending' && (
              <div className="w-full py-3 text-sm text-gray-400 flex items-center justify-center gap-2">
                <Loader2 size={16} className="animate-spin" />
                Envoi en cours...
              </div>
            )}
            {parentNotifState === 'sent' && (
              <div className="w-full py-3 text-sm text-green-600 font-medium flex items-center justify-center gap-2">
                <CheckCircle2 size={16} />
                Message envoyé à tes parents !
              </div>
            )}
            {parentNotifState === 'no-parent' && (
              <div className="w-full py-3 text-sm text-amber-600 font-medium text-center">
                Demande à un adulte de t'abonner sur la page des plans.
              </div>
            )}
            <Button fullWidth variant={ButtonVariant.GHOST} onClick={onClose}>
                Revenir à l'accueil
            </Button>
        </div>
      </div>
    </Modal>
  );
};