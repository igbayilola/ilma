import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Drawer } from '../../components/ui/Drawer';
import { Skeleton } from '../../components/ui/Skeleton';
import { Trophy, Lock, Star } from 'lucide-react';
import { progressService, BadgeDTO } from '../../services/progressService';

export const BadgesPage: React.FC = () => {
  const [badges, setBadges] = useState<BadgeDTO[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBadge, setSelectedBadge] = useState<BadgeDTO | null>(null);

  useEffect(() => {
    progressService.getMyBadges()
      .then(setBadges)
      .catch(() => setBadges([]))
      .finally(() => setIsLoading(false));
  }, []);

  const unlockedCount = badges.filter(b => b.progress >= 100).length;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} variant="rect" className="h-48" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-2 font-display">&#127942; Mes Badges</h1>
            <p className="text-gray-500">Collectionne-les tous !</p>
        </div>
        <div className="gradient-gold text-white px-4 py-2 rounded-2xl font-bold flex items-center shadow-lg">
            <Trophy size={20} className="mr-2" />
            {unlockedCount} / {badges.length}
        </div>
      </header>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {badges.map((badge) => {
          const isUnlocked = badge.progress >= 100;
          return (
            <Card
              key={badge.id}
              interactive
              onClick={() => setSelectedBadge(badge)}
              className={`flex flex-col items-center justify-center p-6 text-center h-48 relative overflow-hidden group ${!isUnlocked ? 'bg-gray-50' : 'bg-white clay-card'}`}
            >
              <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110
                  ${isUnlocked ? 'bg-gradient-to-br from-yellow-100 via-amber-50 to-orange-100 text-yellow-600 border-2 border-yellow-300 shadow-md' : 'bg-gray-200 text-gray-400 grayscale'}
              `}>
                {isUnlocked ? <Trophy size={32} /> : <Lock size={24} />}
              </div>

              <h3 className={`font-bold text-sm ${isUnlocked ? 'text-gray-800' : 'text-gray-400'}`}>{badge.name}</h3>

              {!isUnlocked && (
                  <div className="mt-2 w-full max-w-[80px] h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div className="gradient-xp h-full rounded-full" style={{ width: `${badge.progress}%` }} />
                  </div>
              )}

              {isUnlocked && (
                  <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Star size={16} className="text-yellow-400 fill-yellow-400 animate-pop" />
                  </div>
              )}
            </Card>
          );
        })}
      </div>

      {badges.length === 0 && (
        <div className="text-center py-12 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-3xl border border-dashed border-yellow-200">
          <div className="text-5xl mb-4">&#127941;</div>
          <p className="text-gray-500 font-medium">Aucun badge disponible. Commence &agrave; t'entra&icirc;ner !</p>
        </div>
      )}

      <Drawer
        isOpen={!!selectedBadge}
        onClose={() => setSelectedBadge(null)}
        title={selectedBadge?.progress && selectedBadge.progress >= 100 ? "Badge D\u00e9bloqu\u00e9 !" : "Badge Verrouill\u00e9"}
      >
        {selectedBadge && (
            <div className="flex flex-col items-center text-center p-4">
                <div className={`w-32 h-32 rounded-full flex items-center justify-center mb-6 shadow-float
                    ${selectedBadge.progress >= 100 ? 'bg-gradient-to-br from-yellow-100 via-amber-50 to-orange-100 text-yellow-600 border-4 border-white ring-4 ring-yellow-50' : 'bg-gray-100 text-gray-400'}
                `}>
                    <Trophy size={64} />
                </div>

                <h2 className="text-2xl font-extrabold text-gray-900 mb-2 font-display">{selectedBadge.name}</h2>
                <p className="text-gray-600 text-lg mb-8 max-w-xs">{selectedBadge.description}</p>

                {selectedBadge.progress >= 100 ? (
                    <div className="w-full bg-green-50 border border-green-100 rounded-2xl p-4 mb-4">
                        <p className="text-green-800 font-bold text-sm">
                            Obtenu le {selectedBadge.unlockedAt ? new Date(selectedBadge.unlockedAt).toLocaleDateString('fr-FR') : ''}
                        </p>
                    </div>
                ) : (
                    <div className="w-full space-y-2">
                        <div className="flex justify-between text-sm font-bold text-gray-500">
                            <span>Progression</span>
                            <span>{selectedBadge.current} / {selectedBadge.total}</span>
                        </div>
                        <div className="w-full h-4 bg-gray-100 rounded-full overflow-hidden">
                             <div className="h-full gradient-xp rounded-full" style={{ width: `${selectedBadge.progress}%` }} />
                        </div>
                    </div>
                )}
            </div>
        )}
      </Drawer>
    </div>
  );
};
