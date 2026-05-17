import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// ── Mock contentService + progressService + examService ────────────────────
const { listSubjectsMock, listSkillsMock, getProgressMock, getPredictiveScoreMock } =
  vi.hoisted(() => ({
    listSubjectsMock: vi.fn(),
    listSkillsMock: vi.fn(),
    getProgressMock: vi.fn(),
    getPredictiveScoreMock: vi.fn(),
  }));

vi.mock('../../services/contentService', async () => {
  const actual: any = await vi.importActual('../../services/contentService');
  return {
    ...actual,
    contentService: {
      listSubjects: listSubjectsMock,
      listSkills: listSkillsMock,
    },
  };
});

vi.mock('../../services/progressService', async () => {
  const actual: any = await vi.importActual('../../services/progressService');
  return {
    ...actual,
    progressService: { getSkillsProgress: getProgressMock },
  };
});

vi.mock('../../services/examService', async () => {
  const actual: any = await vi.importActual('../../services/examService');
  return {
    ...actual,
    examService: {
      getPredictiveScore: getPredictiveScoreMock,
    },
  };
});

// ── Mock the auth store : juste ce dont la page a besoin ───────────────────
// State mutable pour que les tests iter 28 puissent simuler "pas de classe".
const { useAuthStoreMock, setAuthState, resetAuthState } = vi.hoisted(() => {
  const DEFAULT = {
    user: { id: 'u1', gradeLevelId: 'gl-cm2' },
    activeProfile: { id: 'p1', gradeLevelId: 'gl-cm2' },
    accessToken: null,
  };
  let state: any = { ...DEFAULT };
  const useAuthStoreMock: any = () => state;
  useAuthStoreMock.getState = () => state;
  const setAuthState = (s: any) => {
    state = { ...state, ...s };
  };
  const resetAuthState = () => {
    state = { ...DEFAULT };
  };
  return { useAuthStoreMock, setAuthState, resetAuthState };
});

vi.mock('../../store/authStore', () => ({
  useAuthStore: useAuthStoreMock,
}));

// Mock useNavigate pour vérifier la redirection iter 28 sans full routing.
const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

import { ProgrammePage } from '../../pages/student/Programme';

const SUBJECT = {
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

const SKILL = {
  id: 'sk-1',
  name: 'Numération 1',
  slug: 'num1',
  domainId: 'd1',
  domainName: 'Numération',
  order: 1,
  trimester: 1,
  weekOrder: 1,
};

describe('<ProgrammePage>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetAuthState();
    listSubjectsMock.mockResolvedValue([SUBJECT]);
    listSkillsMock.mockResolvedValue({
      items: [SKILL],
      total: 1,
      page: 1,
      page_size: 50,
      pages: 1,
    });
    getProgressMock.mockResolvedValue([]);
    getPredictiveScoreMock.mockResolvedValue({
      predicted: 13.5,
      confidence: 0.8,
      coverage: 0.6,
      weak_skills: [],
    });
  });

  it('rend le titre principal de la page', async () => {
    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );
    expect(screen.getByText('Mon programme CM2')).toBeInTheDocument();
    // Drain les effets async pour silencer les warnings act().
    await waitFor(() => expect(listSubjectsMock).toHaveBeenCalled());
  });

  it('intègre la carte CEP en tête (iter 26)', async () => {
    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );
    await waitFor(() => {
      expect(screen.getByText('Score CEP estimé')).toBeInTheDocument();
    });
  });

  it('charge subjects + skills via le gradeLevelId du profil actif', async () => {
    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );
    await waitFor(() => expect(listSubjectsMock).toHaveBeenCalledWith('gl-cm2'));
    expect(listSkillsMock).toHaveBeenCalledWith(SUBJECT.id);
  });

  it('rend la timeline une fois les données chargées (iter 22)', async () => {
    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );
    await waitFor(() => {
      expect(screen.getByText(/Trimestre 1/)).toBeInTheDocument();
    });
  });

  it('garde quand gradeLevelId manquant : message + CTA classe (iter 28)', async () => {
    setAuthState({
      user: { id: 'u1' },
      activeProfile: { id: 'p1' },
    });

    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Choisis ta classe')).toBeInTheDocument();
    // L'effet ne doit pas tenter de charger sans gradeLevelId.
    expect(listSubjectsMock).not.toHaveBeenCalled();
    // La carte CEP est masquée hors contexte classe.
    expect(screen.queryByText('Score CEP estimé')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Choisir ma classe/ }));
    expect(navigateMock).toHaveBeenCalledWith('/select-profile');
  });

  it('affiche l\'état vide retry quand subjects=[] post-chargement (iter 28)', async () => {
    listSubjectsMock.mockResolvedValue([]);

    render(
      <MemoryRouter>
        <ProgrammePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Programme indisponible')).toBeInTheDocument();
    });
    expect(listSkillsMock).not.toHaveBeenCalled();

    // Le clic Réessayer relance la requête (deuxième appel à listSubjects).
    listSubjectsMock.mockResolvedValueOnce([SUBJECT]);
    fireEvent.click(screen.getByRole('button', { name: /Réessayer/ }));
    await waitFor(() => {
      expect(listSubjectsMock).toHaveBeenCalledTimes(2);
    });
  });
});
