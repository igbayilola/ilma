/**
 * Tests rendu `SubjectsPage` (iter 33, P1 punch-list iter 32).
 *
 * Applique le pattern de robustesse iter 28 (Programme) / iter 29
 * (Dashboard) : garde `gradeLevelId` + état vide retry + cancel flag.
 */
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';

const { listSubjectsMock } = vi.hoisted(() => ({
  listSubjectsMock: vi.fn(),
}));

vi.mock('../../services/contentService', async () => {
  const actual: any = await vi.importActual('../../services/contentService');
  return {
    ...actual,
    contentService: { listSubjects: listSubjectsMock },
  };
});

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

const { navigateMock } = vi.hoisted(() => ({ navigateMock: vi.fn() }));
vi.mock('react-router-dom', async () => {
  const actual: any = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

import { SubjectsPage } from '../../pages/student/Subjects';

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

describe('<SubjectsPage>', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resetAuthState();
    listSubjectsMock.mockResolvedValue([SUBJECT]);
  });

  it('garde quand gradeLevelId manquant : message + CTA classe (iter 33)', () => {
    setAuthState({
      user: { id: 'u1' },
      activeProfile: { id: 'p1' },
    });

    render(
      <MemoryRouter>
        <SubjectsPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Choisis ta classe')).toBeInTheDocument();
    expect(listSubjectsMock).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /Choisir ma classe/ }));
    expect(navigateMock).toHaveBeenCalledWith('/select-profile');
  });

  it('affiche l\'état vide retry quand subjects=[] post-chargement', async () => {
    listSubjectsMock.mockResolvedValue([]);

    render(
      <MemoryRouter>
        <SubjectsPage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Matières indisponibles')).toBeInTheDocument();
    });

    // Le clic Réessayer relance la requête.
    listSubjectsMock.mockResolvedValueOnce([SUBJECT]);
    fireEvent.click(screen.getByRole('button', { name: /Réessayer/ }));
    await waitFor(() => {
      expect(listSubjectsMock).toHaveBeenCalledTimes(2);
    });
  });

  it('charge et rend les matières via le gradeLevelId du profil actif', async () => {
    render(
      <MemoryRouter>
        <SubjectsPage />
      </MemoryRouter>,
    );

    await waitFor(() => expect(listSubjectsMock).toHaveBeenCalledWith('gl-cm2'));
    await waitFor(() => {
      expect(screen.getByText(/Maths/)).toBeInTheDocument();
    });
  });
});
