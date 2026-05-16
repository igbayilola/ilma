/**
 * Vue « Mon programme » — composant visuel.
 *
 * Affiche T1/T2/T3 en sections empilées, chaque trimestre listant ses
 * semaines avec les skills coloriés selon leur statut :
 *  - maîtrisé (vert)
 *  - en cours (ambre)
 *  - à faire (bleu)
 *  - à venir / verrouillé (gris)
 *
 * La fonction de regroupement est extraite dans {@link programTimeline.ts}
 * pour pouvoir la tester sans DOM.
 */
import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Circle, Clock, Lock, CalendarDays } from 'lucide-react';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';
import { getCurrentTrimesterWeek, formatTrimesterWeek } from '../../utils/schoolCalendar';
import {
  groupByTrimesterWeek,
  type SkillStatus,
  type TimelineSkill,
  type TimelineTrimester,
} from './programTimeline';

interface Props {
  subjects: SubjectDTO[];
  skillsBySubject: Map<string, SkillDTO[]>;
  progress: SkillProgressDTO[];
}

const STATUS_META: Record<
  SkillStatus,
  { label: string; bg: string; text: string; icon: React.ReactNode }
> = {
  mastered: {
    label: 'Maîtrisé',
    bg: 'bg-emerald-50 border-emerald-200',
    text: 'text-emerald-700',
    icon: <CheckCircle size={16} className="text-emerald-600" />,
  },
  inProgress: {
    label: 'En cours',
    bg: 'bg-amber-50 border-amber-200',
    text: 'text-amber-700',
    icon: <Clock size={16} className="text-amber-600" />,
  },
  upcoming: {
    label: 'À faire',
    bg: 'bg-sky-50 border-sky-200',
    text: 'text-sky-700',
    icon: <Circle size={16} className="text-sky-600" />,
  },
  future: {
    label: 'Plus tard',
    bg: 'bg-gray-50 border-gray-200',
    text: 'text-gray-500',
    icon: <Lock size={14} className="text-gray-400" />,
  },
};

const SkillRow: React.FC<{ item: TimelineSkill }> = ({ item }) => {
  const navigate = useNavigate();
  const meta = STATUS_META[item.status];
  const goTo = () => {
    if (item.status === 'future') return;
    navigate(
      `/app/student/subjects/${item.subject.id}/domains/${item.skill.domainId}/skills/${item.skill.id}`,
    );
  };
  const interactive = item.status !== 'future';
  return (
    <button
      type="button"
      onClick={goTo}
      disabled={!interactive}
      className={`w-full text-left flex items-center gap-3 p-3 rounded-xl border ${meta.bg} ${interactive ? 'hover:shadow-clay transition-shadow cursor-pointer' : 'cursor-not-allowed opacity-80'}`}
      aria-disabled={!interactive}
    >
      <span className="flex-shrink-0">{meta.icon}</span>
      <span className="flex-1 min-w-0">
        <span className="block text-xs font-medium text-gray-500 truncate">
          {item.subject.emoji ? `${item.subject.emoji} ` : ''}{item.subject.name}
        </span>
        <span className={`block text-sm font-semibold ${meta.text} truncate`}>
          {item.skill.name}
        </span>
      </span>
      {item.status === 'inProgress' && (
        <span className="text-xs font-bold text-amber-700">{item.score}%</span>
      )}
    </button>
  );
};

const TrimesterBlock: React.FC<{ tri: TimelineTrimester }> = ({ tri }) => {
  const masteryPct =
    tri.totals.total > 0
      ? Math.round((tri.totals.mastered / tri.totals.total) * 100)
      : 0;
  return (
    <section
      className={`rounded-2xl border ${tri.isCurrent ? 'border-amber-300 bg-amber-50/40' : 'border-gray-200 bg-white'} p-4 md:p-6`}
      aria-labelledby={`tri-${tri.trimester}`}
    >
      <header className="flex items-center justify-between mb-4 gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <h3
            id={`tri-${tri.trimester}`}
            className="text-lg md:text-xl font-extrabold text-gray-900 font-display"
          >
            Trimestre {tri.trimester}
          </h3>
          {tri.isCurrent && (
            <span className="text-xs font-bold uppercase tracking-wide bg-amber-100 text-amber-700 px-2.5 py-1 rounded-full flex items-center gap-1.5">
              <CalendarDays size={12} /> en cours
            </span>
          )}
        </div>
        <div className="text-sm text-gray-600 flex items-center gap-3 flex-wrap">
          <span><strong className="text-emerald-600">{tri.totals.mastered}</strong> maîtrisés</span>
          <span><strong className="text-amber-600">{tri.totals.inProgress}</strong> en cours</span>
          <span><strong className="text-gray-500">{tri.totals.total}</strong> au total</span>
          <span className="font-bold">{masteryPct}%</span>
        </div>
      </header>

      {tri.weeks.length === 0 ? (
        <p className="text-sm text-gray-500 italic">Aucun skill séquencé sur ce trimestre.</p>
      ) : (
        <div className="space-y-5">
          {tri.weeks.map(week => (
            <div key={week.weekOrder}>
              <h4 className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">
                Semaine {week.weekOrder}
              </h4>
              <div className="grid gap-2 md:grid-cols-2">
                {week.skills.map(item => (
                  <SkillRow key={item.skill.id} item={item} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export const ProgramTimeline: React.FC<Props> = ({ subjects, skillsBySubject, progress }) => {
  const calendar = useMemo(() => getCurrentTrimesterWeek(), []);
  const trimesters = useMemo(
    () => groupByTrimesterWeek(subjects, skillsBySubject, progress, calendar),
    [subjects, skillsBySubject, progress, calendar],
  );

  const allEmpty = trimesters.every(t => t.totals.total === 0);
  if (allEmpty) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-6 text-center">
        <p className="text-sm text-gray-600">
          Le programme n'est pas encore disponible pour ton niveau.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {calendar && (
        <p className="text-sm text-gray-600">
          Tu es actuellement en{' '}
          <strong>{formatTrimesterWeek(calendar)}</strong>. Les leçons à venir
          se débloqueront automatiquement.
        </p>
      )}
      {trimesters.map(tri => (
        <TrimesterBlock key={tri.trimester} tri={tri} />
      ))}
    </div>
  );
};
