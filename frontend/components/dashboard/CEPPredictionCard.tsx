import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, AlertTriangle, TrendingUp, ChevronRight } from 'lucide-react';
import { Card, Badge } from '../ui/Cards';
import { Skeleton } from '../ui/Skeleton';
import { examService, PredictiveScoreDTO } from '../../services/examService';

const PASS_THRESHOLD = 10; // /20 — admission CEP au Bénin

function getBand(predicted: number): { color: string; label: string; tone: string } {
  if (predicted >= 14) return { color: 'green', label: 'Très bien', tone: 'text-sitou-green' };
  if (predicted >= 12) return { color: 'blue', label: 'Bien', tone: 'text-blue-600' };
  if (predicted >= PASS_THRESHOLD) return { color: 'amber', label: 'Passable', tone: 'text-sitou-primary-dark' };
  return { color: 'red', label: 'À renforcer', tone: 'text-sitou-red' };
}

function confidenceLabel(c: number): string {
  if (c >= 0.7) return 'Estimation fiable';
  if (c >= 0.4) return 'Estimation indicative';
  return 'Pratique encore peu de questions';
}

export const CEPPredictionCard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<PredictiveScoreDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const resp = await examService.getPredictiveScore();
        if (!cancelled) setData(resp);
      } catch {
        if (!cancelled) setError('Impossible de calculer le score pour le moment.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <Card>
        <Skeleton className="h-6 w-40 mb-3" />
        <Skeleton className="h-16 w-32 mb-4" />
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-3/4" />
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <div className="flex items-center gap-2 text-gray-500">
          <AlertTriangle size={18} />
          <p className="text-sm">{error || 'Aucune donnée disponible.'}</p>
        </div>
      </Card>
    );
  }

  const band = getBand(data.predicted);
  const passing = data.predicted >= PASS_THRESHOLD;
  const gaugePct = Math.min(100, Math.round((data.predicted / 20) * 100));

  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-extrabold text-lg flex items-center gap-2">
          <Target size={20} className="text-sitou-primary" />
          Score CEP estimé
        </h3>
        <Badge label={band.label} color={band.color as any} size="sm" />
      </div>

      <div className="flex items-end gap-2 mb-1">
        <span className={`text-5xl font-black ${band.tone}`}>{data.predicted.toFixed(1)}</span>
        <span className="text-2xl font-bold text-gray-400 mb-1">/20</span>
      </div>

      <div
        className="w-full h-2 bg-gray-100 rounded-full overflow-hidden mb-2"
        role="meter"
        aria-valuenow={data.predicted}
        aria-valuemin={0}
        aria-valuemax={20}
        aria-label="Score CEP prédit sur 20"
      >
        <div
          className={`h-full transition-all duration-500 ${passing ? 'bg-sitou-green' : 'bg-sitou-red'}`}
          style={{ width: `${gaugePct}%` }}
        />
      </div>

      <p className="text-xs text-gray-500 mb-3">
        {confidenceLabel(data.confidence)} · couverture {Math.round(data.coverage * 100)} %
      </p>

      {data.weak_skills.length > 0 ? (
        <div className="mt-4 pt-4 border-t border-sitou-border">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1">
            <TrendingUp size={14} />
            À renforcer
          </p>
          <ul className="space-y-1.5">
            {data.weak_skills.map(ws => (
              <li key={ws.skill_id}>
                <button
                  type="button"
                  onClick={() => navigate(`/app/student/subjects/${ws.subject_id}/domains/${ws.domain_id}/skills/${ws.skill_id}`)}
                  className="w-full flex items-center justify-between text-left px-3 py-2 rounded-xl bg-red-50 hover:bg-red-100 border border-red-100 transition-all group"
                >
                  <span className="text-sm font-medium text-gray-800 truncate">{ws.name}</span>
                  <span className="flex items-center gap-2 flex-shrink-0 ml-2">
                    <span className="text-xs font-bold text-sitou-red">{Math.round(ws.smart_score)}%</span>
                    <ChevronRight size={14} className="text-gray-400 group-hover:text-sitou-red transition-colors" />
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="text-sm text-gray-500 mt-4 pt-4 border-t border-sitou-border">
          {data.coverage > 0
            ? "Aucun point faible détecté — continue à pratiquer !"
            : "Commence à pratiquer pour obtenir une estimation."}
        </p>
      )}
    </Card>
  );
};
