import { create } from 'zustand';

type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isDark: () => boolean;
}

function getSystemPreference(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function applyTheme(theme: Theme) {
  const isDark = theme === 'dark' || (theme === 'system' && getSystemPreference());
  document.documentElement.classList.toggle('dark', isDark);
  localStorage.setItem('sitou-theme', theme);
}

const stored = (typeof localStorage !== 'undefined' && localStorage.getItem('sitou-theme')) as Theme | null;
const initial: Theme = stored && ['light', 'dark', 'system'].includes(stored) ? stored : 'light';

// Apply on load
if (typeof document !== 'undefined') {
  applyTheme(initial);
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: initial,

  setTheme: (theme: Theme) => {
    applyTheme(theme);
    set({ theme });
  },

  isDark: () => {
    const t = get().theme;
    return t === 'dark' || (t === 'system' && getSystemPreference());
  },
}));

// Listen for system preference changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const state = useThemeStore.getState();
    if (state.theme === 'system') {
      applyTheme('system');
    }
  });
}
