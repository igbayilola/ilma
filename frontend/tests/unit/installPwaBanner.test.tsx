import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { InstallPwaBanner } from '../../components/ui/InstallPwaBanner';

const DISMISS_KEY = 'sitou_install_prompt_dismissed_at';

interface FakePromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

function fireBeforeInstallPrompt(outcome: 'accepted' | 'dismissed' = 'accepted') {
  const event = new Event('beforeinstallprompt') as FakePromptEvent;
  let resolveChoice!: (v: { outcome: 'accepted' | 'dismissed' }) => void;
  event.userChoice = new Promise(res => { resolveChoice = res; });
  event.prompt = vi.fn(async () => { resolveChoice({ outcome }); });
  window.dispatchEvent(event);
  return event;
}

describe('InstallPwaBanner', () => {
  beforeEach(() => {
    window.localStorage.clear();
    // Default: not standalone.
    vi.spyOn(window, 'matchMedia').mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders nothing before beforeinstallprompt fires', () => {
    const { container } = render(<InstallPwaBanner />);
    expect(container.firstChild).toBeNull();
  });

  it('shows the banner after capturing beforeinstallprompt + fires shown', async () => {
    const track = vi.fn();
    render(<InstallPwaBanner onTrack={track} />);

    act(() => { fireBeforeInstallPrompt('accepted'); });

    await waitFor(() => {
      expect(screen.getByRole('dialog', { name: /installer/i })).toBeInTheDocument();
    });
    expect(track).toHaveBeenCalledWith('shown');
  });

  it('stays hidden when the app is already standalone', () => {
    (window.matchMedia as any).mockImplementation((query: string) => ({
      matches: query.includes('standalone'),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }));

    const { container } = render(<InstallPwaBanner />);
    act(() => { fireBeforeInstallPrompt(); });
    expect(container.firstChild).toBeNull();
  });

  it('stays hidden when within the dismiss cooldown', () => {
    window.localStorage.setItem(DISMISS_KEY, String(Date.now() - 1000));
    const { container } = render(<InstallPwaBanner />);
    act(() => { fireBeforeInstallPrompt(); });
    expect(container.firstChild).toBeNull();
  });

  it('re-shows after the cooldown expires', async () => {
    window.localStorage.setItem(DISMISS_KEY, String(Date.now() - 30 * 24 * 60 * 60 * 1000));
    render(<InstallPwaBanner />);
    act(() => { fireBeforeInstallPrompt(); });
    await waitFor(() => {
      expect(screen.getByRole('dialog', { name: /installer/i })).toBeInTheDocument();
    });
  });

  it('install button triggers prompt() and reports accepted outcome', async () => {
    const track = vi.fn();
    render(<InstallPwaBanner onTrack={track} />);
    let event: FakePromptEvent;
    act(() => { event = fireBeforeInstallPrompt('accepted'); });

    await waitFor(() => screen.getByRole('button', { name: /installer l'app/i }));
    fireEvent.click(screen.getByRole('button', { name: /installer l'app/i }));

    await waitFor(() => expect(track).toHaveBeenCalledWith('accepted'));
    expect(event!.prompt).toHaveBeenCalled();
    // Banner disappears after a successful install
    expect(screen.queryByRole('dialog')).toBeNull();
    // Acceptance must NOT store a dismiss timestamp (we want the OS to handle it)
    expect(window.localStorage.getItem(DISMISS_KEY)).toBeNull();
  });

  it('dismiss button hides the banner and writes cooldown timestamp', async () => {
    const track = vi.fn();
    render(<InstallPwaBanner onTrack={track} />);
    act(() => { fireBeforeInstallPrompt(); });

    await waitFor(() => screen.getByRole('button', { name: /fermer/i }));
    fireEvent.click(screen.getByRole('button', { name: /fermer/i }));

    expect(track).toHaveBeenCalledWith('dismissed');
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(window.localStorage.getItem(DISMISS_KEY)).not.toBeNull();
  });
});
