import { describe, it, expect } from 'vitest';
import { groupByTrimesterWeek } from '../../components/dashboard/programTimeline';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';
import type { TrimesterWeek } from '../../utils/schoolCalendar';

const subjectMath: SubjectDTO = {
  id: 'sub-math',
  name: 'Maths',
  slug: 'math',
  iconName: 'Calculator',
  color: '',
  textColor: '',
  gradient: '',
  emoji: '🔢',
  order: 1,
};

const subjectFr: SubjectDTO = {
  id: 'sub-fr',
  name: 'Français',
  slug: 'fr',
  iconName: 'Book',
  color: '',
  textColor: '',
  gradient: '',
  emoji: '📚',
  order: 2,
};

function skill(
  id: string,
  domainId: string,
  name: string,
  order: number,
  trimester: number | null,
  weekOrder: number | null,
): SkillDTO {
  return {
    id,
    name,
    slug: id,
    domainId,
    domainName: 'Domaine',
    order,
    trimester,
    weekOrder,
  };
}

function progress(skillId: string, score: number, attempts: number): SkillProgressDTO {
  return { skillId, skillName: skillId, score, totalAttempts: attempts };
}

const T2_W5: TrimesterWeek = { trimester: 2, week: 5, totalWeeks: 13 };

describe('groupByTrimesterWeek', () => {
  it('renvoie 3 trimestres même si certains sont vides', () => {
    const result = groupByTrimesterWeek([], new Map(), [], T2_W5);
    expect(result.map(t => t.trimester)).toEqual([1, 2, 3]);
    expect(result.every(t => t.weeks.length === 0)).toBe(true);
  });

  it('marque uniquement le trimestre courant comme isCurrent', () => {
    const result = groupByTrimesterWeek([], new Map(), [], T2_W5);
    expect(result[0].isCurrent).toBe(false);
    expect(result[1].isCurrent).toBe(true);
    expect(result[2].isCurrent).toBe(false);
  });

  it('classifie selon score (≥80 maîtrisé) et attempts (>0 en cours)', () => {
    const skills = [
      skill('sk-master', 'd1', 'M', 1, 1, 1),
      skill('sk-inprog', 'd1', 'I', 2, 1, 2),
      skill('sk-todo', 'd1', 'T', 3, 1, 3),
      skill('sk-future', 'd1', 'F', 4, 3, 1), // T3 — futur depuis T2.W5
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [
      progress('sk-master', 95, 10),
      progress('sk-inprog', 40, 5),
      // sk-todo et sk-future : aucune tentative
    ];
    const result = groupByTrimesterWeek([subjectMath], map, prog, T2_W5);
    // T1 : mastered + inProgress + todo (W1, W2, W3)
    const t1 = result[0];
    expect(t1.weeks.map(w => w.weekOrder)).toEqual([1, 2, 3]);
    expect(t1.weeks[0].skills[0].status).toBe('mastered');
    expect(t1.weeks[1].skills[0].status).toBe('inProgress');
    expect(t1.weeks[2].skills[0].status).toBe('upcoming');
    // T3 sans progression → future
    const t3 = result[2];
    expect(t3.weeks[0].skills[0].status).toBe('future');
  });

  it("skip les skills sans (trimester, weekOrder)", () => {
    const skills = [
      skill('sk-1', 'd1', 'X', 1, null, null),
      skill('sk-2', 'd1', 'Y', 2, 1, 1),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const result = groupByTrimesterWeek([subjectMath], map, [], T2_W5);
    expect(result[0].totals.total).toBe(1);
    expect(result[0].weeks[0].skills[0].skill.id).toBe('sk-2');
  });

  it('agrège correctement les totaux par trimestre', () => {
    const skills = [
      skill('sk-1', 'd1', 'A', 1, 1, 1),
      skill('sk-2', 'd1', 'B', 2, 1, 2),
      skill('sk-3', 'd1', 'C', 3, 2, 5),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const prog = [progress('sk-1', 90, 10), progress('sk-2', 30, 3)];
    const result = groupByTrimesterWeek([subjectMath], map, prog, T2_W5);
    expect(result[0].totals).toEqual({
      total: 2,
      mastered: 1,
      inProgress: 1,
      upcoming: 0,
      future: 0,
    });
    expect(result[1].totals.total).toBe(1);
  });

  it('regroupe plusieurs matières sous la même semaine et trie par subject.order', () => {
    const mathSkills = [skill('sk-m', 'dm', 'M-T1W1', 1, 1, 1)];
    const frSkills = [skill('sk-f', 'df', 'F-T1W1', 1, 1, 1)];
    const map = new Map([
      [subjectMath.id, mathSkills],
      [subjectFr.id, frSkills],
    ]);
    const result = groupByTrimesterWeek([subjectFr, subjectMath], map, [], T2_W5);
    const week1 = result[0].weeks[0];
    expect(week1.skills.map(s => s.skill.id)).toEqual(['sk-m', 'sk-f']);
  });

  it('calendar=null : tous les skills sans tentative deviennent upcoming', () => {
    const skills = [
      skill('sk-t1', 'd1', 'T1W1', 1, 1, 1),
      skill('sk-t3', 'd1', 'T3W1', 2, 3, 1),
    ];
    const map = new Map([[subjectMath.id, skills]]);
    const result = groupByTrimesterWeek([subjectMath], map, [], null);
    expect(result[0].weeks[0].skills[0].status).toBe('upcoming');
    expect(result[2].weeks[0].skills[0].status).toBe('upcoming'); // pas de futur sans calendrier
    expect(result[1].isCurrent).toBe(false); // pas de trimestre courant
  });
});
