import { create } from 'zustand';

const env = (import.meta as any).env;
const BASE_URL = env?.VITE_API_URL || '/api/v1';

const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Default values (fallback if API unavailable)
const DEFAULTS = {
  freemiumDailyLimit: 5,
  maintenanceMode: false,
  registrationOpen: true,
  minAppVersion: '1.0.0',
  paymentProviders: ['kkiapay', 'fedapay'] as string[],
  allowedPhonePrefixes: ['90', '91', '92', '93', '94', '95', '96', '97'] as string[],
  monthlyPriceXof: 2500,
};

export type PublicConfig = typeof DEFAULTS;

interface ConfigState extends PublicConfig {
  isLoaded: boolean;
  fetchConfig: () => Promise<void>;
  startAutoRefresh: () => void;
  _refreshTimer: ReturnType<typeof setInterval> | null;
}

export const useConfigStore = create<ConfigState>((set, get) => ({
  ...DEFAULTS,
  isLoaded: false,
  _refreshTimer: null,

  fetchConfig: async () => {
    try {
      const res = await fetch(`${BASE_URL}/config/public`, {
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) return;
      const json = await res.json();
      const data = json.data || json;

      set({
        freemiumDailyLimit: data.freemium_daily_limit ?? DEFAULTS.freemiumDailyLimit,
        maintenanceMode: data.maintenance_mode ?? DEFAULTS.maintenanceMode,
        registrationOpen: data.registration_open ?? DEFAULTS.registrationOpen,
        minAppVersion: data.min_app_version ?? DEFAULTS.minAppVersion,
        paymentProviders: data.payment_providers ?? DEFAULTS.paymentProviders,
        allowedPhonePrefixes: data.allowed_phone_prefixes ?? DEFAULTS.allowedPhonePrefixes,
        monthlyPriceXof: data.monthly_price_xof ?? DEFAULTS.monthlyPriceXof,
        isLoaded: true,
      });
    } catch {
      console.warn('[ConfigStore] Failed to fetch public config, using defaults');
      set({ isLoaded: true });
    }
  },

  startAutoRefresh: () => {
    const existing = get()._refreshTimer;
    if (existing) return; // Already running

    const timer = setInterval(() => {
      get().fetchConfig();
    }, REFRESH_INTERVAL);

    set({ _refreshTimer: timer });
  },
}));
