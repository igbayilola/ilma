import React, { useEffect, useState } from 'react';
import { Download, X, Smartphone } from 'lucide-react';

/**
 * Discreet banner that prompts the user to install Sitou as a PWA when the
 * browser supports `beforeinstallprompt` (Chrome / Edge / Android). Hidden:
 * - if the app is already running standalone (matchMedia display-mode)
 * - if the user dismissed within the cooldown window
 * - if no install event has been captured (iOS Safari, unsupported browsers)
 *
 * Tracks 3 analytics events so we can measure conversion:
 *   install_prompt_shown / install_prompt_accepted / install_prompt_dismissed
 *
 * iOS Safari has no `beforeinstallprompt` API — addressing it requires a
 * separate "Ajouter à l'écran d'accueil" hint, out of scope here.
 */

// Cooldown : 14 j avant de re-proposer après un refus explicite.
const DISMISS_COOLDOWN_MS = 14 * 24 * 60 * 60 * 1000;
const DISMISS_KEY = 'sitou_install_prompt_dismissed_at';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

function isStandalone(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  if (window.matchMedia('(display-mode: standalone)').matches) return true;
  // iOS Safari exposes a non-standard nav flag — also treated as installed.
  return Boolean((window.navigator as any).standalone);
}

function isWithinCooldown(): boolean {
  try {
    const raw = window.localStorage.getItem(DISMISS_KEY);
    if (!raw) return false;
    const ts = Number(raw);
    if (Number.isNaN(ts)) return false;
    return Date.now() - ts < DISMISS_COOLDOWN_MS;
  } catch {
    return false;
  }
}

interface InstallPwaBannerProps {
  /** Injected so tests can assert without depending on the real analytics module. */
  onTrack?: (event: 'shown' | 'accepted' | 'dismissed') => void;
}

export const InstallPwaBanner: React.FC<InstallPwaBannerProps> = ({ onTrack }) => {
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = useState(false);
  const [installing, setInstalling] = useState(false);

  useEffect(() => {
    if (isStandalone() || isWithinCooldown()) return;

    const handler = (event: Event) => {
      // Prevent the mini-infobar Chrome would have shown on its own — we
      // surface our own contextualised banner instead.
      event.preventDefault();
      const promptEvent = event as BeforeInstallPromptEvent;
      setInstallEvent(promptEvent);
      setVisible(true);
      onTrack?.('shown');
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, [onTrack]);

  const handleInstall = async () => {
    if (!installEvent || installing) return;
    setInstalling(true);
    try {
      await installEvent.prompt();
      const { outcome } = await installEvent.userChoice;
      onTrack?.(outcome === 'accepted' ? 'accepted' : 'dismissed');
      if (outcome === 'dismissed') {
        try { window.localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch { /* ignore */ }
      }
      // After prompt(), the event can't be reused.
      setInstallEvent(null);
      setVisible(false);
    } finally {
      setInstalling(false);
    }
  };

  const handleDismiss = () => {
    try { window.localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch { /* ignore */ }
    onTrack?.('dismissed');
    setVisible(false);
  };

  if (!visible || !installEvent) return null;

  return (
    <div
      role="dialog"
      aria-labelledby="install-pwa-title"
      className="fixed left-4 right-4 bottom-20 md:bottom-6 md:left-auto md:right-6 md:max-w-sm z-40 bg-white rounded-2xl shadow-2xl border border-gray-200 p-4 animate-slide-up"
    >
      <button
        type="button"
        onClick={handleDismiss}
        aria-label="Fermer"
        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
      >
        <X size={16} />
      </button>

      <div className="flex items-start gap-3 pr-6">
        <div className="w-10 h-10 rounded-xl bg-sitou-primary/10 flex items-center justify-center flex-shrink-0">
          <Smartphone size={20} className="text-sitou-primary" />
        </div>
        <div className="flex-1">
          <h3 id="install-pwa-title" className="font-bold text-gray-900 text-sm">
            Installer Sitou
          </h3>
          <p className="text-xs text-gray-500 mt-0.5 leading-snug">
            Accès direct depuis l'écran d'accueil, sans passer par le navigateur.
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={handleInstall}
        disabled={installing}
        className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-sitou-primary text-white font-bold text-sm rounded-xl hover:bg-amber-600 transition-colors disabled:opacity-50"
      >
        <Download size={16} />
        {installing ? 'Installation…' : 'Installer l\'app'}
      </button>
    </div>
  );
};
