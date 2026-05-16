import React, { useEffect, useState } from 'react';
import { Download, X, Smartphone, Share, Plus } from 'lucide-react';

/**
 * Discreet banner that prompts the user to install Sitou as a PWA.
 *
 * Two code paths, since iOS Safari has no `beforeinstallprompt` :
 * - Android / Chrome / Edge → capture the event, call `prompt()` on click.
 * - iOS Safari              → show static "Add to Home Screen" instructions
 *                             (no programmatic install possible).
 *
 * Hidden in both cases when:
 * - the app is already running standalone (matchMedia display-mode + iOS
 *   `navigator.standalone`)
 * - the user dismissed within the cooldown window (14 j, localStorage)
 *
 * Tracks 3 analytics events to measure the funnel :
 *   install_prompt_shown / install_prompt_accepted / install_prompt_dismissed
 *
 * On iOS we never emit `accepted` (no callback from the OS) — `shown` and
 * `dismissed` only.
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

/**
 * iOS Safari (iPhone, iPad) detection. iPadOS 13+ reports as desktop Safari,
 * so we also check for a touch-capable Mac (Macintosh + maxTouchPoints).
 */
export function isIosSafari(): boolean {
  if (typeof window === 'undefined') return false;
  const ua = window.navigator.userAgent || '';
  const isIDevice = /iPhone|iPad|iPod/.test(ua);
  const isIPadOS13 = /Macintosh/.test(ua) && (window.navigator.maxTouchPoints || 0) > 1;
  if (!isIDevice && !isIPadOS13) return false;
  // Filter out in-app browsers (Facebook, Instagram, Gmail…) where Add to
  // Home Screen isn't available — the prompt would mislead the user.
  const isInAppBrowser = /FBAN|FBAV|Instagram|Line|GSA\//.test(ua);
  return !isInAppBrowser;
}

interface InstallPwaBannerProps {
  /** Injected so tests can assert without depending on the real analytics module. */
  onTrack?: (event: 'shown' | 'accepted' | 'dismissed') => void;
}

type Mode = 'android' | 'ios';

export const InstallPwaBanner: React.FC<InstallPwaBannerProps> = ({ onTrack }) => {
  const [mode, setMode] = useState<Mode | null>(null);
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = useState(false);
  const [installing, setInstalling] = useState(false);

  useEffect(() => {
    if (isStandalone() || isWithinCooldown()) return;

    // iOS path : no event, just show the static hint after a short delay so
    // we don't blast the user the moment the page loads.
    if (isIosSafari()) {
      const t = setTimeout(() => {
        setMode('ios');
        setVisible(true);
        onTrack?.('shown');
      }, 1500);
      return () => clearTimeout(t);
    }

    // Android / Chromium path : wait for the browser event.
    const handler = (event: Event) => {
      event.preventDefault();
      const promptEvent = event as BeforeInstallPromptEvent;
      setInstallEvent(promptEvent);
      setMode('android');
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

  if (!visible || !mode) return null;
  if (mode === 'android' && !installEvent) return null;

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

      {mode === 'android' && (
        <button
          type="button"
          onClick={handleInstall}
          disabled={installing}
          className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-sitou-primary text-white font-bold text-sm rounded-xl hover:bg-amber-600 transition-colors disabled:opacity-50"
        >
          <Download size={16} />
          {installing ? 'Installation…' : 'Installer l\'app'}
        </button>
      )}

      {mode === 'ios' && (
        <ol className="mt-3 space-y-1.5 text-xs text-gray-700">
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-100 inline-flex items-center justify-center text-gray-700 font-bold text-[10px]">1</span>
            <span className="flex items-center gap-1">
              Appuyez sur <Share size={14} className="text-sitou-primary inline" aria-label="icône Partager"/> en bas de Safari
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-100 inline-flex items-center justify-center text-gray-700 font-bold text-[10px]">2</span>
            <span className="flex items-center gap-1">
              Choisissez <strong>« Sur l'écran d'accueil »</strong> <Plus size={14} className="text-gray-500 inline" aria-hidden/>
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-gray-100 inline-flex items-center justify-center text-gray-700 font-bold text-[10px]">3</span>
            <span>Confirmez avec « Ajouter »</span>
          </li>
        </ol>
      )}
    </div>
  );
};
