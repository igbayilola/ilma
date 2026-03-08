import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { ButtonVariant, UserRole } from '../../types';
import { CloudOff, Trophy, BookOpen, ArrowRight } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const SLIDES = [
  {
    id: 1,
    title: "Apprends partout",
    desc: "Emporte tes le\u00e7ons avec toi. \u00c0 la maison, dans le bus, ou chez mamie.",
    icon: <BookOpen className="w-24 h-24 text-white" />,
    gradient: "gradient-math"
  },
  {
    id: 2,
    title: "Pas d'internet ? Pas de souci",
    desc: "Continue \u00e0 t'exercer m\u00eame sans connexion. Tout est sauvegard\u00e9.",
    icon: <CloudOff className="w-24 h-24 text-white" />,
    gradient: "gradient-success"
  },
  {
    id: 3,
    title: "Gagne des badges",
    desc: "Rel\u00e8ve des d\u00e9fis, compl\u00e8te ta collection et monte de niveau !",
    icon: <Trophy className="w-24 h-24 text-white" />,
    gradient: "gradient-gold"
  }
];

export const SplashPage: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleGuestMode = async () => {
      try {
        await login({ identifier: 'guest', password: 'guest' });
        navigate('/app/student/dashboard');
      } catch {
        navigate('/app/student/dashboard');
      }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col justify-between max-w-md mx-auto md:max-w-full md:grid md:grid-cols-2">

      {/* Visual Side (Carousel) */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-white md:bg-ilma-primary-light relative overflow-hidden">
        {/* Carousel Content */}
        <div className="w-full max-w-sm text-center z-10">
          <div className={`w-48 h-48 mx-auto rounded-full flex items-center justify-center mb-8 transition-all duration-500 ${SLIDES[currentSlide].gradient} shadow-lg`}>
             {SLIDES[currentSlide].icon}
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 mb-4 animate-fade-in font-display">
            {SLIDES[currentSlide].title}
          </h2>
          <p className="text-gray-500 text-lg leading-relaxed animate-fade-in">
            {SLIDES[currentSlide].desc}
          </p>
        </div>

        {/* Indicators */}
        <div className="flex space-x-2 mt-8">
          {SLIDES.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentSlide(idx)}
              className={`h-2.5 rounded-full transition-all duration-300 ${
                currentSlide === idx ? 'gradient-hero w-8' : 'bg-gray-300 w-2.5'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Action Side */}
      <div className="p-8 flex flex-col justify-center bg-white md:max-w-md md:mx-auto w-full">
        <div className="md:hidden text-center mb-8">
             <span className="font-extrabold text-2xl bg-gradient-to-r from-amber-600 via-orange-500 to-yellow-500 bg-clip-text text-transparent font-display">ILMA</span>
        </div>

        <div className="space-y-4">
          <Link to="/login" className="block w-full">
            <Button fullWidth className="h-14 text-lg shadow-clay">
              Se connecter
            </Button>
          </Link>

          <Link to="/register" className="block w-full">
            <Button fullWidth variant={ButtonVariant.SECONDARY} className="h-14 text-lg">
              Cr&eacute;er un compte
            </Button>
          </Link>

          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-100"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-400">ou</span>
            </div>
          </div>

          <Button
            fullWidth
            variant={ButtonVariant.GHOST}
            onClick={handleGuestMode}
            className="text-gray-500 font-medium hover:text-ilma-primary hover:bg-gray-50"
          >
            Continuer en mode invit&eacute;
          </Button>
        </div>

        <p className="text-center text-xs text-gray-400 mt-8">
            En continuant, tu acceptes nos <a href="#" className="underline">Conditions d'utilisation</a>.
        </p>
      </div>
    </div>
  );
};
