import { describe, it, expect } from 'vitest';
import { pickCurrentLesson } from '../../components/dashboard/CurrentLessonHero';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';
import type { TrimesterWeek } from '../../utils/schoolCalendar';

const subjectMath: SubjectDTO = {
  id: 'sub-math',
  name: 'Maths',
  slug: 'math',
  iconName: 'Calculator',
  color: 'bg-blue-100',
  textColor: 'text-blue-600',
  gradient: '',
  emoji: '🔢',
  order: 1,
};

const subjectFr: SubjectDTO = {
  id: 'sub-fr',
  name: 'Français',
  slug: 'fr',
  iconName: 'Book',
  color: 'bg-purple-100',
  textColor: 'text-purple-600',
  gradient: '',
  emoji: '📚',
  order: 2,
};

function skill(
  id: string,
  domainId: string,
  name: string,
  order: number,
  trimester: number | null = null,
  weekOrder: number | null = null,
): SkillDTO {
  return {
    id,
    name,
    slug: id,
    domainId,
    domainName: 'Numération',
    order,
    trimester,
    weekOrder,
  };
}

function progress(skillId: string, score: number, attempts = 5): SkillProgressDTO {
  return { skillId, skillName: skillId, score, totalAttempts: attempts };
}

const T2_W5: TrimesterWeek = { trimester: 2, week: 5, totalWeeks: 13 };

describe('pickCurrentLesson', () => {
  it('returns null when no subjects', () => {
    expect(pickCurrentLesson([], new Map(), [], null)).toBeNull();
  });

  it('falls back to first non-mastered when no calendar', () => {
    const skills = [
      skill('sk-1', 'dom-1', 'Lecon 1', 1),
      skill('sk-2', 'dom-1', 'Lecon 2', 2),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [progress('sk-1', 95)]; // sk-1 mastered, sk-2 not

    const hint = pickCurrentLesson([subjectMath], map, prog, null);
    expect(hint?.skill.id).toBe('sk-2');
    expect(hint?.matchedCalendar).toBe(false);
    expect(hint?.subjectMasteredSkills).toBe(1);
    expect(hint?.subjectTotalSkills).toBe(2);
  });

  it('prefers earliest non-mastered (T,W) ≤ today (rattrapage)', () => {
    const skills = [
      skill('sk-1', 'dom-1', 'Lecon 1', 1),                // no trimester data → ignored par strat 1
      skill('sk-2', 'dom-1', 'Lecon T2W3', 2, 2, 3),       // candidat
      skill('sk-3', 'dom-1', 'Lecon T2W5', 3, 2, 5),       // candidat
    ];
    const map = new Map([[subjectMath.id, skills]]);

    const hint = pickCurrentLesson([subjectMath], map, [], T2_W5);
    expect(hint?.skill.id).toBe('sk-2'); // T2W3 — le plus ancien non-maîtrisé
    expect(hint?.matchedCalendar).toBe(true);
    expect(hint?.isCatchUp).toBe(true); // T2W3 < T2W5 → rattrapage
  });

  it('calendar pick excludes mastered skills', () => {
    const skills = [
      skill('sk-1', 'dom-1', 'T2W3', 1, 2, 3),
      skill('sk-2', 'dom-1', 'T2W5', 2, 2, 5),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [progress('sk-2', 90)]; // sk-2 (latest) mastered

    const hint = pickCurrentLesson([subjectMath], map, prog, T2_W5);
    expect(hint?.skill.id).toBe('sk-1'); // sk-1 is the next non-mastered
    expect(hint?.matchedCalendar).toBe(true);
  });

  it('calendar pick does not surface future weeks', () => {
    const skills = [
      skill('sk-1', 'dom-1', 'T2W3', 1, 2, 3),
      skill('sk-2', 'dom-1', 'T2W8', 2, 2, 8), // beyond current week 5
    ];
    const map = new Map([[subjectMath.id, skills]]);

    const hint = pickCurrentLesson([subjectMath], map, [], T2_W5);
    expect(hint?.skill.id).toBe('sk-1'); // sk-2 is future, skipped
  });

  it('falls back to subject order when no skill matches current trimester', () => {
    const mathSkills = [skill('sk-m1', 'dom-1', 'M1', 1, 3, 2)]; // T3 — not current
    const frSkills = [skill('sk-f1', 'dom-2', 'F1', 1)];          // no trimester data
    const map = new Map([
      [subjectMath.id, mathSkills],
      [subjectFr.id, frSkills],
    ]);

    const hint = pickCurrentLesson([subjectMath, subjectFr], map, [], T2_W5);
    // Math T3 skill doesn't match T2, fr has no trimester → falls back, Math first
    expect(hint?.skill.id).toBe('sk-m1');
    expect(hint?.matchedCalendar).toBe(false);
  });

  it('returns allMastered hint when every skill is mastered', () => {
    const skills = [skill('sk-1', 'dom-1', 'Lecon', 1)];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [progress('sk-1', 95)];

    const hint = pickCurrentLesson([subjectMath], map, prog, null);
    expect(hint?.allMastered).toBe(true);
    expect(hint?.subjectMasteredSkills).toBe(1);
  });

  it('prioritise un skill T1 non-maîtrisé sur un T2 non-maîtrisé', () => {
    // Étudiant en T2.W5 avec backlog T1 → on lui sert d'abord le T1.
    const mathSkills = [skill('sk-m', 'dom-m', 'Math T1', 1, 1, 2)]; // T1.W2
    const frSkills = [skill('sk-f', 'dom-f', 'Fr T2W4', 1, 2, 4)];   // T2.W4
    const map = new Map([
      [subjectMath.id, mathSkills],
      [subjectFr.id, frSkills],
    ]);

    const hint = pickCurrentLesson([subjectMath, subjectFr], map, [], T2_W5);
    expect(hint?.skill.id).toBe('sk-m');
    expect(hint?.matchedCalendar).toBe(true);
    expect(hint?.isCatchUp).toBe(true);
  });

  it("nouvel élève en T2.W5 sans progression reçoit T1.W1 d'abord", () => {
    const mathSkills = [
      skill('sk-m1', 'dom-m', 'Math T1W1', 1, 1, 1),
      skill('sk-m5', 'dom-m', 'Math T2W5', 2, 2, 5),
    ];
    const frSkills = [
      skill('sk-f1', 'dom-f', 'Fr T1W1', 1, 1, 1),
      skill('sk-f5', 'dom-f', 'Fr T2W5', 2, 2, 5),
    ];
    const map = new Map([
      [subjectMath.id, mathSkills],
      [subjectFr.id, frSkills],
    ]);

    const hint = pickCurrentLesson([subjectMath, subjectFr], map, [], T2_W5);
    // T1.W1 + subject.order=1 (math) → sk-m1
    expect(hint?.skill.id).toBe('sk-m1');
    expect(hint?.isCatchUp).toBe(true);
  });

  it("élève à jour reçoit le skill de la semaine courante (isCatchUp=false)", () => {
    const skills = [
      skill('sk-1', 'dom-1', 'T1W1', 1, 1, 1),
      skill('sk-2', 'dom-1', 'T2W5', 2, 2, 5),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [progress('sk-1', 90)]; // T1.W1 maîtrisé

    const hint = pickCurrentLesson([subjectMath], map, prog, T2_W5);
    expect(hint?.skill.id).toBe('sk-2');
    expect(hint?.matchedCalendar).toBe(true);
    expect(hint?.isCatchUp).toBe(false); // T2.W5 == calendar → pas du rattrapage
  });
});
