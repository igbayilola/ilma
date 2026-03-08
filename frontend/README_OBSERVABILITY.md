
# Observability & Feature Flags Guide

This document describes the observability stack and feature flag system implemented in ILMA.

## 1. Telemetry Service (`services/telemetry.ts`)

Centralized service handling:
1.  **Error Tracking**: Logs exceptions to Console and Sentry (Mocked).
2.  **Performance**: Tracks Web Vitals (LCP, FID, CLS) and custom transaction spans.
3.  **Structured Logging**: Unified `logEvent` for business actions.

### Usage
```typescript
import { telemetry } from './services/telemetry';

// Log an Error
telemetry.logError(new Error("Something broke"), { contextId: 123 }, "ComponentName");

// Log a Business Event
telemetry.logEvent("Exercise", "Complete", "Math-L5", 100);

// Performance Span
const span = telemetry.startSpan("process", "heavyCalculation");
// ... do work
span.finish();
```

### Sentry Configuration
The service includes a mock Sentry implementation for development. To enable real Sentry:
1.  Install `@sentry/react`.
2.  Update `services/telemetry.ts` to import real Sentry.
3.  Set `VITE_SENTRY_DSN` in your `.env` file.

## 2. Feature Flags (`services/featureFlags.ts`)

A Zustand-based store for managing feature toggles. Supports local defaults and simulated remote configuration.

### Usage
```typescript
import { useFeatureFlag, FeatureFlag } from './services/featureFlags';

const MyComponent = () => {
  const isVoiceEnabled = useFeatureFlag(FeatureFlag.VOICE_INPUT);

  if (!isVoiceEnabled) return null;

  return <VoiceInput />;
};
```

### Adding a Flag
1.  Add the key to the `FeatureFlag` enum in `services/featureFlags.ts`.
2.  Set the default value in `DEFAULTS` constant.

## 3. Error Boundary
The app is wrapped in a global `ErrorBoundary` (`components/common/ErrorBoundary.tsx`) which:
1.  Catches React render errors.
2.  Logs the error and component stack to Telemetry.
3.  Displays a user-friendly "Something went wrong" UI with a reload button.

## 4. Web Vitals
Web Vitals are automatically initialized in `index.tsx` via `telemetry.init()`. Metrics (CLS, LCP, etc.) are logged to the console/telemetry service.
