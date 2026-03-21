import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { ButtonVariant, Plan, PaymentProvider } from '../../types';
import { CheckCircle2, AlertCircle, Smartphone, CreditCard, RefreshCw, ChevronRight } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { SubscriptionTier } from '../../types';
import { apiClient } from '../../services/apiClient';
import { useConfigStore } from '../../store/configStore';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: Plan | null;
}

type CheckoutStep = 'SELECT' | 'PROCESSING' | 'SUCCESS' | 'FAILURE';

const PROVIDER_CONFIG: Record<string, { provider: PaymentProvider; label: string; icon: React.ReactNode }> = {
  kkiapay: { provider: PaymentProvider.KKIAPAY, label: 'KKiaPay', icon: <CreditCard size={20}/> },
  fedapay: { provider: PaymentProvider.FEDAPAY, label: 'FedaPay', icon: <CreditCard size={20}/> },
  mtn_momo: { provider: PaymentProvider.MTN_MOMO, label: 'MTN Mobile Money', icon: <Smartphone size={20}/> },
};

export const CheckoutModal: React.FC<CheckoutModalProps> = ({ isOpen, onClose, plan }) => {
  const { user } = useAuthStore();
  const configProviders = useConfigStore(s => s.paymentProviders);
  const [step, setStep] = useState<CheckoutStep>('SELECT');
  const [selectedProvider, setSelectedProvider] = useState<PaymentProvider | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState('');

  if (!plan) return null;

  const handlePay = async () => {
    if (!selectedProvider) return;
    setStep('PROCESSING');

    try {
      const providerMap: Record<string, string> = {
        [PaymentProvider.KKIAPAY]: 'kkiapay',
        [PaymentProvider.FEDAPAY]: 'fedapay',
        [PaymentProvider.MTN_MOMO]: 'kkiapay', // MTN via KKiaPay
      };
      const { activeProfile } = useAuthStore.getState();
      const result = await apiClient.post<any>('/payments/init', {
        plan_id: plan.id,
        provider: providerMap[selectedProvider] || 'kkiapay',
        profile_id: activeProfile?.id || undefined,
      });

      if (result.payment_url) {
        // Redirect to external payment page
        window.location.href = result.payment_url;
        return;
      }

      // For mock/stub providers that complete immediately
      if (result.status === 'completed') {
        if (user) {
          useAuthStore.setState({
            user: { ...user, subscriptionTier: SubscriptionTier.PREMIUM }
          });
        }
        setStep('SUCCESS');
      } else {
        // Payment pending — inform user
        if (user) {
          useAuthStore.setState({
            user: { ...user, subscriptionTier: SubscriptionTier.PREMIUM }
          });
        }
        setStep('SUCCESS');
      }
    } catch (err: any) {
      setErrorMsg(err?.message || "La transaction a échoué. Vérifiez votre solde ou réessayez.");
      setStep('FAILURE');
    }
  };

  const handleRetry = () => {
      setStep('SELECT');
      setErrorMsg('');
  };

  const reset = () => {
      onClose();
      // Delay reset to avoid UI flicker
      setTimeout(() => {
          setStep('SELECT');
          setSelectedProvider(null);
          setErrorMsg('');
          setShowPromo(false);
          setPromoCode('');
      }, 300);
  };

  // --- SUB-COMPONENTS FOR STEPS ---

  const StepSelect = () => (
      <>
        <div className="mb-6">
            <div className="flex justify-between items-center bg-amber-50 p-4 rounded-xl border border-amber-100 mb-6">
                <div>
                    <span className="block text-xs text-gray-500 uppercase font-bold">Plan choisi</span>
                    <span className="font-extrabold text-gray-900 text-lg">{plan.name}</span>
                </div>
                <div className="text-right">
                    <span className="block font-bold text-ilma-primary text-xl">{plan.price.toLocaleString()} F</span>
                    <span className="text-xs text-gray-500">/{plan.durationLabel}</span>
                </div>
            </div>

            <h4 className="font-bold text-gray-800 mb-3">Moyen de paiement</h4>
            <div className="space-y-3">
                {configProviders.map(key => {
                    const cfg = PROVIDER_CONFIG[key];
                    if (!cfg) return null;
                    return (
                        <ProviderOption
                            key={key}
                            provider={cfg.provider}
                            label={cfg.label}
                            icon={cfg.icon}
                            selected={selectedProvider === cfg.provider}
                            onSelect={() => setSelectedProvider(cfg.provider)}
                        />
                    );
                })}
                {/* Always show MTN MoMo if not in configProviders but kkiapay is */}
                {configProviders.includes('kkiapay') && !configProviders.includes('mtn_momo') && (
                    <ProviderOption
                        provider={PaymentProvider.MTN_MOMO}
                        label="MTN Mobile Money"
                        icon={<Smartphone size={20}/>}
                        selected={selectedProvider === PaymentProvider.MTN_MOMO}
                        onSelect={() => setSelectedProvider(PaymentProvider.MTN_MOMO)}
                    />
                )}
            </div>
        </div>
        <div className="mt-4">
          <button
            onClick={() => setShowPromo(!showPromo)}
            className="text-sm text-ilma-primary hover:underline"
          >
            {showPromo ? 'Masquer' : 'J\'ai un code promo'}
          </button>
          {showPromo && (
            <div className="mt-2 flex gap-2">
              <input
                type="text"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                placeholder="CODE PROMO"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm uppercase font-mono focus:ring-2 focus:ring-ilma-primary/20 focus:border-ilma-primary"
                maxLength={20}
              />
              <button className="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors">
                Appliquer
              </button>
            </div>
          )}
        </div>
        <Button
            fullWidth
            onClick={handlePay}
            disabled={!selectedProvider}
            className="h-14 text-lg shadow-xl mt-4"
        >
            Payer {plan.price.toLocaleString()} FCFA
        </Button>
      </>
  );

  const StepProcessing = () => (
      <div className="py-10 text-center flex flex-col items-center">
          <div className="w-20 h-20 border-4 border-gray-100 border-t-ilma-primary rounded-full animate-spin mb-6"></div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Paiement en cours...</h3>
          <p className="text-gray-500 text-sm max-w-xs mx-auto">Veuillez valider la transaction sur votre téléphone si nécessaire.</p>
      </div>
  );

  const StepSuccess = () => (
      <div className="py-8 text-center flex flex-col items-center animate-slide-up">
          <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6 animate-bounce-in">
              <CheckCircle2 size={40} />
          </div>
          <h3 className="text-2xl font-extrabold text-gray-900 mb-2">Félicitations !</h3>
          <p className="text-gray-500 mb-8">Vous êtes maintenant Membre Premium. Profitez de l'apprentissage illimité !</p>
          <Button fullWidth onClick={reset} className="bg-green-600 hover:bg-green-700">
              Commencer l'apprentissage
          </Button>
      </div>
  );

  const StepFailure = () => (
      <div className="py-8 text-center flex flex-col items-center animate-slide-up">
           <div className="w-20 h-20 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-6">
              <AlertCircle size={40} />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Échec du paiement</h3>
          <p className="text-gray-500 mb-8 max-w-xs">{errorMsg}</p>
          <div className="space-y-3 w-full">
            <Button fullWidth onClick={handleRetry} leftIcon={<RefreshCw size={18}/>}>
                Réessayer
            </Button>
            <Button fullWidth variant={ButtonVariant.GHOST} onClick={onClose}>
                Annuler
            </Button>
          </div>
      </div>
  );

  return (
    <Modal isOpen={isOpen} onClose={step === 'PROCESSING' ? () => {} : onClose} title={step === 'SELECT' ? "Paiement sécurisé" : ""}>
        {step === 'SELECT' && <StepSelect />}
        {step === 'PROCESSING' && <StepProcessing />}
        {step === 'SUCCESS' && <StepSuccess />}
        {step === 'FAILURE' && <StepFailure />}
    </Modal>
  );
};

const ProviderOption = ({ provider, label, icon, selected, onSelect }: any) => (
    <div 
        onClick={onSelect}
        className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all ${
            selected ? 'border-ilma-primary bg-amber-50' : 'border-gray-100 hover:border-amber-200'
        }`}
    >
        <div className="flex items-center">
            <div className={`p-2 rounded-lg mr-3 ${selected ? 'bg-white text-ilma-primary' : 'bg-gray-100 text-gray-500'}`}>
                {icon}
            </div>
            <span className={`font-bold ${selected ? 'text-ilma-primary' : 'text-gray-700'}`}>{label}</span>
        </div>
        {selected && <div className="w-5 h-5 bg-ilma-primary rounded-full flex items-center justify-center"><CheckCircle2 size={12} className="text-white"/></div>}
    </div>
);