/**
 * Mini-widget Dashboard : 3 barres T1/T2/T3 avec progression annuelle.
 *
 * Réutilise `groupByTrimesterWeek` (déjà testée iter 22) pour calculer les
 * totaux par trimestre, et navigue vers la page programme au clic.
 */
import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, CalendarDays } from 'lucide-react';
import { Card } from '../ui/Cards';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';
import { getCurrentTrimesterWeek } from '../../utils/schoolCalendar';
import { groupByTrimesterWeek } from './programTimeline';

interface Props {
  subjects: SubjectDTO[];
  skillsBySubject: Map<string, SkillDTO[]>;
  progress: SkillProgressDTO[];
  /**
   * Titre custom (par défaut « Tu en es là dans le programme » pour l'élève).
   * Le dashboard parent passe ex. « Où en est <Prénom> dans le programme ».
   */
  title?: string;
  /**
   * URL cible du lien « Détail → ». Si omise, le widget reste statique
   * (cas parent qui n'a pas la route élève accessible).
   */
  programmeHref?: string;
  /** Label aria pour le lien (override quand le titre change). */
  linkAriaLabel?: string;
}

export const ProgressByTrimester: React.FC<Props> = ({
  subjects,
  skillsBySubject,
  progress,
  title = 'Tu en es là dans le programme',
  programmeHref,
  linkAriaLabel = 'Voir tout mon programme',
}) => {
  const navigate = useNavigate();
  const calendar = useMemo(() => getCurrentTrimesterWeek(), []);
  const trimesters = useMemo(
    () => groupByTrimesterWeek(subjects, skillsBySubject, progress, calendar),
    [subjects, skillsBySubject, progress, calendar],
  );

  // N'affiche rien tant que le séquencement n'a pas encore de données.
  const totalSequenced = trimesters.reduce((acc, t) => acc + t.totals.total, 0);
  if (totalSequenced === 0) return null;

  const interactive = Boolean(programmeHref);

  const Header = (
    <div className="flex items-center justify-between gap-3 mb-4">
      <div className="flex items-center gap-2">
        <CalendarDays size={20} className="text-sitou-primary" />
        <h3 className="text-base md:text-lg font-extrabold text-gray-900 font-display">
          {title}
        </h3>
      </div>
      {interactive && (
        <span className="text-sm font-bold text-sitou-primary flex items-center gap-1 hover:gap-1.5 transition-all">
          D&eacute;tail <ArrowRight size={14} />
        </span>
      )}
    </div>
  );

  return (
    <Card className="bg-white border border-gray-200 shadow-clay">
      {interactive ? (
        <button
          type="button"
          onClick={() => navigate(programmeHref!)}
          className="w-full text-left"
          aria-label={linkAriaLabel}
        >
          {Header}
        </button>
      ) : (
        Header
      )}

      <ul className="space-y-3" data-testid="trimester-progress-list">
        {trimesters.map(tri => {
          const total = tri.totals.total;
          const mastered = tri.totals.mastered;
          const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
          return (
            <li key={tri.trimester}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-semibold text-gray-700">
                  Trimestre {tri.trimester}
                  {tri.isCurrent && (
                    <span className="ml-2 text-xs font-bold uppercase tracking-wide text-amber-700">
                      &middot; en cours
                    </span>
                  )}
                </span>
                <span className="text-xs font-bold text-gray-700">
                  {mastered}/{total} <span className="text-gray-500 font-medium">({pct}%)</span>
                </span>
              </div>
              <div
                className="w-full h-2 rounded-full bg-gray-100 overflow-hidden"
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Progression Trimestre ${tri.trimester}`}
              >
                <div
                  className={`h-full rounded-full transition-all duration-500 ${tri.isCurrent ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>
    </Card>
  );
};
