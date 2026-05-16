/**
 * Product analytics service.
 *
 * Batches events in memory and flushes them to POST /analytics/events.
 * Uses navigator.sendBeacon on page unload so drop_off events survive tab close.
 */
import { apiClient } from './apiClient';

const FLUSH_INTERVAL_MS = 30_000; // 30 s
const MAX_BATCH = 50;

interface AnalyticsEvent {
  event_type: string;
  session_id?: string;
  data?: Record<string, any>;
  client_ts: string;
}

let queue: AnalyticsEvent[] = [];
let flushTimer: ReturnType<typeof setInterval> | null = null;

function enqueue(event: Omit<AnalyticsEvent, 'client_ts'>) {
  queue.push({ ...event, client_ts: new Date().toISOString() });
  if (queue.length >= MAX_BATCH) {
    flush();
  }
}

async function flush() {
  if (queue.length === 0) return;
  const batch = queue.splice(0, MAX_BATCH);
  try {
    await apiClient.post('/analytics/events', { events: batch });
  } catch {
    // On failure, put events back so they retry next flush
    queue.unshift(...batch);
  }
}

/** Best-effort flush via sendBeacon (works during page unload). */
function beaconFlush() {
  if (queue.length === 0) return;
  const batch = queue.splice(0, MAX_BATCH);
  const env = (import.meta as any).env;
  const baseUrl = env?.VITE_API_URL || '/api/v1';

  // sendBeacon requires a full URL and doesn't support custom auth headers,
  // so we include the token in the body for this special case.
  const payload = JSON.stringify({ events: batch });
  try {
    navigator.sendBeacon(`${baseUrl}/analytics/events`, new Blob([payload], { type: 'application/json' }));
  } catch {
    // silently ignore — best-effort
  }
}

function start() {
  if (flushTimer) return;
  flushTimer = setInterval(flush, FLUSH_INTERVAL_MS);
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') beaconFlush();
  });
  window.addEventListener('pagehide', beaconFlush);
}

function stop() {
  if (flushTimer) {
    clearInterval(flushTimer);
    flushTimer = null;
  }
  flush();
}

// ── Public tracking helpers ──────────────────────────────────

function exerciseStart(sessionId: string, data: {
  skill_id: string;
  micro_skill_id?: string;
  source: string;
}) {
  enqueue({ event_type: 'exercise_start', session_id: sessionId, data });
}

function exerciseStepCompleted(sessionId: string, data: {
  question_number: number;
  question_id: string;
  question_type: string;
  is_correct: boolean;
  time_spent_seconds: number;
  hints_used: number;
}) {
  enqueue({ event_type: 'exercise_step_completed', session_id: sessionId, data });
}

function hintRequested(sessionId: string, data: {
  question_number: number;
  question_id: string;
  time_before_hint_seconds: number;
}) {
  enqueue({ event_type: 'hint_requested', session_id: sessionId, data });
}

function exerciseCompleted(sessionId: string, data: {
  score_percent: number;
  time_total_seconds: number;
  total_questions: number;
  correct_answers: number;
  total_hints_used: number;
  status: 'success' | 'abandon';
  smart_score_delta?: number;
}) {
  enqueue({ event_type: 'exercise_completed', session_id: sessionId, data });
}

function dropOff(sessionId: string, data: {
  question_number: number;
  time_on_question_seconds: number;
  total_time_seconds: number;
}) {
  enqueue({ event_type: 'drop_off', session_id: sessionId, data });
}

function contentViewed(data: {
  content_type: string;
  content_id: string;
  source: string;
}) {
  enqueue({ event_type: 'content_viewed', data });
}

/** PWA install funnel (A5.6) — shown / accepted / dismissed. */
function installPromptOutcome(outcome: 'shown' | 'accepted' | 'dismissed') {
  enqueue({ event_type: `install_prompt_${outcome}` });
}

export const analytics = {
  start,
  stop,
  flush,
  exerciseStart,
  exerciseStepCompleted,
  hintRequested,
  exerciseCompleted,
  dropOff,
  contentViewed,
  installPromptOutcome,
};
