import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within a ToastProvider');
  return context;
};

// --- Toast Item Component ---
const ToastItem: React.FC<{ toast: Toast; onClose: () => void }> = ({ toast, onClose }) => {
  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(onClose, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.duration, onClose]);

  const styles = {
    success: 'bg-white border-l-4 border-green-500 text-gray-800',
    error: 'bg-white border-l-4 border-red-500 text-gray-800',
    warning: 'bg-white border-l-4 border-yellow-500 text-gray-800',
    info: 'bg-white border-l-4 border-ilma-primary text-gray-800'
  };

  const icons = {
    success: <CheckCircle size={20} className="text-green-500" />,
    error: <AlertCircle size={20} className="text-red-500" />,
    warning: <AlertTriangle size={20} className="text-yellow-500" />,
    info: <Info size={20} className="text-ilma-primary" />
  };

  return (
    <div role="alert" className={`flex items-start p-4 rounded-lg shadow-float mb-3 min-w-[300px] max-w-sm animate-slide-in-right ${styles[toast.type]}`}>
      <div className="mr-3 mt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        <h4 className="font-bold text-sm">{toast.title}</h4>
        {toast.message && <p className="text-xs text-gray-500 mt-1">{toast.message}</p>}
      </div>
      <button onClick={onClose} className="ml-3 text-gray-400 hover:text-gray-600">
        <X size={16} />
      </button>
    </div>
  );
};

// --- Provider ---
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback(({ type, title, message, duration = 5000 }: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, type, title, message, duration }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-[9999] flex flex-col items-end pointer-events-none">
        <div className="pointer-events-auto" role="region" aria-label="Notifications" aria-live="polite">
            {toasts.map(toast => (
            <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
            ))}
        </div>
      </div>
    </ToastContext.Provider>
  );
};
