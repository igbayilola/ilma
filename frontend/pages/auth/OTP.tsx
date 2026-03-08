import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { Button } from '../../components/ui/Button';
import { ButtonVariant, UserRole } from '../../types';
import { useAuthStore } from '../../store/authStore';
import { apiClient } from '../../services/apiClient';
import { CheckCircle2 } from 'lucide-react';

export const OTPPage: React.FC = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [timer, setTimer] = useState(60);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [attempts, setAttempts] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuthStore();

  const identifier = (location.state as any)?.identifier || 'votre compte';
  const usePhone = (location.state as any)?.usePhone ?? true;
  const maskedIdentifier = identifier.length > 4
    ? identifier.slice(0, 3) + '***' + identifier.slice(-2)
    : identifier;

  useEffect(() => {
    const interval = setInterval(() => {
      setTimer(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (value: string, index: number) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);
    setError('');

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pastedData.length === 6) {
      setOtp(pastedData.split(''));
      inputRefs.current[5]?.focus();
    }
  };

  const handleResend = async () => {
    setTimer(60);
    setOtp(['', '', '', '', '', '']);
    setError('');
    setAttempts(0);
    inputRefs.current[0]?.focus();
    if (usePhone && identifier) {
      try {
        await apiClient.post('/auth/otp/send', { phone: identifier });
      } catch {
        // Silently fail — timer restarted regardless
      }
    }
  };

  const handleVerify = async () => {
    const code = otp.join('');
    if (code.length < 6) return;

    if (attempts >= 3) {
      setError('Trop de tentatives. Renvoie un nouveau code.');
      return;
    }

    setIsLoading(true);
    setAttempts(prev => prev + 1);

    try {
      if (usePhone) {
        // Verify OTP via backend
        await apiClient.post('/auth/otp/verify', { phone: identifier, code });
      }
      // After OTP verified, login normally
      await login({ identifier, password: (location.state as any)?.password || '' });
      navigate('/app/student/dashboard', { replace: true });
    } catch (err: any) {
      const msg = err?.message || 'Code incorrect ou expiré.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const otpFilled = otp.every(d => d !== '');
  const formatTimer = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

  return (
    <AuthLayout
      title="Vérification"
      subtitle={`Entre le code à 6 chiffres envoyé ${usePhone ? 'par SMS' : 'par email'} à ${maskedIdentifier}.`}
      backLink="/register"
    >
      {error && (
        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl font-medium mb-4 animate-slide-down">
          {error}
        </div>
      )}

      <div className="flex justify-center gap-2 mb-2" onPaste={handlePaste}>
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={el => { inputRefs.current[index] = el; }}
            className={`w-10 h-12 md:w-12 md:h-14 border-2 rounded-xl text-center text-xl font-bold transition-colors focus:outline-none
              ${digit ? 'border-ilma-primary bg-ilma-primary-light/30' : 'border-gray-200'}
              ${error ? 'border-red-300 bg-red-50' : ''}
              focus:border-ilma-primary focus:ring-2 focus:ring-ilma-primary-light`}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={e => handleChange(e.target.value, index)}
            onKeyDown={e => handleKeyDown(e, index)}
            aria-label={`Chiffre ${index + 1}`}
          />
        ))}
      </div>

      {attempts > 0 && attempts < 3 && (
        <p className="text-xs text-gray-400 text-center mb-4">
          {3 - attempts} tentative{3 - attempts > 1 ? 's' : ''} restante{3 - attempts > 1 ? 's' : ''}
        </p>
      )}

      <Button
        fullWidth
        onClick={handleVerify}
        isLoading={isLoading}
        disabled={!otpFilled || attempts >= 3}
        className="mt-4"
        leftIcon={<CheckCircle2 size={18} />}
      >
        Vérifier
      </Button>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500 mb-2">Pas reçu le code ?</p>
        {timer > 0 ? (
          <span className="text-sm font-medium text-gray-400">
            Renvoyer dans {formatTimer(timer)}
          </span>
        ) : (
          <button
            onClick={handleResend}
            className="text-sm font-bold text-ilma-primary hover:underline"
          >
            Renvoyer le code
          </button>
        )}
      </div>
    </AuthLayout>
  );
};
