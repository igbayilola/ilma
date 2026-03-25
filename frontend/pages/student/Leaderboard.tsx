import React, { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Cards';
import { Skeleton } from '../../components/ui/Skeleton';
import { Trophy, Medal, Crown, Star, Zap, Swords, Share2, History } from 'lucide-react';
import { socialService, LeaderboardData, ChallengeDTO, LeaderboardHistoryEntry } from '../../services/socialService';

const RANK_STYLES: Record<number, { icon: React.ReactNode; bg: string; text: string }> = {
  1: { icon: <Crown size={18} className="text-yellow-500 fill-yellow-500" />, bg: 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200', text: 'text-yellow-700' },
  2: { icon: <Medal size={18} className="text-gray-400" />, bg: 'bg-gray-50 border-gray-200', text: 'text-gray-600' },
  3: { icon: <Medal size={18} className="text-amber-600" />, bg: 'bg-orange-50 border-orange-200', text: 'text-orange-700' },
};

export const LeaderboardPage: React.FC = () => {
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [challenges, setChallenges] = useState<ChallengeDTO[]>([]);
  const [history, setHistory] = useState<LeaderboardHistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'classement' | 'defis' | 'historique'>('classement');

  useEffect(() => {
    Promise.all([
      socialService.getWeeklyLeaderboard().catch(() => null),
      socialService.getMyChallenges().catch(() => []),
      socialService.getLeaderboardHistory().catch(() => []),
    ]).then(([lb, ch, hist]) => {
      setData(lb);
      setChallenges(ch);
      setHistory(hist);
    }).finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton variant="text" className="w-48 h-8" />
        {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} variant="rect" className="h-16" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20 md:pb-0">
      <header>
        <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 font-display">Classement</h1>
        <p className="text-gray-500 text-sm mt-1">Semaine {data?.week || '...'}</p>
      </header>

      {/* Tabs */}
      <div className="flex bg-gray-100 rounded-xl p-1">
        <button
          onClick={() => setActiveTab('classement')}
          className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${
            activeTab === 'classement' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500'
          }`}
        >
          <Trophy size={16} className="inline mr-1" /> Classement
        </button>
        <button
          onClick={() => setActiveTab('defis')}
          className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${
            activeTab === 'defis' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500'
          }`}
        >
          <Swords size={16} className="inline mr-1" /> Défis
          {challenges.filter(c => c.status === 'pending' && !c.is_challenger).length > 0 && (
            <span className="ml-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 inline-flex items-center justify-center">
              {challenges.filter(c => c.status === 'pending' && !c.is_challenger).length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('historique')}
          className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${
            activeTab === 'historique' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500'
          }`}
        >
          <History size={16} className="inline mr-1" /> Historique
        </button>
      </div>

      {activeTab === 'classement' && (
        <>
          {/* My position card */}
          {data?.my_rank && (
            <Card className="bg-gradient-to-r from-sitou-primary/10 to-amber-50 border-sitou-primary/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 font-medium">Ta position</p>
                  <p className="text-2xl font-extrabold text-gray-900">#{data.my_rank}</p>
                  <p className="text-sm font-medium text-gray-600">{data.my_pseudonym}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-sitou-primary font-bold text-lg">
                    <Zap size={20} className="fill-sitou-primary" />
                    {data.my_xp} XP
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Leaderboard entries */}
          <div className="space-y-2">
            {data?.entries.map((entry) => {
              const style = RANK_STYLES[entry.rank];
              return (
                <div
                  key={entry.rank}
                  className={`flex items-center p-3 rounded-xl border transition-all ${
                    entry.is_me
                      ? 'bg-sitou-primary/5 border-sitou-primary/30 ring-2 ring-sitou-primary/20'
                      : style?.bg || 'bg-white border-gray-100'
                  }`}
                >
                  {/* Rank */}
                  <div className="w-10 text-center flex-shrink-0">
                    {style?.icon || (
                      <span className="text-sm font-bold text-gray-400">{entry.rank}</span>
                    )}
                  </div>

                  {/* Pseudonym */}
                  <div className="flex-1 ml-3">
                    <p className={`font-bold text-sm ${entry.is_me ? 'text-sitou-primary' : style?.text || 'text-gray-700'}`}>
                      {entry.pseudonym}
                      {entry.is_me && <span className="text-xs ml-1 opacity-60">(Toi)</span>}
                    </p>
                  </div>

                  {/* XP */}
                  <div className="flex items-center gap-1 font-bold text-sm text-gray-600">
                    <Star size={14} className="text-yellow-400 fill-yellow-400" />
                    {entry.xp_earned}
                  </div>
                </div>
              );
            })}

            {(!data?.entries || data.entries.length === 0) && (
              <div className="text-center py-12 bg-gray-50 rounded-2xl">
                <Trophy size={48} className="mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500 font-medium">Le classement commence cette semaine !</p>
                <p className="text-gray-400 text-sm mt-1">Fais des exercices pour gagner des XP.</p>
              </div>
            )}
          </div>
        </>
      )}

      {activeTab === 'historique' && (
        <div className="space-y-3">
          {history.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-2xl">
              <History size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">Pas encore d'historique</p>
              <p className="text-gray-400 text-sm mt-1">Tes résultats hebdomadaires apparaîtront ici.</p>
            </div>
          ) : (
            history.map(h => (
              <div
                key={h.week}
                className={`flex items-center p-4 rounded-xl border transition-all ${
                  h.is_current
                    ? 'bg-sitou-primary/5 border-sitou-primary/30'
                    : 'bg-white border-gray-100'
                }`}
              >
                <div className="flex-1">
                  <p className="font-bold text-sm text-gray-800">
                    Semaine {h.week}
                    {h.is_current && <span className="text-xs text-sitou-primary ml-2">(en cours)</span>}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {h.pseudonym} &middot; {h.total_participants} participant{h.total_participants > 1 ? 's' : ''}
                  </p>
                </div>
                <div className="text-right">
                  {h.rank && (
                    <p className="font-bold text-sm text-gray-700">#{h.rank}</p>
                  )}
                  <div className="flex items-center gap-1 text-xs text-sitou-primary font-bold">
                    <Zap size={12} className="fill-sitou-primary" />
                    {h.xp_earned} XP
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'defis' && (
        <div className="space-y-3">
          {/* Share challenge button */}
          <button
            onClick={async () => {
              const text = `Je te défie sur Sitou ! Viens montrer ce que tu sais faire 🎓⚔️`;
              const url = window.location.origin;
              if (navigator.share) {
                await navigator.share({ title: 'Défi Sitou', text, url }).catch(() => {});
              } else {
                await navigator.clipboard.writeText(`${text}\n${url}`).catch(() => {});
              }
            }}
            className="w-full flex items-center justify-center gap-2 p-3 bg-gradient-to-r from-sitou-primary to-amber-500 text-white rounded-xl font-bold text-sm shadow-md hover:opacity-90 transition-opacity"
          >
            <Share2 size={16} />
            Défier un ami
          </button>

          {challenges.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-2xl">
              <Swords size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">Pas encore de défis</p>
              <p className="text-gray-400 text-sm mt-1">Défie tes amis en partageant un lien !</p>
            </div>
          ) : (
            challenges.map(ch => (
              <Card key={ch.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-sm text-gray-800">
                      {ch.is_challenger ? 'Défi envoyé' : 'Défi reçu'}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {ch.status === 'pending' && 'En attente'}
                      {ch.status === 'accepted' && 'Accepté — en cours'}
                      {ch.status === 'completed' && (
                        <>Terminé — {ch.challenger_score ?? 0} vs {ch.challenged_score ?? 0}</>
                      )}
                      {ch.status === 'expired' && 'Expiré'}
                    </p>
                  </div>
                  <div className={`px-2 py-1 rounded-lg text-xs font-bold ${
                    ch.status === 'completed' ? 'bg-green-100 text-green-700' :
                    ch.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                    ch.status === 'expired' ? 'bg-gray-100 text-gray-500' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {ch.status}
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
};
