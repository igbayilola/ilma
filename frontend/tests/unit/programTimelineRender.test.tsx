/**
 * Tests rendu ProgramTimeline (iter 30).
 *
 * La fonction pure `groupByTrimesterWeek` est déjà couverte par
 * `programTimeline.test.ts` (7 cas). On isole ici les branches React
 * du composant en mockant l'agrégation et le calendrier — on alimente
 * directement `TimelineTrimester[]`.
 */
import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type {
  TimelineTrimester,
  TimelineSkill,
} from '../../components/dashboard/programTimeline';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';

// ── Mocks --------------------------------------------------------------------
const { groupMock, getCurrentMock, navigateMock } = vi.hoisted(() => ({
  groupMock: vi.fn(),
  getCurrentMock: vi.fn(),
  navigateMock: vi.fn(),
}));

vi.mock('../../components/dashboard/programTimeline', async () => {
  const actual: any = await vi.importActual(
    '../../components/dashboard/programTimeline',
  );
  return { ...actual, groupByTrimesterWeek: groupMock };
});

vi.mock('../../utils/schoolCalendar', async () => {
  const actual: any = await vi.importActual('../../utils/schoolCalendar');
  return { ...actual, getCurrentTrimesterWeek: getCurrentMock };
});

vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

import { ProgramTimeline } from '../../components/dashboard/ProgramTimeline';

// ── Fixtures -----------------------------------------------------------------
const SUBJECT: SubjectDTO = {
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

function makeSkill(id: string, name: string, order = 1): SkillDTO {
  return {
    id,
    name,
    slug: id,
    domainId: 'd1',
    domainName: 'Numération',
    order,
    trimester: 1,
    weekOrder: 1,
  };
}

function makeTimelineSkill(
  overrides: Partial<TimelineSkill> & { skill?: SkillDTO } = {},
): TimelineSkill {
  return {
    subject: SUBJECT,
    skill: overrides.skill ?? makeSkill('sk-1', 'Numération 1'),
    status: 'upcoming',
    score: 0,
    totalAttempts: 0,
    ...overrides,
  };
}

function makeTrimester(
  trimester: 1 | 2 | 3,
  opts: { isCurrent?: boolean; skills?: TimelineSkill[]; weekOrder?: number } = {},
): TimelineTrimester {
  const skills = opts.skills ?? [];
  const week = opts.weekOrder ?? 1;
  const totals = {
    total: skills.length,
    mastered: skills.filter(s => s.status === 'mastered').length,
    inProgress: skills.filter(s => s.status === 'inProgress').length,
    upcoming: skills.filter(s => s.status === 'upcoming').length,
    future: skills.filter(s => s.status === 'future').length,
  };
  return {
    trimester,
    isCurrent: opts.isCurrent ?? false,
    weeks: skills.length > 0 ? [{ weekOrder: week, skills }] : [],
    totals,
  };
}

function renderTimeline() {
  return render(
    <MemoryRouter>
      <ProgramTimeline
        subjects={[SUBJECT]}
        skillsBySubject={new Map([[SUBJECT.id, [makeSkill('sk-1', 'X')]]])}
        progress={[]}
      />
    </MemoryRouter>,
  );
}

// ── Tests --------------------------------------------------------------------
describe('<ProgramTimeline>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getCurrentMock.mockReturnValue({ trimester: 1, week: 4, totalWeeks: 14 });
  });

  it('rend le fallback quand tous les trimestres sont vides', () => {
    groupMock.mockReturnValue([
      makeTrimester(1),
      makeTrimester(2),
      makeTrimester(3),
    ]);

    renderTimeline();

    expect(
      screen.getByText(/programme n'est pas encore disponible/i),
    ).toBeInTheDocument();
    // Ni la ligne calendrier, ni les sections trimestres.
    expect(screen.queryByText(/Tu es actuellement en/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Trimestre 1/)).not.toBeInTheDocument();
  });

  it('affiche la ligne « Tu es actuellement en … » quand calendrier présent', () => {
    groupMock.mockReturnValue([
      makeTrimester(1, { isCurrent: true, skills: [makeTimelineSkill()] }),
      makeTrimester(2),
      makeTrimester(3),
    ]);

    renderTimeline();

    expect(screen.getByText(/Tu es actuellement en/)).toBeInTheDocument();
    expect(
      screen.getByText(/Les leçons à venir se débloqueront automatiquement/),
    ).toBeInTheDocument();
  });

  it('masque la ligne calendrier quand getCurrentTrimesterWeek=null', () => {
    getCurrentMock.mockReturnValue(null);
    groupMock.mockReturnValue([
      makeTrimester(1, { skills: [makeTimelineSkill()] }),
      makeTrimester(2),
      makeTrimester(3),
    ]);

    renderTimeline();

    expect(screen.queryByText(/Tu es actuellement en/)).not.toBeInTheDocument();
    // Mais les trimestres sont bien rendus.
    expect(screen.getByText(/Trimestre 1/)).toBeInTheDocument();
  });

  it('marque le trimestre courant avec le badge « en cours »', () => {
    groupMock.mockReturnValue([
      makeTrimester(1, { isCurrent: true, skills: [makeTimelineSkill()] }),
      makeTrimester(2, { skills: [makeTimelineSkill({ skill: makeSkill('sk-2', 'Op 1') })] }),
      makeTrimester(3, { skills: [makeTimelineSkill({ skill: makeSkill('sk-3', 'Mes 1') })] }),
    ]);

    renderTimeline();

    // Le badge est à côté du titre (pas dans les stats où « X en cours »
    // apparaît aussi). On scope au parent du heading.
    const t1Heading = within(
      screen.getByRole('region', { name: /Trimestre 1/ }),
    ).getByRole('heading', { name: /Trimestre 1/ });
    expect(t1Heading.parentElement).toHaveTextContent(/en cours/);

    const t2Heading = within(
      screen.getByRole('region', { name: /Trimestre 2/ }),
    ).getByRole('heading', { name: /Trimestre 2/ });
    expect(t2Heading.parentElement).not.toHaveTextContent(/en cours/);
  });

  it('affiche un message dédié dans un trimestre vide (weeks=[])', () => {
    groupMock.mockReturnValue([
      makeTrimester(1, { skills: [makeTimelineSkill()] }),
      makeTrimester(2), // weeks=[], totals.total=0 mais autre trimestre non-vide
      makeTrimester(3, { skills: [makeTimelineSkill({ skill: makeSkill('sk-3', 'Mes 1') })] }),
    ]);

    renderTimeline();

    const t2 = screen.getByRole('region', { name: /Trimestre 2/ });
    expect(t2).toHaveTextContent('Aucun skill séquencé sur ce trimestre');
  });

  it('clic sur un skill non-futur navigue vers son détail', () => {
    const skill = makeSkill('sk-77', 'Fractions');
    groupMock.mockReturnValue([
      makeTrimester(1, {
        isCurrent: true,
        skills: [makeTimelineSkill({ skill, status: 'upcoming' })],
      }),
      makeTrimester(2),
      makeTrimester(3),
    ]);

    renderTimeline();

    fireEvent.click(screen.getByRole('button', { name: /Fractions/ }));
    expect(navigateMock).toHaveBeenCalledWith(
      `/app/student/subjects/${SUBJECT.id}/domains/d1/skills/sk-77`,
    );
  });

  it('un skill de statut « future » est désactivé et ne navigue pas', () => {
    const skill = makeSkill('sk-99', 'Géométrie T3');
    groupMock.mockReturnValue([
      makeTrimester(1, { isCurrent: true, skills: [makeTimelineSkill()] }),
      makeTrimester(2),
      makeTrimester(3, {
        skills: [makeTimelineSkill({ skill, status: 'future' })],
      }),
    ]);

    renderTimeline();

    const btn = screen.getByRole('button', { name: /Géométrie T3/ });
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute('aria-disabled', 'true');

    fireEvent.click(btn);
    expect(navigateMock).not.toHaveBeenCalled();
  });

  it('un skill « inProgress » affiche son score', () => {
    const skill = makeSkill('sk-42', 'Numération avancée');
    groupMock.mockReturnValue([
      makeTrimester(1, {
        isCurrent: true,
        skills: [
          makeTimelineSkill({ skill, status: 'inProgress', score: 65, totalAttempts: 3 }),
        ],
      }),
      makeTrimester(2),
      makeTrimester(3),
    ]);

    renderTimeline();

    // Le pourcentage apparaît à l'intérieur du bouton du skill.
    const btn = screen.getByRole('button', { name: /Numération avancée/ });
    expect(btn).toHaveTextContent('65%');
  });
});
