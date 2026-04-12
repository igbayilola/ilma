
import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import App from './App';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { telemetry } from './services/telemetry';
import { analytics } from './services/analytics';
import { useFeatureFlagStore } from './services/featureFlags';
import { useConfigStore } from './store/configStore';

// Sentry error monitoring (DSN from environment variable only)
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
    tracesSampleRate: 0.2,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 1.0,
    environment: import.meta.env.MODE,
  });
}

// Initialize Observability
telemetry.init();
analytics.start();

// Initialize Feature Flags
useFeatureFlagStore.getState().init();

// Initialize Dynamic Config from backend
useConfigStore.getState().fetchConfig();
useConfigStore.getState().startAutoRefresh();

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <ErrorBoundary>
        <App />
    </ErrorBoundary>
  </React.StrictMode>
);
