/**
 * Tests rendu CEPPredictionCard (iter 35, P2 punch-list iter 32).
 *
 * Composant rendu sur Dashboard (depuis iter 7) ET sur Programme
 * (depuis iter 26). Sans test rendu jusqu'ici.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import type {
  PredictiveScoreDTO,
  PredictiveScoreWeakSkillDTO,
} from '../../services/examService';

const { getPredictiveScoreMock } = vi.hoisted(() => ({
  getPredictiveScoreMock: vi.fn(),
}));

vi.mock('../../services/examService', async () => {
  const actual: any = await vi.importActual('../../services/examService');
  return {
    ...actual,
    examService: { getPredictiveScore: getPredictiveScoreMock },
  };
});

const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

import { CEPPredictionCard } from '../../components/dashboard/CEPPredictionCard';

function makeScore(overrides: Partial<PredictiveScoreDTO> = {}): PredictiveScoreDTO {
  return {
    predicted: 12.5,
    confidence: 0.6,
    coverage: 0.5,
    weighted_avg_score: 60,
    weak_skills: [],
    subject_id: null,
    ...overrides,
  };
}

function makeWeak(
  overrides: Partial<PredictiveScoreWeakSkillDTO> = {},
): PredictiveScoreWeakSkillDTO {
  return {
    skill_id: 'sk-1',
    name: 'Fractions difficiles',
    smart_score: 32,
    cep_frequency: 5,
    subject_id: 'sub-math',
    domain_id: 'd-num',
    ...overrides,
  };
}

function renderCard() {
  return render(
    <MemoryRouter>
      <CEPPredictionCard />
    </MemoryRouter>,
  );
}

describe('<CEPPredictionCard>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('rend l\'état loading (skeletons, pas de score)', () => {
    // Promesse qui ne résout jamais pendant le test.
    getPredictiveScoreMock.mockReturnValue(new Promise(() => {}));

    renderCard();

    expect(screen.queryByText('Score CEP estimé')).not.toBeInTheDocument();
    expect(screen.queryByRole('meter')).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Impossible de calculer le score/),
    ).not.toBeInTheDocument();
  });

  it('rend l\'état d\'erreur quand le fetch échoue', async () => {
    getPredictiveScoreMock.mockRejectedValue(new Error('500'));

    renderCard();

    await waitFor(() => {
      expect(
        screen.getByText(/Impossible de calculer le score/),
      ).toBeInTheDocument();
    });
    expect(screen.queryByRole('meter')).not.toBeInTheDocument();
  });

  it('affiche le score et le badge « Très bien » pour predicted ≥ 14', async () => {
    getPredictiveScoreMock.mockResolvedValue(makeScore({ predicted: 15.3 }));

    renderCard();

    await waitFor(() => {
      expect(screen.getByText('Score CEP estimé')).toBeInTheDocument();
    });
    expect(screen.getByText('15.3')).toBeInTheDocument();
    expect(screen.getByText('Très bien')).toBeInTheDocument();
  });

  it('expose un meter avec aria-valuenow=predicted', async () => {
    getPredictiveScoreMock.mockResolvedValue(makeScore({ predicted: 9.7 }));

    renderCard();

    await waitFor(() => {
      const meter = screen.getByRole('meter', { name: /Score CEP prédit sur 20/ });
      expect(meter).toHaveAttribute('aria-valuenow', '9.7');
      expect(meter).toHaveAttribute('aria-valuemin', '0');
      expect(meter).toHaveAttribute('aria-valuemax', '20');
    });
    // < 10 → bande « À renforcer ».
    expect(screen.getByText('À renforcer')).toBeInTheDocument();
  });

  it('rend la liste des weak_skills et navigue au clic', async () => {
    const weak = makeWeak({
      skill_id: 'sk-77',
      subject_id: 'sub-math',
      domain_id: 'd-num',
      name: 'Division euclidienne',
      smart_score: 28,
    });
    getPredictiveScoreMock.mockResolvedValue(
      makeScore({ predicted: 11, weak_skills: [weak] }),
    );

    renderCard();

    await waitFor(() => {
      expect(screen.getByText('Division euclidienne')).toBeInTheDocument();
    });
    expect(screen.getByText('À renforcer')).toBeInTheDocument(); // section header
    expect(screen.getByText('28%')).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole('button', { name: /Division euclidienne/ }),
    );
    expect(navigateMock).toHaveBeenCalledWith(
      '/app/student/subjects/sub-math/domains/d-num/skills/sk-77',
    );
  });

  it('weak_skills=[] avec coverage>0 → message « Aucun point faible détecté »', async () => {
    getPredictiveScoreMock.mockResolvedValue(
      makeScore({ predicted: 16, coverage: 0.8, weak_skills: [] }),
    );

    renderCard();

    await waitFor(() => {
      expect(
        screen.getByText(/Aucun point faible détecté/),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByText(/Commence à pratiquer pour obtenir/),
    ).not.toBeInTheDocument();
  });

  it('weak_skills=[] avec coverage=0 → message « Commence à pratiquer »', async () => {
    getPredictiveScoreMock.mockResolvedValue(
      makeScore({ predicted: 10, coverage: 0, weak_skills: [] }),
    );

    renderCard();

    await waitFor(() => {
      expect(
        screen.getByText(/Commence à pratiquer pour obtenir une estimation/),
      ).toBeInTheDocument();
    });
    expect(
      screen.queryByText(/Aucun point faible détecté/),
    ).not.toBeInTheDocument();
  });
});
