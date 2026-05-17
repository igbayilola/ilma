/**
 * Tests rendu CurrentLessonHero (iter 31).
 *
 * La fonction pure `pickCurrentLesson` est déjà couverte par 10 cas
 * dans `currentLessonHero.test.ts` (depuis iter 7). On isole ici les
 * branches React du composant en construisant des inputs qui forcent
 * chaque variante de hint via la vraie `pickCurrentLesson`, et en
 * mockant `getCurrentTrimesterWeek` + `useNavigate`.
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';

// ── Mocks --------------------------------------------------------------------
const { getCurrentMock, navigateMock } = vi.hoisted(() => ({
  getCurrentMock: vi.fn(),
  navigateMock: vi.fn(),
}));

vi.mock('../../utils/schoolCalendar', async () => {
  const actual: any = await vi.importActual('../../utils/schoolCalendar');
  return { ...actual, getCurrentTrimesterWeek: getCurrentMock };
});

vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

import { CurrentLessonHero } from '../../components/dashboard/CurrentLessonHero';

// ── Fixtures -----------------------------------------------------------------
const SUBJECT_MATH: SubjectDTO = {
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

function makeSkill(
  id: string,
  name: string,
  opts: Partial<SkillDTO> = {},
): SkillDTO {
  return {
    id,
    name,
    slug: id,
    domainId: 'd-num',
    domainName: 'Numération',
    order: 1,
    trimester: 1,
    weekOrder: 1,
    ...opts,
  };
}

function makeProgress(
  skillId: string,
  score: number,
  totalAttempts = 1,
): SkillProgressDTO {
  return {
    skillId,
    skillName: skillId,
    score,
    totalAttempts,
    correctAttempts: Math.round((score / 100) * totalAttempts),
    lastPlayedAt: new Date().toISOString(),
  } as unknown as SkillProgressDTO;
}

function renderHero(
  subjects: SubjectDTO[],
  skillsBySubject: Map<string, SkillDTO[]>,
  progress: SkillProgressDTO[] = [],
) {
  return render(
    <MemoryRouter>
      <CurrentLessonHero
        subjects={subjects}
        skillsBySubject={skillsBySubject}
        progress={progress}
      />
    </MemoryRouter>,
  );
}

// ── Tests --------------------------------------------------------------------
describe('<CurrentLessonHero>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Calendrier courant : T2 semaine 5 (par défaut pour la plupart des cas).
    getCurrentMock.mockReturnValue({ trimester: 2, week: 5, totalWeeks: 12 });
  });

  it('rend null quand aucun subject n\'est fourni', () => {
    const { container } = renderHero([], new Map());
    expect(container).toBeEmptyDOMElement();
  });

  it('rend l\'état de célébration quand tout est maîtrisé', () => {
    const skills = [
      makeSkill('sk-1', 'Numération 1', { order: 1 }),
      makeSkill('sk-2', 'Numération 2', { order: 2 }),
    ];
    const progress = [makeProgress('sk-1', 95), makeProgress('sk-2', 90)];

    renderHero(
      [SUBJECT_MATH],
      new Map([[SUBJECT_MATH.id, skills]]),
      progress,
    );

    expect(
      screen.getByText(/Bravo — tu maîtrises tout le programme CM2/i),
    ).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole('button', { name: /Explorer mes matières/ }),
    );
    expect(navigateMock).toHaveBeenCalledWith('/app/student/subjects');
  });

  it('affiche « À rattraper » quand le skill choisi précède la semaine courante', () => {
    // calendar = T2.W5 ; skill non-maîtrisé à T1.W3 → catch-up
    const skill = makeSkill('sk-1', 'Fractions', { trimester: 1, weekOrder: 3 });
    renderHero([SUBJECT_MATH], new Map([[SUBJECT_MATH.id, [skill]]]));

    expect(screen.getByText(/À rattraper/)).toBeInTheDocument();
    expect(screen.queryByText(/Cette semaine en CM2/)).not.toBeInTheDocument();
    expect(screen.getByText('Fractions')).toBeInTheDocument();
  });

  it('affiche « Cette semaine en CM2 » + badge calendrier quand le skill est sur la semaine courante', () => {
    // calendar = T2.W5 ; skill à T2.W5 → pas de catch-up
    const skill = makeSkill('sk-1', 'Géométrie', {
      trimester: 2,
      weekOrder: 5,
    });
    renderHero([SUBJECT_MATH], new Map([[SUBJECT_MATH.id, [skill]]]));

    expect(screen.getByText(/Cette semaine en CM2/)).toBeInTheDocument();
    // Badge calendrier `matchedCalendar=true` → formatTrimesterWeek rendu.
    expect(screen.getByText(/Trimestre 2/)).toBeInTheDocument();
    expect(screen.getByText(/Semaine 5/)).toBeInTheDocument();
  });

  it('omet le badge calendrier quand le pick est en stratégie fallback (calendar=null)', () => {
    getCurrentMock.mockReturnValue(null);
    const skill = makeSkill('sk-1', 'Logique', {
      trimester: null,
      weekOrder: null,
    });
    renderHero([SUBJECT_MATH], new Map([[SUBJECT_MATH.id, [skill]]]));

    // Le composant rend mais sans le badge formatTrimesterWeek.
    expect(screen.getByText('Logique')).toBeInTheDocument();
    expect(screen.queryByText(/Trimestre/)).not.toBeInTheDocument();
  });

  it('« Continuer la leçon » navigue vers le détail du skill', () => {
    const skill = makeSkill('sk-77', 'Mesures', {
      trimester: 2,
      weekOrder: 5,
      domainId: 'd-mes',
    });
    renderHero([SUBJECT_MATH], new Map([[SUBJECT_MATH.id, [skill]]]));

    fireEvent.click(screen.getByRole('button', { name: /Continuer la leçon/ }));
    expect(navigateMock).toHaveBeenCalledWith(
      `/app/student/subjects/${SUBJECT_MATH.id}/domains/d-mes/skills/sk-77`,
    );
  });

  it('« Voir tout mon programme » navigue vers /app/student/programme', () => {
    const skill = makeSkill('sk-1', 'Aire', { trimester: 2, weekOrder: 5 });
    renderHero([SUBJECT_MATH], new Map([[SUBJECT_MATH.id, [skill]]]));

    fireEvent.click(
      screen.getByRole('button', { name: /Voir tout mon programme/ }),
    );
    expect(navigateMock).toHaveBeenCalledWith('/app/student/programme');
  });

  it('rend la barre de progression et la mention « X leçons en cours »', () => {
    // 3 skills : 1 maîtrisé, 1 touché non-maîtrisé, 1 vierge.
    // mastered=1, touched=2, total=3 → 33%, "1 leçon en cours".
    const skills = [
      makeSkill('sk-1', 'Numération 1', { order: 1, trimester: 1, weekOrder: 1 }),
      makeSkill('sk-2', 'Numération 2', { order: 2, trimester: 1, weekOrder: 2 }),
      makeSkill('sk-3', 'Numération 3', { order: 3, trimester: 1, weekOrder: 3 }),
    ];
    const progress = [
      makeProgress('sk-1', 95, 5), // maîtrisé
      makeProgress('sk-2', 40, 3), // touché, non-maîtrisé → la cible
    ];
    renderHero(
      [SUBJECT_MATH],
      new Map([[SUBJECT_MATH.id, skills]]),
      progress,
    );

    const bar = screen.getByRole('progressbar', { name: /Progression en Maths/ });
    expect(bar).toHaveAttribute('aria-valuenow', '33');
    expect(screen.getByText(/1 leçon en cours/)).toBeInTheDocument();
    expect(screen.getByText(/1\/3 leçons maîtrisées/)).toBeInTheDocument();
  });
});
