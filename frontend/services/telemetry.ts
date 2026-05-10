
import * as SentrySDK from '@sentry/react';
import { onCLS, onFID, onLCP, onINP, onFCP, onTTFB } from 'web-vitals';

export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

const env = (import.meta as any).env;
const SENTRY_DSN = env?.VITE_SENTRY_DSN || '';
// Opt-in: must be explicitly enabled. Default off until DSN points to APDP-compliant host.
const SENTRY_ENABLED = String(env?.VITE_SENTRY_ENABLED || 'false').toLowerCase() === 'true';
const SENTRY_ACTIVE = SENTRY_ENABLED && Boolean(SENTRY_DSN);

class TelemetryService {
  private isInitialized = false;

  init() {
    if (this.isInitialized) return;

    if (SENTRY_ACTIVE) {
      SentrySDK.init({
        dsn: SENTRY_DSN,
        environment: env?.MODE || 'development',
        tracesSampleRate: env?.MODE === 'production' ? 0.2 : 1.0,
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
        integrations: [
          SentrySDK.browserTracingIntegration(),
          SentrySDK.replayIntegration(),
        ],
      });
      if (env?.MODE !== 'production') console.debug('[Telemetry] Sentry initialized');
    } else {
      if (env?.MODE !== 'production') console.debug('[Telemetry] No SENTRY_DSN — console-only mode');
    }

    this.initWebVitals();
    this.isInitialized = true;
  }

  private initWebVitals() {
    const logVital = (metric: any) => {
      this.logEvent('Performance', 'WebVital', metric.name, metric.value);
    };

    onCLS(logVital);
    onFID(logVital);
    onLCP(logVital);
    onINP(logVital);
    onFCP(logVital);
    onTTFB(logVital);
  }

  setUser(user: { id: string; role: string; email?: string } | null) {
    if (SENTRY_ACTIVE) {
      SentrySDK.setUser(user ? { id: user.id, data: { role: user.role } } : null);
    }
  }

  logError(error: Error | string, context?: Record<string, any>, source?: string) {
    const errObj = typeof error === 'string' ? new Error(error) : error;
    console.error(`[${source || 'App'}] Error:`, errObj);

    if (SENTRY_ACTIVE) {
      SentrySDK.captureException(errObj, { extra: { ...context, source } });
    }
  }

  logEvent(category: string, action: string, label?: string, value?: number) {
    if (SENTRY_ACTIVE) {
      SentrySDK.addBreadcrumb({
        category,
        message: action,
        data: { label, value },
        level: 'info',
      });
    }
  }

  startSpan(op: string, name: string) {
    if (SENTRY_ACTIVE) {
      return SentrySDK.startInactiveSpan({ name: `${op}.${name}`, op });
    }
    // Fallback no-op span
    const start = performance.now();
    return {
      end: () => {
        const duration = performance.now() - start;
        console.debug(`[Perf] ${op}.${name}: ${duration.toFixed(2)}ms`);
      },
    };
  }
}

export const telemetry = new TelemetryService();
