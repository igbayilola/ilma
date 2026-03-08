import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../store/authStore';
import { User, ShieldCheck, Mail, Lock, Phone, GraduationCap } from 'lucide-react';
import { ButtonVariant } from '../../types';
import { contentService, GradeLevelDTO } from '../../services/contentService';

type RegRole = 'student' | 'parent';

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

const validatePhone = (phone: string): string | null => {
  const cleaned = phone.replace(/\s/g, '');
  if (!cleaned) return null;
  const regex = /^\+229(90|91|94|95|96|97)\d{6}$/;
  if (!regex.test(cleaned)) return 'Format: +229XXXXXXXX (préfixes 90-97)';
  return null;
};

const validatePassword = (pw: string): string | null => {
  if (pw.length < 8) return 'Minimum 8 caractères';
  if (!/[A-Z]/.test(pw)) return 'Au moins 1 majuscule';
  if (!/\d/.test(pw)) return 'Au moins 1 chiffre';
  if (!/[^a-zA-Z0-9]/.test(pw)) return 'Au moins 1 caractère spécial';
  return null;
};

const validateEmail = (email: string): string | null => {
  if (!email) return null;
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!regex.test(email)) return 'Email invalide';
  return null;
};

export const RegisterPage: React.FC = () => {
  const [role, setRole] = useState<RegRole>('student');
  const [usePhone, setUsePhone] = useState(true);
  const [formData, setFormData] = useState({ name: '', identifier: '', password: '', confirmPassword: '' });
  const [selectedGradeId, setSelectedGradeId] = useState('');
  const [gradeLevels, setGradeLevels] = useState<GradeLevelDTO[]>([]);
  const [displayIdentifier, setDisplayIdentifier] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const { register, isLoading, error: apiError } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    contentService.listGradeLevels().then(setGradeLevels).catch(() => {});
  }, []);

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!formData.name.trim()) errs.name = 'Nom requis';
    if (!formData.identifier.trim()) {
      errs.identifier = usePhone ? 'Téléphone requis' : 'Email requis';
    } else if (usePhone) {
      const phoneErr = validatePhone(formData.identifier);
      if (phoneErr) errs.identifier = phoneErr;
    } else {
      const emailErr = validateEmail(formData.identifier);
      if (emailErr) errs.identifier = emailErr;
    }
    const pwErr = validatePassword(formData.password);
    if (pwErr) errs.password = pwErr;
    if (formData.password !== formData.confirmPassword) errs.confirmPassword = 'Les mots de passe ne correspondent pas';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleBlur = (field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    validate();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ name: true, identifier: true, password: true, confirmPassword: true });
    if (!validate()) return;

    try {
      await register({
        email: usePhone ? '' : formData.identifier,
        phone: usePhone ? formData.identifier : '',
        password: formData.password,
        name: formData.name,
        role: role,
        gradeLevelId: role === 'student' && selectedGradeId ? selectedGradeId : undefined,
      });
      navigate('/otp', { state: { identifier: formData.identifier, usePhone, password: formData.password } });
    } catch {
      // Error handled in store
    }
  };

  const passwordStrength = (() => {
    const pw = formData.password;
    if (!pw) return 0;
    let s = 0;
    if (pw.length >= 8) s++;
    if (/[A-Z]/.test(pw)) s++;
    if (/\d/.test(pw)) s++;
    if (/[^a-zA-Z0-9]/.test(pw)) s++;
    return s;
  })();

  const strengthColors = ['bg-gray-200', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-ilma-green'];
  const strengthLabels = ['', 'Faible', 'Moyen', 'Bon', 'Fort'];

  return (
    <AuthLayout title="Créer un compte" subtitle="Rejoins l'aventure ILMA." backLink="/">

      {/* Role Switcher */}
      <div className="flex bg-gray-100 p-1 rounded-xl mb-6">
        <button
          type="button"
          className={`flex-1 flex items-center justify-center py-2.5 rounded-lg text-sm font-bold transition-all ${role === 'student' ? 'bg-white shadow-sm text-ilma-primary' : 'text-gray-500'}`}
          onClick={() => setRole('student')}
        >
          <User size={16} className="mr-2" /> Élève
        </button>
        <button
          type="button"
          className={`flex-1 flex items-center justify-center py-2.5 rounded-lg text-sm font-bold transition-all ${role === 'parent' ? 'bg-white shadow-sm text-ilma-primary' : 'text-gray-500'}`}
          onClick={() => setRole('parent')}
        >
          <ShieldCheck size={16} className="mr-2" /> Parent
        </button>
      </div>

      {/* Grade level selector for students only (parents add children's grades via profiles) */}
      {role === 'student' && gradeLevels.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm font-bold text-gray-700 mb-1.5">
            <GraduationCap size={16} className="inline mr-1.5 -mt-0.5" />
            Classe
          </label>
          <select
            value={selectedGradeId}
            onChange={e => setSelectedGradeId(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-ilma-primary/20 focus:border-ilma-primary text-sm bg-white"
          >
            <option value="">— Choisir ta classe —</option>
            {gradeLevels.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
          </select>
        </div>
      )}

      {role === 'parent' && (
        <div className="mb-4 p-3 bg-blue-50 rounded-xl">
          <p className="text-xs text-blue-700 leading-relaxed">
            Vous pourrez ajouter des profils pour vos enfants (avec leur classe et avatar) après l'inscription.
          </p>
        </div>
      )}

      {apiError && (
        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-xl font-medium mb-4 animate-slide-down">
          {apiError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Nom complet"
          placeholder={role === 'student' ? "Ton prénom" : "Votre nom"}
          value={formData.name}
          onChange={e => setFormData({...formData, name: e.target.value})}
          onBlur={() => handleBlur('name')}
          error={touched.name ? errors.name : undefined}
          required
        />

        {/* Identifier type switcher */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-sm font-bold text-gray-700">
              {usePhone ? 'Téléphone' : 'Email'}
            </label>
            <button
              type="button"
              onClick={() => { setUsePhone(!usePhone); setFormData({...formData, identifier: ''}); setDisplayIdentifier(''); }}
              className="text-xs font-bold text-ilma-primary hover:underline"
            >
              Utiliser {usePhone ? "l'email" : 'le téléphone'}
            </button>
          </div>
          <Input
            placeholder={usePhone ? "+229 96 XX XX XX" : "exemple@email.com"}
            type={usePhone ? "tel" : "email"}
            leftIcon={usePhone ? <Phone size={18} /> : <Mail size={18} />}
            value={usePhone ? displayIdentifier : formData.identifier}
            onChange={e => {
              if (usePhone) {
                const formatted = formatPhone(e.target.value);
                setDisplayIdentifier(formatted);
                setFormData({...formData, identifier: rawPhone(formatted)});
              } else {
                setFormData({...formData, identifier: e.target.value});
              }
            }}
            onBlur={() => handleBlur('identifier')}
            error={touched.identifier ? errors.identifier : undefined}
            required
          />
        </div>

        <div>
          <Input
            label="Mot de passe"
            type="password"
            placeholder="Minimum 8 caractères"
            leftIcon={<Lock size={18} />}
            value={formData.password}
            onChange={e => setFormData({...formData, password: e.target.value})}
            onBlur={() => handleBlur('password')}
            error={touched.password ? errors.password : undefined}
            required
          />
          {formData.password && (
            <div className="mt-2 flex items-center gap-2">
              <div className="flex gap-1 flex-1">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className={`h-1.5 flex-1 rounded-full transition-colors ${i <= passwordStrength ? strengthColors[passwordStrength] : 'bg-gray-200'}`} />
                ))}
              </div>
              <span className="text-xs font-bold text-gray-400">{strengthLabels[passwordStrength]}</span>
            </div>
          )}
        </div>

        <Input
          label="Confirmer le mot de passe"
          type="password"
          placeholder="Retape ton mot de passe"
          leftIcon={<Lock size={18} />}
          value={formData.confirmPassword}
          onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
          onBlur={() => handleBlur('confirmPassword')}
          error={touched.confirmPassword ? errors.confirmPassword : undefined}
          required
        />

        {role === 'parent' && (
          <label className="flex items-start gap-3 p-3 bg-amber-50 rounded-xl cursor-pointer">
            <input type="checkbox" required className="mt-1 w-4 h-4 accent-ilma-primary" />
            <span className="text-xs text-gray-600 leading-relaxed">
              Je certifie être le parent ou tuteur légal de l'enfant et je consens au traitement de ses données conformément à la politique de confidentialité d'ILMA.
            </span>
          </label>
        )}

        <div className="pt-2">
          <Button fullWidth type="submit" isLoading={isLoading}>
            Créer mon compte
          </Button>
        </div>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Déjà un compte ?{' '}
          <Link to="/login" className="font-bold text-ilma-primary hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
};
