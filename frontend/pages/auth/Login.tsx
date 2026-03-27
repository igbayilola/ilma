import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/authStore';
import { UserRole } from '../../types';
import { Mail, Lock, Phone } from 'lucide-react';

const formatPhone = (value: string): string => {
  // Strip everything except digits and +
  let digits = value.replace(/[^\d+]/g, '');
  // Auto-prepend +229 if user starts with local number
  if (digits.match(/^(90|91|94|95|96|97)/)) {
    digits = '+229' + digits;
  }
  if (digits.startsWith('229') && !digits.startsWith('+')) {
    digits = '+' + digits;
  }
  // Format: +229 XX XX XX XX
  if (digits.startsWith('+229') && digits.length > 4) {
    const local = digits.slice(4);
    const parts = local.match(/.{1,2}/g) || [];
    return '+229 ' + parts.join(' ');
  }
  return digits;
};

const rawPhone = (value: string): string => {
  return value.replace(/[^\d+]/g, '');
};

const looksLikePhone = (value: string): boolean => {
  const stripped = value.replace(/[\s\-()]/g, '');
  return /^(\+?\d|9[0-7])/.test(stripped) && !/[a-zA-Z@]/.test(stripped);
};

export const LoginPage: React.FC = () => {
  const [identifier, setIdentifier] = useState(''); // Email or Phone (raw value for submission)
  const [displayIdentifier, setDisplayIdentifier] = useState(''); // Formatted display value
  const [isPhone, setIsPhone] = useState(false);
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier || !password) return;

    try {
        await login({ identifier, password });
        
        // Redirect logic
        const from = (location.state as any)?.from?.pathname;
        if (from) {
            navigate(from, { replace: true });
            return;
        }

        // Role based redirect if no history
        const user = useAuthStore.getState().user;
        const { activeProfile } = useAuthStore.getState();
        if (user?.role === UserRole.ADMIN) {
            navigate('/app/admin/dashboard');
        } else if (!activeProfile) {
            // No auto-selected profile → go to Netflix selector (PIN required, multiple profiles, or parent)
            navigate('/select-profile');
        } else {
            navigate('/app/student/dashboard');
        }

    } catch (e) {
        // Error is handled in store and displayed via `error` state
    }
  };

  return (
    <AuthLayout title="Bon retour !" subtitle="Connecte-toi pour continuer tes leçons." backLink="/">
      <form onSubmit={handleLogin} className="space-y-4">
        {error && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl font-medium flex items-center animate-slide-down">
                ⚠️ {error}
            </div>
        )}
        
        <Input
          label="Email ou Téléphone"
          placeholder="ex: leo@sitou.app ou +229 96 XX XX XX"
          leftIcon={isPhone ? <Phone size={18} /> : <Mail size={18} />}
          value={displayIdentifier}
          onChange={(e) => {
            const val = e.target.value;
            if (looksLikePhone(val)) {
              setIsPhone(true);
              const formatted = formatPhone(val);
              setDisplayIdentifier(formatted);
              setIdentifier(rawPhone(formatted));
            } else {
              setIsPhone(false);
              setDisplayIdentifier(val);
              setIdentifier(val);
            }
          }}
        />
        
        <div className="space-y-1">
            <Input 
            label="Mot de passe"
            type="password"
            placeholder="••••••••"
            leftIcon={<Lock size={18} />}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            />
            <div className="text-right">
                <Link to="/forgot-password" className="text-xs font-bold text-sitou-primary hover:underline">
                    Mot de passe oublié ?
                </Link>
            </div>
        </div>

        <Button fullWidth type="submit" isLoading={isLoading} className="mt-4">
          Se connecter
        </Button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Pas encore de compte ?{' '}
          <Link to="/register" className="font-bold text-sitou-primary hover:underline">
            S'inscrire
          </Link>
        </p>
      </div>


    </AuthLayout>
  );
};
