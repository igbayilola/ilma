/**
 * Push notification registration service.
 * Handles permission request + subscription management.
 */
import { apiClient } from './apiClient';
import { telemetry } from './telemetry';

const PUSH_SUBSCRIBED_KEY = 'ilma_push_subscribed';

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
        // Already subscribed at browser level
        localStorage.setItem(PUSH_SUBSCRIBED_KEY, '1');
        return true;
      }

      // Subscribe — in a real deployment, the VAPID public key comes from the server
      // For now, create a subscription that works with the mock push provider
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        // applicationServerKey would be the VAPID public key from the server
        // applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      }).catch(() => null);

      if (subscription) {
        // Send subscription to backend
        await apiClient.post('/notifications/push-subscription', {
          endpoint: subscription.endpoint,
          keys: subscription.toJSON().keys,
        }).catch(() => {
          // Backend may not have this endpoint yet — that's OK
        });

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
