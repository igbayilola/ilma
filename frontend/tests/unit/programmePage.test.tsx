import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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
const { useAuthStoreMock } = vi.hoisted(() => {
  const useAuthStoreMock: any = () => ({
    user: { id: 'u1', gradeLevelId: 'gl-cm2' },
    activeProfile: { id: 'p1', gradeLevelId: 'gl-cm2' },
  });
  useAuthStoreMock.getState = () => ({
    user: { id: 'u1', gradeLevelId: 'gl-cm2' },
    activeProfile: { id: 'p1', gradeLevelId: 'gl-cm2' },
    accessToken: null,
  });
  return { useAuthStoreMock };
});

vi.mock('../../store/authStore', () => ({
  useAuthStore: useAuthStoreMock,
}));

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
});
