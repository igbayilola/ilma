
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { StreakReminderCard } from '../../pages/Dashboard';

// Mock lucide-react icons to simple spans so we can assert on them
vi.mock('lucide-react', () => ({
  Flame: (props: any) => <span data-testid="flame-icon" {...props} />,
  Clock: (props: any) => <span data-testid="clock-icon" {...props} />,
  Sprout: (props: any) => <span data-testid="sprout-icon" {...props} />,
  Play: (props: any) => <span data-testid="play-icon" {...props} />,
  Zap: (props: any) => <span data-testid="zap-icon" {...props} />,
  Trophy: (props: any) => <span data-testid="trophy-icon" {...props} />,
  Download: (props: any) => <span data-testid="download-icon" {...props} />,
  Book: (props: any) => <span data-testid="book-icon" {...props} />,
  Calculator: (props: any) => <span data-testid="calculator-icon" {...props} />,
  FlaskConical: (props: any) => <span data-testid="flask-icon" {...props} />,
  Globe: (props: any) => <span data-testid="globe-icon" {...props} />,
  BookOpen: (props: any) => <span data-testid="bookopen-icon" {...props} />,
  PlayCircle: (props: any) => <span data-testid="playcircle-icon" {...props} />,
}));

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('StreakReminderCard — 3 streak states', () => {
  describe('State 1: Streak active (hasPlayedToday=true, streak > 0)', () => {
    it('shows the streak count with fire icon and positive message', () => {
      renderWithRouter(
        <StreakReminderCard streak={5} hasPlayedToday={true} lastActivity={null} />
      );

      // Should display the streak day count
      expect(screen.getByText(/Série : 5 jours/i)).toBeInTheDocument();

      // Should show positive reinforcement message
      expect(screen.getByText(/Bravo.*Tu as joué aujourd'hui/i)).toBeInTheDocument();

      // Should show fire/flame icon
      expect(screen.getByTestId('flame-icon')).toBeInTheDocument();

      // Should have green background (positive state)
      const container = screen.getByText(/Série : 5 jours/i).closest('.clay-card');
      expect(container).toHaveClass('bg-gradient-to-r');
      expect(container?.className).toContain('green');

      // Should show "Rejouer" button
      expect(screen.getByText(/Rejouer/i)).toBeInTheDocument();
    });

    it('uses singular "jour" for streak of 1', () => {
      renderWithRouter(
        <StreakReminderCard streak={1} hasPlayedToday={true} lastActivity={null} />
      );

      // "jour" without "s" for singular
      expect(screen.getByText(/Série : 1 jour !/i)).toBeInTheDocument();
      // Make sure it does NOT say "jours"
      expect(screen.queryByText(/Série : 1 jours/i)).not.toBeInTheDocument();
    });
  });

  describe('State 2: Streak in danger (hasPlayedToday=false, streak > 0)', () => {
    it('shows urgency message with countdown to midnight', () => {
      renderWithRouter(
        <StreakReminderCard streak={3} hasPlayedToday={false} lastActivity={null} />
      );

      // Should display the streak day count
      expect(screen.getByText(/Série : 3 jours/i)).toBeInTheDocument();

      // Should show urgency message
      expect(screen.getByText(/Joue aujourd'hui pour ne pas perdre ta série/i)).toBeInTheDocument();

      // Should show the countdown clock icon
      expect(screen.getByTestId('clock-icon')).toBeInTheDocument();

      // Should show the time remaining text
      expect(screen.getByText(/Il te reste.*avant minuit/i)).toBeInTheDocument();

      // Should have orange background (danger/warning state)
      const container = screen.getByText(/Série : 3 jours/i).closest('.clay-card');
      expect(container?.className).toContain('orange');

      // Should show "Jouer" call-to-action button
      expect(screen.getByText(/Jouer/i)).toBeInTheDocument();
    });

    it('shows fire icon with wiggle animation', () => {
      renderWithRouter(
        <StreakReminderCard streak={7} hasPlayedToday={false} lastActivity={null} />
      );

      const flameIcon = screen.getByTestId('flame-icon');
      expect(flameIcon).toBeInTheDocument();
    });
  });

  describe('State 3: Streak = 0 (no active streak)', () => {
    it('shows encouragement to start a new streak', () => {
      renderWithRouter(
        <StreakReminderCard streak={0} hasPlayedToday={false} lastActivity={null} />
      );

      // Should show "start a new streak" message
      expect(screen.getByText(/Commence une nouvelle série/i)).toBeInTheDocument();

      // Should show the explanation
      expect(screen.getByText(/1 exercice = 1 jour de série/i)).toBeInTheDocument();

      // Should show sprout icon (growth metaphor)
      expect(screen.getByTestId('sprout-icon')).toBeInTheDocument();

      // Should NOT show fire/flame icon
      expect(screen.queryByTestId('flame-icon')).not.toBeInTheDocument();

      // Should NOT show clock icon (no countdown needed)
      expect(screen.queryByTestId('clock-icon')).not.toBeInTheDocument();

      // Should have blue/sky background (neutral/encouraging state)
      const container = screen.getByText(/Commence une nouvelle série/i).closest('.clay-card');
      expect(container?.className).toContain('sky');

      // Should show "C'est parti" call-to-action button
      expect(screen.getByText(/C'est parti/i)).toBeInTheDocument();
    });

    it('still shows encouragement even if hasPlayedToday is true but streak is 0', () => {
      // Edge case: user played today but streak was already 0 (e.g., just started)
      renderWithRouter(
        <StreakReminderCard streak={0} hasPlayedToday={true} lastActivity={null} />
      );

      // With streak=0, the component falls through to the "no streak" state
      // regardless of hasPlayedToday
      expect(screen.getByText(/Commence une nouvelle série/i)).toBeInTheDocument();
    });
  });

  describe('Navigation behavior', () => {
    it('renders "Jouer" button linking to subjects when no lastActivity', () => {
      renderWithRouter(
        <StreakReminderCard streak={3} hasPlayedToday={false} lastActivity={null} />
      );

      // Button should exist and be clickable
      const button = screen.getByText(/Jouer/i);
      expect(button).toBeInTheDocument();
      expect(button.tagName.toLowerCase()).toBe('button');
    });

    it('renders action button when lastActivity is provided', () => {
      const lastActivity = {
        skillId: 'skill-123',
        skillName: 'Les fractions',
        subjectId: 'math-1',
        subjectName: 'Mathématiques',
      };

      renderWithRouter(
        <StreakReminderCard streak={5} hasPlayedToday={true} lastActivity={lastActivity} />
      );

      // "Rejouer" button should be rendered in the active streak state
      const button = screen.getByText(/Rejouer/i);
      expect(button).toBeInTheDocument();
    });
  });
});
