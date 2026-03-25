
import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import App from './App';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { telemetry } from './services/telemetry';
import { useFeatureFlagStore } from './services/featureFlags';
import { useConfigStore } from './store/configStore';

// Sentry error monitoring
Sentry.init({
  dsn: 'https://a0760f076dbdbb5e5775ae7c94f74a03@o4511106245853184.ingest.de.sentry.io/4511106316238928',
  integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
  tracesSampleRate: 0.2,
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 1.0,
  environment: import.meta.env.MODE,
});

// Initialize Observability
telemetry.init();

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
