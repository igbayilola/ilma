import { create } from 'zustand';
import fr from './fr.json';

export type Locale = 'fr' | 'en';

type TranslationDict = Record<string, string | Record<string, string>>;

const translations: Record<string, TranslationDict> = {
  fr,
  en: fr, // Placeholder — will load real English translations when ready
};

let currentLocale: Locale = 'fr';

interface I18nState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('sitou-locale') : null;
const initial: Locale = stored === 'en' ? 'en' : 'fr';
currentLocale = initial;

function resolve(dict: TranslationDict, key: string): string | undefined {
  const parts = key.split('.');
  let current: any = dict;
  for (const part of parts) {
    if (current == null || typeof current !== 'object') return undefined;
    current = current[part];
  }
  return typeof current === 'string' ? current : undefined;
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) return template;
  return template.replace(/\{\{(\w+)\}\}/g, (_, key) => String(params[key] ?? `{{${key}}}`));
}

// ── Standalone helpers (non-React contexts) ──────────────────────

export function setLocale(locale: Locale) {
  currentLocale = locale;
  localStorage.setItem('sitou-locale', locale);
  document.documentElement.lang = locale;
}

export function t(key: string, params?: Record<string, string | number>): string {
  const dict = translations[currentLocale];
  const value = resolve(dict, key);
  if (!value) return key;
  if (params) {
    return Object.entries(params).reduce(
      (str, [k, v]) => str.replace(`{${k}}`, String(v)),
      interpolate(value, params),
    );
  }
  return interpolate(value, params);
}

// ── Zustand store (React components) ─────────────────────────────

export const useI18n = create<I18nState>((set, get) => ({
  locale: initial,

  setLocale: (locale: Locale) => {
    currentLocale = locale;
    localStorage.setItem('sitou-locale', locale);
    document.documentElement.lang = locale;
    set({ locale });
  },

  t: (key: string, params?: Record<string, string | number>) => {
    const dict = translations[get().locale];
    const value = resolve(dict, key);
    if (!value) return key;
    return interpolate(value, params);
  },
}));

export { fr };
