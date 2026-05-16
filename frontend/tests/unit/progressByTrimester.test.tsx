import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ProgressByTrimester } from '../../components/dashboard/ProgressByTrimester';
import type { SubjectDTO, SkillDTO } from '../../services/contentService';
import type { SkillProgressDTO } from '../../services/progressService';

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

function skill(
  id: string,
  name: string,
  order: number,
  trimester: number,
  weekOrder: number,
): SkillDTO {
  return {
    id,
    name,
    slug: id,
    domainId: 'd1',
    domainName: 'D',
    order,
    trimester,
    weekOrder,
  };
}

function progress(skillId: string, score: number, attempts: number): SkillProgressDTO {
  return { skillId, skillName: skillId, score, totalAttempts: attempts };
}

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('<ProgressByTrimester>', () => {
  it("ne rend rien quand aucun skill n'est séquencé", () => {
    const { container } = renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, []]])}
        progress={[]}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('affiche les 3 barres T1/T2/T3 quand au moins un skill est séquencé', () => {
    const skills = [
      skill('sk-1', 'A', 1, 1, 1),
      skill('sk-2', 'B', 2, 2, 1),
      skill('sk-3', 'C', 3, 3, 1),
    ];
    renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, skills]])}
        progress={[]}
      />,
    );
    const list = screen.getByTestId('trimester-progress-list');
    expect(list.querySelectorAll('li')).toHaveLength(3);
    expect(screen.getByText('Trimestre 1')).toBeInTheDocument();
    expect(screen.getByText('Trimestre 2')).toBeInTheDocument();
    expect(screen.getByText('Trimestre 3')).toBeInTheDocument();
  });

  it('compte correctement les maîtrisés par trimestre', () => {
    const skills = [
      skill('sk-1', 'A', 1, 1, 1),
      skill('sk-2', 'B', 2, 1, 2),
      skill('sk-3', 'C', 3, 2, 1),
    ];
    const prog = [progress('sk-1', 95, 10)]; // T1 → 1/2 maîtrisés
    renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, skills]])}
        progress={prog}
      />,
    );
    expect(screen.getByText('1/2', { exact: false })).toBeInTheDocument(); // T1
    expect(screen.getByText('0/1', { exact: false })).toBeInTheDocument(); // T2 (et T3 vide à 0/0)
  });

  it("expose un lien aria-label quand programmeHref est fourni", () => {
    const skills = [skill('sk-1', 'A', 1, 1, 1)];
    renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, skills]])}
        progress={[]}
        programmeHref="/app/student/programme"
      />,
    );
    expect(screen.getByLabelText('Voir tout mon programme')).toBeInTheDocument();
  });

  it("statique (pas de lien) quand programmeHref est omis", () => {
    const skills = [skill('sk-1', 'A', 1, 1, 1)];
    renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, skills]])}
        progress={[]}
      />,
    );
    expect(screen.queryByLabelText('Voir tout mon programme')).toBeNull();
    expect(screen.queryByText('Détail')).toBeNull();
  });

  it("accepte un titre custom (cas parent)", () => {
    const skills = [skill('sk-1', 'A', 1, 1, 1)];
    renderWithRouter(
      <ProgressByTrimester
        subjects={[subjectMath]}
        skillsBySubject={new Map([[subjectMath.id, skills]])}
        progress={[]}
        title="Où en est Léa dans le programme"
      />,
    );
    expect(
      screen.getByText('Où en est Léa dans le programme'),
    ).toBeInTheDocument();
  });
});
