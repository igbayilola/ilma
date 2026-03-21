/**
 * Hook that listens for service worker messages (foreground push notifications)
 * and shows them as in-app toasts.
 */
import { useEffect } from 'react';
import { useToast, ToastType } from '../components/ui/Toast';

export function useForegroundNotifications() {
  const { addToast } = useToast();

  useEffect(() => {
    if (!('serviceWorker' in navigator)) return;

    const handler = (event: MessageEvent) => {
      const data = event.data;
      if (!data || data.type !== 'PUSH_RECEIVED') return;

      const notifType: ToastType =
        data.notificationType === 'BADGE_EARNED' ? 'success' :
        data.notificationType === 'STREAK_DANGER' ? 'warning' :
        'info';

      addToast({
        type: notifType,
        title: data.title || 'Notification',
        message: data.body || '',
        duration: 6000,
      });
    };

    navigator.serviceWorker.addEventListener('message', handler);
    return () => navigator.serviceWorker.removeEventListener('message', handler);
  }, [addToast]);
}
