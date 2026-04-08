import { ApiClientError, ErrorCode } from '../types/api';
import { useAuthStore } from '../store/authStore';

// Fix for Property 'env' does not exist on type 'ImportMeta'
const env = (import.meta as any).env;
const BASE_URL = env?.VITE_API_URL || '/api/v1';
const DEFAULT_TIMEOUT = 10000;

interface RequestConfig extends RequestInit {
  timeout?: number;
  retry?: number;
  skipAuth?: boolean;
  _isRetry?: boolean; // Internal flag to prevent infinite loops
}

// Queue for failed requests during refreshing
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Core Fetch Wrapper
 */
async function client<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
  const { timeout = DEFAULT_TIMEOUT, retry = 0, skipAuth = false, _isRetry = false, ...customConfig } = config;

  // Retry wrapper with exponential backoff
  if (retry > 0 && !_isRetry) {
    let lastError: Error | null = null;
    for (let attempt = 0; attempt <= retry; attempt++) {
      try {
        return await client<T>(endpoint, { ...config, retry: 0, _isRetry: true });
      } catch (err: any) {
        lastError = err;
        // Don't retry on 4xx errors (client errors)
        if (err instanceof ApiClientError && err.status >= 400 && err.status < 500) throw err;
        if (attempt < retry) {
          await new Promise(r => setTimeout(r, Math.min(1000 * Math.pow(2, attempt), 10000)));
        }
      }
    }
    throw lastError;
  }

  // 1. Get Token + Active Profile from Store
  const { accessToken, activeProfile } = useAuthStore.getState();

  const headers = new Headers(customConfig.headers);
  if (!skipAuth && accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  if (activeProfile) {
    headers.set('X-Profile-Id', activeProfile.id);
  }
  headers.set('Content-Type', 'application/json');
  headers.set('Accept', 'application/json');

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...customConfig,
      headers,
      signal: controller.signal,
    });

    clearTimeout(id);

    // 2. Error Handling & Interceptors
    if (!response.ok) {
      
      // --- START: 401 Interceptor Logic ---
      if (response.status === 401 && !skipAuth && !_isRetry && !endpoint.includes('/auth/logout')) {
        if (isRefreshing) {
          // If already refreshing, queue this request
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          }).then(() => {
            return client<T>(endpoint, { ...config, _isRetry: true });
          });
        }

        isRefreshing = true;

        try {
          // Attempt Refresh — send refresh_token from localStorage
          const storedRefresh = localStorage.getItem('sitou_refresh_token');
          if (!storedRefresh) throw new Error('No refresh token');

          const refreshResponse = await fetch(`${BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: storedRefresh }),
          });

          if (!refreshResponse.ok) {
            throw new Error('Refresh failed');
          }

          const refreshEnvelope = await refreshResponse.json();
          const refreshData = refreshEnvelope?.data || refreshEnvelope;
          const newAccessToken = refreshData.access_token || refreshData.accessToken;
          // Store new refresh token if rotated
          if (refreshData.refresh_token) {
            localStorage.setItem('sitou_refresh_token', refreshData.refresh_token);
          }

          // Update Store
          useAuthStore.getState().setAccessToken(newAccessToken);

          // Process Queue
          processQueue(null, newAccessToken);
          isRefreshing = false;

          // Retry Original Request
          return client<T>(endpoint, { ...config, _isRetry: true });

        } catch (refreshError) {
          processQueue(refreshError as Error, null);
          isRefreshing = false;
          // Trigger Logout
          useAuthStore.getState().logout();
          throw new ApiClientError('Session expirée. Veuillez vous reconnecter.', ErrorCode.UNAUTHORIZED, 401);
        }
      }
      // --- END: 401 Interceptor Logic ---

      // Standard Error Parsing — backend returns {success, error: {code, message, details}}
      let errorData: any;
      try {
        errorData = await response.json();
      } catch {
        errorData = { error: { message: response.statusText } };
      }

      const errMsg = errorData?.error?.message || errorData?.message || response.statusText;
      const errDetails = errorData?.error?.details || errorData?.details;

      switch (response.status) {
        case 400: throw new ApiClientError(errMsg, ErrorCode.VALIDATION_ERROR, 400, errDetails);
        case 401: throw new ApiClientError('Session expirée', ErrorCode.UNAUTHORIZED, 401);
        case 403: throw new ApiClientError(errMsg || 'Accès refusé', ErrorCode.FORBIDDEN, 403);
        case 404: throw new ApiClientError(errMsg || 'Ressource introuvable', ErrorCode.NOT_FOUND, 404);
        case 409: throw new ApiClientError(errMsg, ErrorCode.VALIDATION_ERROR, 409);
        case 422: throw new ApiClientError(errMsg, ErrorCode.VALIDATION_ERROR, 422, errDetails);
        case 429: throw new ApiClientError('Trop de requêtes', ErrorCode.NETWORK_ERROR, 429);
        case 500: throw new ApiClientError('Erreur serveur', ErrorCode.SERVER_ERROR, 500);
        default: throw new ApiClientError(errMsg || 'Erreur inconnue', ErrorCode.UNKNOWN, response.status);
      }
    }

    if (response.status === 204) return {} as T;

    // Backend envelope: {success, data, message, timestamp} → extract data
    const envelope = await response.json();
    if (envelope && typeof envelope === 'object' && 'success' in envelope) {
      return envelope.data as T;
    }
    return envelope;

  } catch (error: any) {
    clearTimeout(id);
    if (error.name === 'AbortError') throw new ApiClientError('Timeout', ErrorCode.TIMEOUT, 408);
    if (error.message === 'Failed to fetch') throw new ApiClientError('Pas de connexion internet', ErrorCode.NETWORK_ERROR, 0);
    throw error;
  }
}

export const apiClient = {
  get: <T>(url: string, config?: RequestConfig) => client<T>(url, { ...config, method: 'GET' }),
  post: <T>(url: string, body: any, config?: RequestConfig) => client<T>(url, { ...config, method: 'POST', body: JSON.stringify(body) }),
  put: <T>(url: string, body: any, config?: RequestConfig) => client<T>(url, { ...config, method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(url: string, body: any, config?: RequestConfig) => client<T>(url, { ...config, method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(url: string, config?: RequestConfig) => client<T>(url, { ...config, method: 'DELETE' }),

  async upload<T = any>(url: string, formData: FormData): Promise<T> {
    const { accessToken, activeProfile } = useAuthStore.getState();
    const headers: Record<string, string> = {};
    if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
    if (activeProfile) headers['X-Profile-Id'] = activeProfile.id;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout for uploads

    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiClientError(
          errorData.message || errorData?.error?.message || 'Upload failed',
          ErrorCode.UNKNOWN,
          response.status,
          errorData.details,
        );
      }

      const data = await response.json();
      return data.data ?? data;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof ApiClientError) throw error;
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new ApiClientError('Upload timeout', ErrorCode.TIMEOUT, 408);
      }
      throw new ApiClientError('Network error during upload', ErrorCode.NETWORK_ERROR, 0);
    }
  },
};
