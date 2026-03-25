/**
 * Push notification registration service.
 * Handles permission request + subscription management via Web Push with VAPID.
 */
import { apiClient } from './apiClient';
import { telemetry } from './telemetry';

const PUSH_SUBSCRIBED_KEY = 'ilma_push_subscribed';
const VAPID_PUBLIC_KEY = 'BNQC2U0LMDuszpg_NmkMmh_v8_FuJUkCoC3o-Ew-X3fNzvJb4F8iBmxFXV55y3Z8u7KQ0-Rwyixz2BUL7ttgo50';

/** Convert a base64 VAPID key to Uint8Array for pushManager.subscribe(). */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export const pushService = {
  /** Check if push is supported in this browser. */
  isSupported(): boolean {
    return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  },

  /** Check current permission status. */
  getPermission(): NotificationPermission | 'unsupported' {
    if (!this.isSupported()) return 'unsupported';
    return Notification.permission;
  },

  /** Check if already subscribed (local flag). */
  isSubscribed(): boolean {
    try {
      return localStorage.getItem(PUSH_SUBSCRIBED_KEY) === '1';
    } catch {
      return false;
    }
  },

  /**
   * Request permission and subscribe to push notifications.
   * Returns true if subscribed successfully.
   */
  async subscribe(): Promise<boolean> {
    if (!this.isSupported()) return false;

    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        telemetry.logEvent('Push', 'Permission Denied');
        return false;
      }

      const registration = await navigator.serviceWorker.ready;
      const existingSub = await registration.pushManager.getSubscription();

      if (existingSub) {
        // Already subscribed — send to backend in case it's a new login
        await apiClient.post('/notifications/push-subscription', {
          endpoint: existingSub.endpoint,
          keys: existingSub.toJSON().keys,
        }).catch(() => {});
        localStorage.setItem(PUSH_SUBSCRIBED_KEY, '1');
        return true;
      }

      // Subscribe with VAPID public key
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      }).catch(() => null);

      if (subscription) {
        // Send subscription to backend
        await apiClient.post('/notifications/push-subscription', {
          endpoint: subscription.endpoint,
          keys: subscription.toJSON().keys,
        }).catch(() => {});

        localStorage.setItem(PUSH_SUBSCRIBED_KEY, '1');
        telemetry.logEvent('Push', 'Subscribed');
        return true;
      }

      return false;
    } catch (err) {
      telemetry.logError(err instanceof Error ? err : new Error(String(err)), {}, 'pushService');
      return false;
    }
  },

  /** Unsubscribe from push notifications. */
  async unsubscribe(): Promise<boolean> {
    if (!this.isSupported()) return false;

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        // Remove from backend
        await apiClient.delete('/notifications/push-subscription', {
          data: {
            endpoint: subscription.endpoint,
            keys: subscription.toJSON().keys,
          },
        }).catch(() => {});
        await subscription.unsubscribe();
      }
      localStorage.removeItem(PUSH_SUBSCRIBED_KEY);
      telemetry.logEvent('Push', 'Unsubscribed');
      return true;
    } catch {
      return false;
    }
  },
};
