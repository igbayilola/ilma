import { Profile, User } from '../types';

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken?: string; // Optional if using HttpOnly cookies
  expiresIn?: number;
  profiles?: Profile[];
}

export interface LoginCredentials {
  identifier: string; // Email or Phone
  password?: string;
  otp?: string;
}

export interface RegisterData {
  name?: string;
  fullName?: string;
  email: string;
  phone?: string;
  password?: string;
  role: string;
  gradeLevelId?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  profiles: Profile[];
  activeProfile: Profile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>; // Session restoration on load
  setAccessToken: (token: string) => void;
  setProfiles: (profiles: Profile[]) => void;
  selectProfile: (profileId: string) => void;
  clearProfile: () => void;
}
