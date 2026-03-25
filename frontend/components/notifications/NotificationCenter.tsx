import React, { useState } from 'react';
import { Drawer } from '../ui/Drawer';
import { useAppStore } from '../../store';
import { NotificationItem } from './NotificationItem';
import { Button } from '../ui/Button';
import { ButtonVariant } from '../../types';
import { Check, BellOff, Filter } from 'lucide-react';
import { useSync } from '../../contexts/SyncContext';

export const NotificationCenter: React.FC = () => {
  const { 
    isNotificationOpen, 
    setNotificationOpen, 
    notifications, 
    markAllNotificationsAsRead 
  } = useAppStore();
  
  const { enqueueAction } = useSync();
  const [filterUnread, setFilterUnread] = useState(false);

  const filteredNotifications = filterUnread 
    ? notifications.filter(n => !n.read) 
    : notifications;

  const unreadCount = notifications.filter(n => !n.read).length;

  const handleMarkAllRead = () => {
    markAllNotificationsAsRead();
    // In a real app, optimize this to send one bulk action or just rely on local state update + periodic sync
    notifications.filter(n => !n.read).forEach(n => {
        enqueueAction('notification_read', { id: n.id });
    });
  };

  return (
    <Drawer 
      isOpen={isNotificationOpen} 
      onClose={() => setNotificationOpen(false)} 
      title="Notifications"
      position="right"
    >
      <div className="flex flex-col h-full">
        {/* Actions Header */}
        <div className="flex items-center justify-between mb-4">
            <button 
                onClick={() => setFilterUnread(!filterUnread)}
                className={`flex items-center text-xs font-bold px-3 py-1.5 rounded-full border transition-colors ${filterUnread ? 'bg-sitou-primary text-white border-sitou-primary' : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'}`}
            >
                <Filter size={12} className="mr-1.5" />
                {filterUnread ? 'Non lues uniquement' : 'Toutes'}
            </button>
            
            {unreadCount > 0 && (
                <button 
                    onClick={handleMarkAllRead}
                    className="flex items-center text-xs font-bold text-sitou-primary hover:text-amber-700"
                >
                    <Check size={14} className="mr-1" /> Tout marquer comme lu
                </button>
            )}
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto -mx-2 px-2 pb-safe">
            {filteredNotifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-center text-gray-400">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <BellOff size={24} />
                    </div>
                    <p className="text-sm font-medium">Aucune notification {filterUnread ? 'non lue' : ''}.</p>
                </div>
            ) : (
                filteredNotifications.map(notif => (
                    <NotificationItem 
                        key={notif.id} 
                        notification={notif} 
                        onClick={() => setNotificationOpen(false)}
                    />
                ))
            )}
        </div>
      </div>
    </Drawer>
  );
};