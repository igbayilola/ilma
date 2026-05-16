/**
 * Vue « Mon programme » — agrégation pure (testable sans DOM).
 *
 * Regroupe les skills par trimestre puis par semaine, avec un statut par
 * skill calculé à partir de la progression et du calendrier courant.
 *
 * Utilisé par {@link ProgramTimeline} pour rendre la timeline T1/T2/T3 à
 * l'élève après iter 19-21 (backfill + cleanup ordre + picker rattrapage).
 */
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';
import type { TrimesterWeek } from '../../utils/schoolCalendar';

export type SkillStatus = 'mastered' | 'inProgress' | 'upcoming' | 'future';

export interface TimelineSkill {
  subject: SubjectDTO;
  skill: SkillDTO;
  status: SkillStatus;
  /** Score actuel (0-100) — utile pour afficher une mini-barre. */
  score: number;
  /** Tentatives cumulées sur le skill. */
  totalAttempts: number;
}

export interface TimelineWeek {
  weekOrder: number;
  skills: TimelineSkill[];
}

export interface TimelineTrimester {
  trimester: 1 | 2 | 3;
  /** True quand `calendar.trimester === this.trimester`. */
  isCurrent: boolean;
  weeks: TimelineWeek[];
  /** Compteur agrégé pour l'en-tête du trimestre. */
  totals: {
    total: number;
    mastered: number;
    inProgress: number;
    upcoming: number;
    future: number;
  };
}

const MASTERY_THRESHOLD = 80;

function classify(
  trimester: number,
  weekOrder: number,
  score: number,
  totalAttempts: number,
  calendar: TrimesterWeek | null,
): SkillStatus {
  if (score >= MASTERY_THRESHOLD) return 'mastered';
  if (totalAttempts > 0) return 'inProgress';
  // Pas encore tenté : passé/présent → upcoming (à faire), futur → future.
  if (!calendar) return 'upcoming';
  if (
    trimester > calendar.trimester ||
    (trimester === calendar.trimester && weekOrder > calendar.week)
  ) {
    return 'future';
  }
  return 'upcoming';
}

export function groupByTrimesterWeek(
  subjects: SubjectDTO[],
  skillsBySubject: Map<string, SkillDTO[]>,
  progress: SkillProgressDTO[],
  calendar: TrimesterWeek | null,
): TimelineTrimester[] {
  const progressById = new Map(progress.map(p => [p.skillId, p]));
  const subjectById = new Map(subjects.map(s => [s.id, s]));

  // Initialise les 3 trimestres vides.
  const byTri = new Map<1 | 2 | 3, Map<number, TimelineSkill[]>>([
    [1, new Map()],
    [2, new Map()],
    [3, new Map()],
  ]);

  for (const subject of subjects) {
    const skills = skillsBySubject.get(subject.id) || [];
    for (const skill of skills) {
      const t = skill.trimester ?? null;
      const w = skill.weekOrder ?? null;
      if (t == null || w == null) continue;
      if (t !== 1 && t !== 2 && t !== 3) continue;

      const p = progressById.get(skill.id);
      const score = p?.score ?? 0;
      const totalAttempts = p?.totalAttempts ?? 0;

      const status = classify(t, w, score, totalAttempts, calendar);
      const triBucket = byTri.get(t)!;
      const weekBucket = triBucket.get(w) || [];
      weekBucket.push({
        subject: subjectById.get(subject.id) || subject,
        skill,
        status,
        score,
        totalAttempts,
      });
      triBucket.set(w, weekBucket);
    }
  }

  const result: TimelineTrimester[] = [];
  for (const tri of [1, 2, 3] as const) {
    const triBucket = byTri.get(tri)!;
    const weeks: TimelineWeek[] = [];
    const totals = { total: 0, mastered: 0, inProgress: 0, upcoming: 0, future: 0 };

    const orderedWeeks = [...triBucket.keys()].sort((a, b) => a - b);
    for (const weekOrder of orderedWeeks) {
      const items = triBucket.get(weekOrder)!.slice();
      // Tri stable par subject.order puis skill.order pour un rendu cohérent.
      items.sort((a, b) => {
        const so = (a.subject.order ?? 0) - (b.subject.order ?? 0);
        if (so !== 0) return so;
        return (a.skill.order ?? 0) - (b.skill.order ?? 0);
      });
      weeks.push({ weekOrder, skills: items });
      for (const item of items) {
        totals.total += 1;
        totals[item.status] += 1;
      }
    }

    result.push({
      trimester: tri,
      isCurrent: calendar?.trimester === tri,
      weeks,
      totals,
    });
  }
  return result;
}
