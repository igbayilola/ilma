import React from 'react';
import { AppNotification, NotificationType } from '../../types';
import { Flame, Trophy, FileText, Bell, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store';
import { useSync } from '../../contexts/SyncContext';

interface NotificationItemProps {
  notification: AppNotification;
  onClick?: () => void;
}

export const NotificationItem: React.FC<NotificationItemProps> = ({ notification, onClick }) => {
  const navigate = useNavigate();
  const { markNotificationAsRead } = useAppStore();
  const { enqueueAction } = useSync();

  const handleClick = () => {
    if (!notification.read) {
        markNotificationAsRead(notification.id);
        enqueueAction('notification_read', { id: notification.id });
    }
    if (onClick) onClick();
    if (notification.actionUrl) {
        navigate(notification.actionUrl);
    }
  };

  const getIcon = () => {
    switch (notification.type) {
      case NotificationType.STREAK_DANGER:
        return <Flame className="text-white fill-current" size={20} />;
      case NotificationType.BADGE_EARNED:
        return <Trophy className="text-white fill-current" size={20} />;
      case NotificationType.REPORT_READY:
        return <FileText className="text-white" size={20} />;
      case NotificationType.SYSTEM:
      default:
        return <Bell className="text-white" size={20} />;
    }
  };

  const getStyles = () => {
    switch (notification.type) {
      case NotificationType.STREAK_DANGER:
        return {
          bg: 'bg-red-50 hover:bg-red-100',
          iconBg: 'bg-red-500',
          border: 'border-red-100'
        };
      case NotificationType.BADGE_EARNED:
        return {
          bg: 'bg-yellow-50 hover:bg-yellow-100',
          iconBg: 'bg-yellow-500',
          border: 'border-yellow-100'
        };
      case NotificationType.REPORT_READY:
        return {
          bg: 'bg-blue-50 hover:bg-blue-100',
          iconBg: 'bg-blue-500',
          border: 'border-blue-100'
        };
      default:
        return {
          bg: 'bg-white hover:bg-gray-50',
          iconBg: 'bg-gray-400',
          border: 'border-gray-100'
        };
    }
  };

  const styles = getStyles();
  const timeAgo = new Date(notification.timestamp).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) + 
                  ' ' + new Date(notification.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

  return (
    <div 
        onClick={handleClick}
        className={`relative flex p-4 rounded-xl cursor-pointer transition-all border mb-3 ${styles.bg} ${styles.border} ${!notification.read ? 'border-l-4 border-l-sitou-primary shadow-sm' : ''}`}
    >
      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 mr-4 shadow-sm ${styles.iconBg}`}>
        {getIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className={`text-sm font-bold mb-0.5 ${!notification.read ? 'text-gray-900' : 'text-gray-600'}`}>
            {notification.title}
        </h4>
        <p className={`text-xs leading-relaxed ${!notification.read ? 'text-gray-700' : 'text-gray-500'}`}>
            {notification.message}
        </p>
        <span className="text-[10px] text-gray-400 mt-2 block font-medium uppercase">
            {timeAgo}
        </span>
      </div>

      {!notification.read && (
        <div className="absolute top-4 right-4 w-2 h-2 bg-sitou-primary rounded-full"></div>
      )}
    </div>
  );
};