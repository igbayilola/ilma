import React, { useState, useEffect, useMemo } from 'react';
import { Card } from '../../components/ui/Cards';
import { Drawer } from '../../components/ui/Drawer';
import { Skeleton } from '../../components/ui/Skeleton';
import { Trophy, Lock, Star, ChevronRight } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

interface BadgeProgress {
  current: number;
  target: number;
}

interface CollectionBadge {
  badge_code: string;
  badge_name: string;
  description: string;
  icon: string;
  category: string;
  earned: boolean;
  awarded_at: string | null;
  progress: BadgeProgress | null;
}

const CATEGORY_META: Record<string, { label: string; emoji: string; color: string; bg: string }> = {
  streak: { label: 'Régularité', emoji: '🔥', color: 'text-orange-600', bg: 'bg-orange-50' },
  mastery: { label: 'Maîtrise', emoji: '⭐', color: 'text-yellow-600', bg: 'bg-yellow-50' },
  exploration: { label: 'Exploration', emoji: '🌍', color: 'text-blue-600', bg: 'bg-blue-50' },
  cep: { label: 'CEP', emoji: '🎓', color: 'text-purple-600', bg: 'bg-purple-50' },
  social: { label: 'Social', emoji: '⚔️', color: 'text-pink-600', bg: 'bg-pink-50' },
  special: { label: 'Spécial', emoji: '💎', color: 'text-emerald-600', bg: 'bg-emerald-50' },
  completion: { label: 'Complétion', emoji: '✅', color: 'text-green-600', bg: 'bg-green-50' },
};

const CATEGORY_ORDER = ['streak', 'mastery', 'exploration', 'cep', 'social', 'special', 'completion'];

export const BadgesPage: React.FC = () => {
  const [badges, setBadges] = useState<CollectionBadge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBadge, setSelectedBadge] = useState<CollectionBadge | null>(null);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  useEffect(() => {
    apiClient.get<CollectionBadge[]>('/students/me/badges/collection')
      .then(data => setBadges(data || []))
      .catch(() => setBadges([]))
      .finally(() => setIsLoading(false));
  }, []);

  const grouped = useMemo(() => {
    const map: Record<string, CollectionBadge[]> = {};
    for (const b of badges) {
      (map[b.category] ??= []).push(b);
    }
    return map;
  }, [badges]);

  const categories = useMemo(() =>
    CATEGORY_ORDER.filter(c => grouped[c]?.length),
    [grouped]
  );

  const earnedTotal = badges.filter(b => b.earned).length;

  const displayedCategories = activeCategory
    ? categories.filter(c => c === activeCategory)
    : categories;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <div className="grid grid-cols-3 gap-3">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} variant="rect" className="h-36" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20 md:pb-0">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">Mes Badges</h1>
          <p className="text-gray-500 text-sm mt-1">Collectionne-les tous !</p>
        </div>
        <div className="gradient-gold text-white px-4 py-2 rounded-2xl font-bold flex items-center shadow-lg text-sm">
          <Trophy size={18} className="mr-1.5" />
          {earnedTotal} / {badges.length}
        </div>
      </header>

      {/* Category filter chips */}
      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-hide">
        <button
          onClick={() => setActiveCategory(null)}
          className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
            !activeCategory
              ? 'bg-gray-900 text-white shadow-md'
              : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          }`}
        >
          Tous
        </button>
        {categories.map(cat => {
          const meta = CATEGORY_META[cat] || { label: cat, emoji: '', color: 'text-gray-600', bg: 'bg-gray-50' };
          const earned = grouped[cat]?.filter(b => b.earned).length || 0;
          const total = grouped[cat]?.length || 0;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition-all flex items-center gap-1 ${
                activeCategory === cat
                  ? 'bg-gray-900 text-white shadow-md'
                  : `${meta.bg} ${meta.color} hover:opacity-80`
              }`}
            >
              <span>{meta.emoji}</span>
              <span>{meta.label}</span>
              <span className="opacity-60">{earned}/{total}</span>
            </button>
          );
        })}
      </div>

      {/* Badge grid by category */}
      {displayedCategories.map(cat => {
        const meta = CATEGORY_META[cat] || { label: cat, emoji: '', color: 'text-gray-600', bg: 'bg-gray-50' };
        const catBadges = grouped[cat] || [];
        return (
          <section key={cat}>
            <h2 className={`text-sm font-bold uppercase tracking-wider mb-3 flex items-center gap-1.5 ${meta.color}`}>
              <span>{meta.emoji}</span>
              <span>{meta.label}</span>
            </h2>
            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {catBadges.map(badge => (
                <button
                  key={badge.badge_code}
                  onClick={() => setSelectedBadge(badge)}
                  className={`flex flex-col items-center justify-center p-4 rounded-2xl text-center h-36 relative overflow-hidden group transition-all duration-200 ${
                    badge.earned
                      ? 'bg-white shadow-sm hover:shadow-md border border-gray-100'
                      : 'bg-gray-50 hover:bg-gray-100 border border-gray-100'
                  }`}
                >
                  {/* Badge icon */}
                  <div className={`text-3xl mb-2 transition-transform duration-300 group-hover:scale-110 ${
                    !badge.earned ? 'grayscale opacity-30' : ''
                  }`}>
                    {badge.icon}
                  </div>

                  {/* Lock overlay for unearned */}
                  {!badge.earned && (
                    <div className="absolute top-2 right-2">
                      <Lock size={12} className="text-gray-300" />
                    </div>
                  )}

                  <h3 className={`font-bold text-xs leading-tight ${
                    badge.earned ? 'text-gray-800' : 'text-gray-400'
                  }`}>
                    {badge.badge_name}
                  </h3>

                  {/* Progress bar for unearned badges */}
                  {!badge.earned && badge.progress && badge.progress.target > 0 && (
                    <div className="w-full mt-1.5 px-1">
                      <div className="w-full bg-gray-200 h-1 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-ilma-primary/60 rounded-full transition-all"
                          style={{ width: `${Math.min(100, Math.round((badge.progress.current / badge.progress.target) * 100))}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-gray-400 mt-0.5">{badge.progress.current}/{badge.progress.target}</p>
                    </div>
                  )}

                  {/* Earned indicator */}
                  {badge.earned && (
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Star size={14} className="text-yellow-400 fill-yellow-400" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </section>
        );
      })}

      {badges.length === 0 && (
        <div className="text-center py-12 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-3xl border border-dashed border-yellow-200">
          <div className="text-5xl mb-4">&#127941;</div>
          <p className="text-gray-500 font-medium">Aucun badge disponible. Commence &agrave; t'entra&icirc;ner !</p>
        </div>
      )}

      {/* Badge detail drawer */}
      <Drawer
        isOpen={!!selectedBadge}
        onClose={() => setSelectedBadge(null)}
        title={selectedBadge?.earned ? 'Badge Débloqué !' : 'Badge Verrouillé'}
      >
        {selectedBadge && (
          <div className="flex flex-col items-center text-center p-4">
            {/* Large icon */}
            <div className={`w-28 h-28 rounded-full flex items-center justify-center mb-6 transition-all ${
              selectedBadge.earned
                ? 'bg-gradient-to-br from-yellow-100 via-amber-50 to-orange-100 border-4 border-white ring-4 ring-yellow-50 shadow-lg'
                : 'bg-gray-100 border-4 border-gray-200'
            }`}>
              <span className={`text-5xl ${!selectedBadge.earned ? 'grayscale opacity-30' : ''}`}>
                {selectedBadge.icon}
              </span>
            </div>

            <h2 className="text-2xl font-extrabold text-gray-900 mb-2 font-display">
              {selectedBadge.badge_name}
            </h2>
            <p className="text-gray-600 mb-6 max-w-xs">{selectedBadge.description}</p>

            {/* Category tag */}
            {(() => {
              const meta = CATEGORY_META[selectedBadge.category];
              return meta ? (
                <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold mb-6 ${meta.bg} ${meta.color}`}>
                  <span>{meta.emoji}</span>
                  <span>{meta.label}</span>
                </div>
              ) : null;
            })()}

            {selectedBadge.earned ? (
              <div className="w-full bg-green-50 border border-green-100 rounded-2xl p-4">
                <p className="text-green-800 font-bold text-sm flex items-center justify-center gap-2">
                  <Star size={16} className="text-green-500 fill-green-500" />
                  Obtenu le {selectedBadge.awarded_at
                    ? new Date(selectedBadge.awarded_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
                    : ''}
                </p>
              </div>
            ) : (
              <div className="w-full space-y-3">
                {selectedBadge.progress && selectedBadge.progress.target > 0 && (
                  <div className="bg-ilma-primary/5 border border-ilma-primary/20 rounded-2xl p-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="font-bold text-gray-700">Progression</span>
                      <span className="font-bold text-ilma-primary">
                        {selectedBadge.progress.current} / {selectedBadge.progress.target}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 h-2.5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-ilma-primary to-amber-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(100, Math.round((selectedBadge.progress.current / selectedBadge.progress.target) * 100))}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1.5 text-center">
                      Encore {Math.max(0, selectedBadge.progress.target - selectedBadge.progress.current)} pour débloquer !
                    </p>
                  </div>
                )}
                <div className="bg-gray-50 border border-gray-100 rounded-2xl p-4">
                  <p className="text-gray-500 text-sm flex items-center justify-center gap-2">
                    <Lock size={14} />
                    Continue tes exercices pour débloquer ce badge !
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};
