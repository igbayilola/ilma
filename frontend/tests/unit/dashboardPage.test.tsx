import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// ── Mock services -----------------------------------------------------------
const {
  listSubjectsMock,
  listSkillsMock,
  listFormulasMock,
  getProgressMock,
  getPredictiveScoreMock,
} = vi.hoisted(() => ({
  listSubjectsMock: vi.fn(),
  listSkillsMock: vi.fn(),
  listFormulasMock: vi.fn(),
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
      listFormulas: listFormulasMock,
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
    examService: { getPredictiveScore: getPredictiveScoreMock },
  };
});

// ── Mock auth store (mutable for tests iter 29) ----------------------------
const { useAuthStoreMock, setAuthState, resetAuthState } = vi.hoisted(() => {
  const DEFAULT = {
    user: {
      id: 'u1',
      name: 'Adèle',
      gradeLevelId: 'gl-cm2',
      streak: 3,
      xp: 120,
      xpToNextLevel: 1000,
      level: 2,
    },
    activeProfile: {
      id: 'p1',
      displayName: 'Adèle',
      gradeLevelId: 'gl-cm2',
      avatarUrl: null,
    },
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

// ── Mock app store (selector form) -----------------------------------------
const { useAppStoreMock } = vi.hoisted(() => {
  const state: any = {
    lastActivity: null,
    dailyExerciseCount: 0,
  };
  const useAppStoreMock: any = (selector?: any) =>
    selector ? selector(state) : state;
  useAppStoreMock.getState = () => state;
  return { useAppStoreMock };
});

vi.mock('../../store', () => ({
  useAppStore: useAppStoreMock,
}));

// ── Mock useNavigate -------------------------------------------------------
const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

import { Dashboard } from '../../pages/Dashboard';

const SUBJECT = {
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

describe('<Dashboard>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetAuthState();
    listSubjectsMock.mockResolvedValue([SUBJECT]);
    listSkillsMock.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 50,
      pages: 0,
    });
    listFormulasMock.mockResolvedValue([]);
    getProgressMock.mockResolvedValue([]);
    getPredictiveScoreMock.mockResolvedValue({
      predicted: 12,
      confidence: 0.5,
      coverage: 0.5,
      weak_skills: [],
    });
  });

  it('garde quand gradeLevelId manquant : message + CTA classe (iter 29)', () => {
    setAuthState({
      user: { id: 'u1', name: 'Adèle' },
      activeProfile: { id: 'p1', displayName: 'Adèle' },
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>,
    );

    expect(screen.getByText('Choisis ta classe')).toBeInTheDocument();
    // L'effet ne doit pas tenter de charger sans gradeLevelId.
    expect(listSubjectsMock).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /Choisir ma classe/ }));
    expect(navigateMock).toHaveBeenCalledWith('/select-profile');
  });

  it('charge subjects via le gradeLevelId du profil actif (smoke iter 29)', async () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>,
    );

    await waitFor(() => expect(listSubjectsMock).toHaveBeenCalledWith('gl-cm2'));
    // Rendu nominal : la salutation utilise displayName du profil actif.
    await waitFor(() =>
      expect(screen.getByText(/Bonjour, Adèle/)).toBeInTheDocument(),
    );
  });
});
