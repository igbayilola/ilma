import React from 'react';

interface Tab {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange, className = '' }) => {
  return (
    <div
      role="tablist"
      aria-label="Onglets"
      className={`flex space-x-1 border-b border-gray-200 mb-6 overflow-x-auto no-scrollbar ${className}`}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`tabpanel-${tab.id}`}
          id={`tab-${tab.id}`}
          onClick={() => onChange(tab.id)}
          className={`
            pb-3 px-4 text-sm font-bold whitespace-nowrap transition-colors border-b-2 flex-shrink-0
            ${activeTab === tab.id
              ? 'border-sitou-primary text-sitou-primary'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
          `}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};
