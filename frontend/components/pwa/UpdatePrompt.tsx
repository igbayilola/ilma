import React, { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { ButtonVariant } from '../../types';
import { RefreshCw, X, Clock } from 'lucide-react';

export const PWAUpdatePrompt: React.FC = () => {
  const [showUpdate, setShowUpdate] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);
  const [isInExercise, setIsInExercise] = useState(false);

  // Track whether user is in an active exercise session
  useEffect(() => {
    const checkExercise = () => {
      setIsInExercise(window.location.hash.includes('/exercise/'));
    };

    checkExercise();
    window.addEventListener('hashchange', checkExercise);
    return () => window.removeEventListener('hashchange', checkExercise);
  }, []);

  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

    const registerSW = async () => {
      try {
        const reg = await navigator.serviceWorker.register('/sw.js');
        setRegistration(reg);

        // Check for updates
        reg.addEventListener('updatefound', () => {
          const newWorker = reg.installing;
          if (!newWorker) return;

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New version available
              setShowUpdate(true);
            }
          });
        });

        // Listen for controller changes (after skipWaiting)
        let refreshing = false;
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          if (!refreshing) {
            refreshing = true;
            window.location.reload();
          }
        });
      } catch (err) {
        console.warn('[PWA] Service Worker registration failed:', err);
      }
    };

    registerSW();
  }, []);

  const handleUpdate = () => {
    if (registration?.waiting) {
      registration.waiting.postMessage('SKIP_WAITING');
    }
    setShowUpdate(false);
  };

  if (!showUpdate) return null;

  return (
    <div className="fixed bottom-20 md:bottom-6 left-4 right-4 md:left-auto md:right-6 md:w-96 z-50 animate-slide-up">
      <div className="bg-white rounded-2xl shadow-float border border-gray-200 p-4 flex items-start gap-3">
        <div className={`p-2 rounded-xl flex-shrink-0 ${isInExercise ? 'bg-blue-100 text-blue-600' : 'bg-amber-100 text-ilma-primary'}`}>
          {isInExercise ? <Clock size={20} /> : <RefreshCw size={20} />}
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-gray-900 text-sm">
            {isInExercise ? 'Mise à jour disponible' : 'Nouvelle version disponible'}
          </h4>
          <p className="text-xs text-gray-500 mt-0.5 mb-3">
            {isInExercise
              ? "Mise à jour disponible. Elle sera installée au prochain lancement."
              : "Une mise a jour d'ILMA est prête. Rechargez pour en profiter."}
          </p>
          <div className="flex gap-2">
            {!isInExercise && (
              <Button size="sm" onClick={handleUpdate} leftIcon={<RefreshCw size={14} />}>
                Mettre à jour
              </Button>
            )}
            <Button size="sm" variant={ButtonVariant.GHOST} onClick={() => setShowUpdate(false)}>
              {isInExercise ? 'Compris' : 'Plus tard'}
            </Button>
          </div>
        </div>
        <button
          onClick={() => setShowUpdate(false)}
          className="p-1 text-gray-400 hover:text-gray-600"
          aria-label="Fermer"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
};
