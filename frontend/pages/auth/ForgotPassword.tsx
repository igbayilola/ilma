import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { ButtonVariant } from '../../types';
import { apiClient } from '../../services/apiClient';
import { Mail, Lock, ArrowLeft, CheckCircle2 } from 'lucide-react';

type Step = 'email' | 'otp' | 'new-password' | 'done';

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [timer, setTimer] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (timer <= 0) return;
    const t = setTimeout(() => setTimer(timer - 1), 1000);
    return () => clearTimeout(t);
  }, [timer]);

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    setIsLoading(true);
    setError('');
    try {
      await apiClient.post('/auth/otp/send', { phone_or_email: email.trim() });
      setStep('otp');
      setTimer(60);
    } catch (err: any) {
      setError(err.message || 'Impossible d\'envoyer le code.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);
    if (value && index < 5) inputRefs.current[index + 1]?.focus();
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join('');
    if (code.length !== 6) return;
    setIsLoading(true);
    setError('');
    try {
      await apiClient.post('/auth/otp/verify', { phone_or_email: email.trim(), code });
      setStep('new-password');
    } catch (err: any) {
      setError(err.message || 'Code invalide.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      await apiClient.post('/auth/password/reset', { email: email.trim(), new_password: newPassword });
      setStep('done');
    } catch (err: any) {
      setError(err.message || 'Impossible de réinitialiser le mot de passe.');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'done') {
    return (
      <AuthLayout title="Mot de passe modifie" backTo="/login">
        <div className="text-center py-8 space-y-4">
          <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle2 className="text-green-600 w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-gray-800">Mot de passe reinitialise !</h2>
          <p className="text-sm text-gray-500">Tu peux maintenant te connecter avec ton nouveau mot de passe.</p>
          <Button fullWidth onClick={() => navigate('/login')}>Se connecter</Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Mot de passe oublie" backTo="/login">
      <div className="space-y-6">
        {step === 'email' && (
          <form onSubmit={handleSendOTP} className="space-y-4">
            <p className="text-sm text-gray-500">Entre ton adresse e-mail pour recevoir un code de verification.</p>
            <Input
              label="Adresse e-mail"
              type="email"
              placeholder="ton.email@exemple.com"
              leftIcon={<Mail size={18} />}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {error && <p className="text-sm text-red-600 font-medium">{error}</p>}
            <Button fullWidth type="submit" isLoading={isLoading}>Envoyer le code</Button>
            <div className="text-center">
              <Link to="/login" className="text-sm text-sitou-primary font-bold hover:underline inline-flex items-center gap-1">
                <ArrowLeft size={14} /> Retour a la connexion
              </Link>
            </div>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleVerifyOTP} className="space-y-4">
            <p className="text-sm text-gray-500">Un code a 6 chiffres a ete envoye a <b>{email}</b>.</p>
            <div className="flex justify-center gap-2">
              {otp.map((digit, i) => (
                <input
                  key={i}
                  ref={(el) => { inputRefs.current[i] = el; }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(i, e.target.value)}
                  onKeyDown={(e) => handleOtpKeyDown(i, e)}
                  className="w-12 h-14 text-center text-2xl font-black rounded-xl border-2 border-gray-200 focus:border-sitou-primary focus:ring-2 focus:ring-amber-200 outline-none transition-all"
                />
              ))}
            </div>
            {error && <p className="text-sm text-red-600 font-medium text-center">{error}</p>}
            <Button fullWidth type="submit" isLoading={isLoading} disabled={otp.join('').length !== 6}>
              Verifier
            </Button>
            <div className="text-center">
              {timer > 0 ? (
                <p className="text-xs text-gray-400">Renvoyer dans {timer}s</p>
              ) : (
                <button type="button" onClick={handleSendOTP} className="text-xs text-sitou-primary font-bold hover:underline">
                  Renvoyer le code
                </button>
              )}
            </div>
          </form>
        )}

        {step === 'new-password' && (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <p className="text-sm text-gray-500">Choisis ton nouveau mot de passe (8 caracteres minimum).</p>
            <Input
              label="Nouveau mot de passe"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock size={18} />}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <Input
              label="Confirmer le mot de passe"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock size={18} />}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
            {error && <p className="text-sm text-red-600 font-medium">{error}</p>}
            <Button fullWidth type="submit" isLoading={isLoading}>Reinitialiser</Button>
          </form>
        )}
      </div>
    </AuthLayout>
  );
};
