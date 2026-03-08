
import { create } from 'zustand';

export enum FeatureFlag {
  NEW_PLAYER_UI = 'new_player_ui',
  DARK_MODE = 'dark_mode',
  VOICE_INPUT = 'voice_input',
  OFFLINE_SYNC_V2 = 'offline_sync_v2',
  PARENT_REPORTS_WEEKLY = 'parent_reports_weekly'
}

const DEFAULTS: Record<FeatureFlag, boolean> = {
  [FeatureFlag.NEW_PLAYER_UI]: false,
  [FeatureFlag.DARK_MODE]: false,
  [FeatureFlag.VOICE_INPUT]: true,
  [FeatureFlag.OFFLINE_SYNC_V2]: true,
  [FeatureFlag.PARENT_REPORTS_WEEKLY]: false,
};

const env = (import.meta as any).env;
const FLAGS_URL = env?.VITE_FLAGS_URL || '';

interface FeatureFlagState {
  flags: Record<string, boolean>;
  isLoading: boolean;
  init: () => Promise<void>;
  isEnabled: (flag: FeatureFlag) => boolean;
  setFlag: (flag: FeatureFlag, value: boolean) => void;
}

export const useFeatureFlagStore = create<FeatureFlagState>((set, get) => ({
  flags: DEFAULTS,
  isLoading: true,

  init: async () => {
    set({ isLoading: true });
    try {
      let remoteFlags: Record<string, boolean> = {};

      if (FLAGS_URL) {
        const res = await fetch(FLAGS_URL, { signal: AbortSignal.timeout(3000) });
        if (res.ok) {
          const data = await res.json();
          // Accept { flags: {...} } or flat { key: bool } shape
          remoteFlags = data.flags ?? data;
        }
      }

      set((state) => ({
        flags: { ...state.flags, ...remoteFlags },
        isLoading: false,
      }));
    } catch {
      console.warn('[FeatureFlags] Remote fetch failed, using defaults');
      set({ isLoading: false });
    }
  },

  isEnabled: (flag: FeatureFlag) => {
    return get().flags[flag] ?? false;
  },

  setFlag: (flag: FeatureFlag, value: boolean) => {
    set((state) => ({
      flags: { ...state.flags, [flag]: value },
    }));
  },
}));

export const useFeatureFlag = (flag: FeatureFlag) => {
  return useFeatureFlagStore((state) => state.isEnabled(flag));
};
