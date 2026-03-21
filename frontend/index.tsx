
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { telemetry } from './services/telemetry';
import { useFeatureFlagStore } from './services/featureFlags';
import { useConfigStore } from './store/configStore';

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
