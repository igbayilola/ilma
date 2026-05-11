/**
 * Calendrier scolaire Bénin (CM2) — programme officiel MEMP.
 *
 * MVP : Bénin uniquement. Quand on étendra à d'autres pays francophones
 * d'Afrique, on passera ces dates en data (table `school_calendars` côté BE
 * keyed par country_code) plutôt que hardcodées ici.
 *
 * Dates approximatives (la rentrée et les vacances varient légèrement chaque
 * année). On se contente de ranger l'année en 3 trimestres + 3 intervalles
 * "vacances" pendant lesquels le picker bascule sur l'heuristique de fallback.
 */

interface MonthDay {
  /** 1-12 */
  month: number;
  /** 1-31 */
  day: number;
}

interface TrimesterBoundaries {
  number: 1 | 2 | 3;
  start: MonthDay;
  end: MonthDay;
}

const BENIN_CM2_TRIMESTERS: TrimesterBoundaries[] = [
  { number: 1, start: { month: 9, day: 16 }, end: { month: 12, day: 20 } },  // ~14 semaines
  { number: 2, start: { month: 1, day: 6 },  end: { month: 4, day: 5 } },    // ~13 semaines
  { number: 3, start: { month: 4, day: 22 }, end: { month: 6, day: 30 } },   // ~10 semaines (CEP fin juin)
];

const MS_PER_WEEK = 7 * 24 * 60 * 60 * 1000;

export interface TrimesterWeek {
  trimester: 1 | 2 | 3;
  /** 1-indexé depuis le début du trimestre. */
  week: number;
  /** Nombre total de semaines du trimestre. */
  totalWeeks: number;
}

/**
 * Retourne le trimestre + semaine courants si on est en période scolaire,
 * sinon `null` (vacances, weekend, peu importe — c'est juste pour aider le
 * dashboard à pondérer le contenu).
 */
export function getCurrentTrimesterWeek(now: Date = new Date()): TrimesterWeek | null {
  const year = now.getFullYear();
  const t = now.getTime();

  for (const tri of BENIN_CM2_TRIMESTERS) {
    const start = new Date(year, tri.start.month - 1, tri.start.day).getTime();
    const end = new Date(year, tri.end.month - 1, tri.end.day, 23, 59, 59).getTime();
    if (t >= start && t <= end) {
      const week = Math.floor((t - start) / MS_PER_WEEK) + 1;
      const totalWeeks = Math.floor((end - start) / MS_PER_WEEK) + 1;
      return { trimester: tri.number, week, totalWeeks };
    }
  }
  return null;
}

/**
 * Label FR humain : "Trimestre 2 · Semaine 5".
 */
export function formatTrimesterWeek(tw: TrimesterWeek): string {
  return `Trimestre ${tw.trimester} · Semaine ${tw.week}`;
}
