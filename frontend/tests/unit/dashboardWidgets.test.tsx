/**
 * Tests rendu des 4 mini-widgets in-Dashboard (iter 36, P4 punch-list iter 32).
 *
 * `StreakReminderCard`, `RuleDuJourWidget`, `DailyChallengeWidget` et
 * `CalculMentalWidget` sont définis dans `pages/Dashboard.tsx`. Tous
 * exportés à présent pour permettre leur test isolé.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';

const { listFormulasMock } = vi.hoisted(() => ({
  listFormulasMock: vi.fn(),
}));

vi.mock('../../services/contentService', async () => {
  const actual: any = await vi.importActual('../../services/contentService');
  return {
    ...actual,
    contentService: { listFormulas: listFormulasMock },
  };
});

const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

import {
  StreakReminderCard,
  RuleDuJourWidget,
  DailyChallengeWidget,
  CalculMentalWidget,
} from '../../pages/Dashboard';

function wrap(children: React.ReactNode) {
  return render(<MemoryRouter>{children}</MemoryRouter>);
}

// ── StreakReminderCard ──────────────────────────────────────────────────────
describe('<StreakReminderCard>', () => {
  beforeEach(() => vi.clearAllMocks());

  it('rend la branche « Bravo » quand série active ET joué aujourd\'hui', () => {
    wrap(
      <StreakReminderCard
        streak={5}
        hasPlayedToday={true}
        lastActivity={{
          skillId: 'sk-1',
          skillName: 'Fractions',
          subjectId: 'sub-math',
          subjectName: 'Maths',
        }}
      />,
    );
    expect(screen.getByText(/Série : 5 jours/)).toBeInTheDocument();
    expect(screen.getByText(/Bravo ! Tu as joué aujourd'hui/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Rejouer/ })).toBeInTheDocument();
  });

  it('rend la branche « urgence » quand série active mais pas joué', () => {
    wrap(
      <StreakReminderCard
        streak={3}
        hasPlayedToday={false}
        lastActivity={null}
      />,
    );
    expect(screen.getByText(/Série : 3 jours/)).toBeInTheDocument();
    expect(
      screen.getByText(/Joue aujourd'hui pour ne pas perdre/),
    ).toBeInTheDocument();
    // Le timer « Il te reste Xh » dépend du temps réel — on vérifie juste le préfixe.
    expect(screen.getByText(/Il te reste/)).toBeInTheDocument();
  });

  it('rend la branche « nouvelle série » quand streak=0', () => {
    wrap(
      <StreakReminderCard
        streak={0}
        hasPlayedToday={false}
        lastActivity={null}
      />,
    );
    expect(
      screen.getByText(/Commence une nouvelle série/),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /C'est parti/ })).toBeInTheDocument();
  });

  it('clic sur le bouton navigue vers lastActivity quand présent', () => {
    wrap(
      <StreakReminderCard
        streak={2}
        hasPlayedToday={false}
        lastActivity={{
          skillId: 'sk-99',
          skillName: 'Op',
          subjectId: 'sub-math',
          subjectName: 'Maths',
        }}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /Jouer/ }));
    expect(navigateMock).toHaveBeenCalledWith(
      '/app/student/exercise/sk-99',
      expect.objectContaining({
        state: expect.objectContaining({
          subjectId: 'sub-math',
          subjectName: 'Maths',
        }),
      }),
    );
  });

  it('clic sans lastActivity renvoie vers /app/student/subjects', () => {
    wrap(
      <StreakReminderCard
        streak={0}
        hasPlayedToday={false}
        lastActivity={null}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /C'est parti/ }));
    expect(navigateMock).toHaveBeenCalledWith('/app/student/subjects');
  });
});

// ── RuleDuJourWidget ────────────────────────────────────────────────────────
describe('<RuleDuJourWidget>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('rend null quand listFormulas retourne []', async () => {
    listFormulasMock.mockResolvedValue([]);
    const { container } = wrap(<RuleDuJourWidget skillsProgress={[]} />);

    await waitFor(() => expect(listFormulasMock).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });

  it('rend la règle quand une formule est disponible', async () => {
    listFormulasMock.mockResolvedValue([
      {
        id: 'f1',
        title: 'Périmètre du rectangle',
        formula: 'P = 2 × (L + l)',
        summary: 'Somme des 4 côtés',
        skillId: 'sk-peri',
      },
    ]);
    wrap(<RuleDuJourWidget skillsProgress={[]} />);

    await waitFor(() => {
      expect(screen.getByText('Périmètre du rectangle')).toBeInTheDocument();
    });
    expect(screen.getByText('P = 2 × (L + l)')).toBeInTheDocument();
  });

  it('clic « Pratiquer » navigue vers l\'exercice du skill', async () => {
    listFormulasMock.mockResolvedValue([
      {
        id: 'f1',
        title: 'Aire du carré',
        formula: 'A = c × c',
        skillId: 'sk-aire',
      },
    ]);
    wrap(<RuleDuJourWidget skillsProgress={[]} />);

    await waitFor(() => {
      expect(screen.getByText('Aire du carré')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole('button', { name: /Pratiquer/ }));
    expect(navigateMock).toHaveBeenCalledWith(
      '/app/student/exercise/sk-aire',
      expect.objectContaining({
        state: { returnPath: '/app/student/dashboard' },
      }),
    );
  });
});

// ── DailyChallengeWidget ────────────────────────────────────────────────────
describe('<DailyChallengeWidget>', () => {
  beforeEach(() => vi.clearAllMocks());

  it('rend le titre, la description et le bonus XP', () => {
    wrap(
      <DailyChallengeWidget
        challenge={{
          title: 'Maîtriser la division',
          desc: 'Réussis 5 exercices sans faute',
          xp: 50,
        }}
      />,
    );
    expect(screen.getByText('Maîtriser la division')).toBeInTheDocument();
    expect(
      screen.getByText(/Réussis 5 exercices sans faute/),
    ).toBeInTheDocument();
    expect(screen.getByText(/\+50 XP/)).toBeInTheDocument();
  });

  it('clic « Relever » navigue vers /app/student/subjects', () => {
    wrap(
      <DailyChallengeWidget
        challenge={{ title: 'X', desc: 'Y', xp: 10 }}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /Relever/ }));
    expect(navigateMock).toHaveBeenCalledWith('/app/student/subjects');
  });
});

// ── CalculMentalWidget ──────────────────────────────────────────────────────
describe('<CalculMentalWidget>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('affiche le message d\'amorce quand aucun record stocké', () => {
    wrap(<CalculMentalWidget />);
    expect(screen.getByText('Calcul Mental')).toBeInTheDocument();
    expect(
      screen.getByText(/60 secondes pour répondre au maximum/),
    ).toBeInTheDocument();
    expect(screen.queryByText(/Record/)).not.toBeInTheDocument();
  });

  it('affiche le record quand localStorage contient une valeur > 0', () => {
    window.localStorage.setItem('sitou_calcul_mental_best', '42');
    wrap(<CalculMentalWidget />);
    expect(screen.getByText(/Record/)).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('clic sur la carte navigue vers /app/student/calcul-mental', () => {
    wrap(<CalculMentalWidget />);
    // La carte entière est cliquable (onClick sur le wrapper) — on déclenche
    // via le bouton « Jouer → » qui partage le navigate parent.
    fireEvent.click(screen.getByRole('button', { name: /Jouer/ }));
    expect(navigateMock).toHaveBeenCalledWith('/app/student/calcul-mental');
  });
});
