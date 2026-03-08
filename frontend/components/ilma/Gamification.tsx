import React from 'react';
import { Flame } from 'lucide-react';

export const LEVEL_NAMES: Record<number, string> = {
  1: 'Apprenti', 2: 'Apprenti',
  3: 'Écolier brillant', 4: 'Écolier brillant',
  5: 'As du calcul', 6: 'As du calcul',
  7: 'Champion du village', 8: 'Champion du village',
  9: 'Fierté de l\'école', 10: 'Fierté de l\'école',
  11: 'Major du Bénin', 12: 'Major du Bénin',
};

interface SmartScoreMeterProps {
  score: number;
}

export const SmartScoreMeter: React.FC<SmartScoreMeterProps> = ({ score }) => {
  const getColor = (s: number) => {
    if (s >= 80) return '#D97706';
    if (s >= 50) return '#F59E0B';
    return '#94a3b8';
  };

  const getTextClass = (s: number) => {
    if (s >= 80) return 'text-ilma-primary';
    if (s >= 50) return 'text-ilma-orange';
    return 'text-gray-400';
  };

  return (
    <div
        className="flex flex-col items-center justify-center relative w-16 h-16"
        role="img"
        aria-label={`Score de comp\u00e9tence: ${score} sur 100`}
    >
       <svg className="w-full h-full" viewBox="0 0 36 36" aria-hidden="true">
        <path
          className="text-gray-200"
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="3.5"
          strokeLinecap="round"
        />
        <path
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke={getColor(score)}
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeDasharray={`${score}, 100`}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-sm font-bold ${getTextClass(score)}`}>{score}</span>
        <span className="text-[8px] uppercase font-bold text-gray-400" aria-hidden="true">Score</span>
      </div>
    </div>
  );
};

interface XPBarProps {
  current: number;
  max: number;
  level: number;
}

export const XPBar: React.FC<XPBarProps> = ({ current, max, level }) => {
  const percentage = Math.min(100, Math.max(0, (current / max) * 100));

  return (
    <div
        className="w-full"
        role="progressbar"
        aria-valuenow={current}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={`Progression niveau ${level}`}
    >
      <div className="flex justify-between items-end mb-1" aria-hidden="true">
        <span className="text-xs font-bold text-ilma-primary uppercase tracking-wide">Niveau {level} — {LEVEL_NAMES[level] || 'Apprenti'}</span>
        <span className="text-xs text-gray-500">{current}/{max} XP</span>
      </div>
      <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden shadow-clay-sm">
        <div
          className="h-full gradient-xp rounded-full transition-all duration-500 ease-out relative"
          style={{ width: `${percentage}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0 animate-shimmer" style={{ backgroundSize: '200% 100%', animation: 'shimmer 2s linear infinite' }}></div>
        </div>
      </div>
    </div>
  );
};

interface StreakWidgetProps {
  days: number;
  active: boolean;
}

export const StreakWidget: React.FC<StreakWidgetProps> = ({ days, active }) => {
  return (
    <div
        className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border ${active ? 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200' : 'bg-gray-50 border-gray-200'}`}
        title={`${days} jours de suite`}
        role="status"
    >
      <Flame className={`w-5 h-5 ${active ? 'text-ilma-orange fill-ilma-orange' : 'text-gray-400'} ${days >= 7 ? 'animate-wiggle' : ''}`} />
      <span className={`font-bold ${active ? 'text-ilma-orange' : 'text-gray-400'}`}>
        {days} <span className="sr-only">jours de suite</span><span aria-hidden="true">jours</span>
      </span>
    </div>
  );
};
