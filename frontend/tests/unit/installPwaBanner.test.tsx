import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { InstallPwaBanner, isIosSafari } from '../../components/ui/InstallPwaBanner';

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

// ── iOS Safari path (iter 18) ───────────────────────────────

describe('isIosSafari', () => {
  const originalUA = window.navigator.userAgent;

  function setUA(ua: string, maxTouchPoints = 0) {
    Object.defineProperty(window.navigator, 'userAgent', { value: ua, configurable: true });
    Object.defineProperty(window.navigator, 'maxTouchPoints', { value: maxTouchPoints, configurable: true });
  }

  afterEach(() => {
    Object.defineProperty(window.navigator, 'userAgent', { value: originalUA, configurable: true });
    Object.defineProperty(window.navigator, 'maxTouchPoints', { value: 0, configurable: true });
  });

  it('detects iPhone', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1');
    expect(isIosSafari()).toBe(true);
  });

  it('detects iPadOS 13+ (reports as desktop Mac)', () => {
    setUA('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15', 5);
    expect(isIosSafari()).toBe(true);
  });

  it('rejects desktop Mac without touch', () => {
    setUA('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15', 0);
    expect(isIosSafari()).toBe(false);
  });

  it('rejects Android', () => {
    setUA('Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36');
    expect(isIosSafari()).toBe(false);
  });

  it('rejects iOS in-app browsers (Facebook FBAN, Instagram)', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 [FBAN/FBIOS;FBAV/420.0.0]');
    expect(isIosSafari()).toBe(false);
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Instagram 100.0.0');
    expect(isIosSafari()).toBe(false);
  });
});

describe('InstallPwaBanner iOS path', () => {
  const originalUA = window.navigator.userAgent;

  beforeEach(() => {
    window.localStorage.clear();
    vi.useFakeTimers();
    vi.spyOn(window, 'matchMedia').mockImplementation((query: string) => ({
      matches: false, media: query, onchange: null,
      addListener: () => {}, removeListener: () => {},
      addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => false,
    }) as MediaQueryList);
    Object.defineProperty(window.navigator, 'userAgent', {
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1',
      configurable: true,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    Object.defineProperty(window.navigator, 'userAgent', { value: originalUA, configurable: true });
  });

  it('shows the iOS instructions after the initial delay and reports shown', async () => {
    const track = vi.fn();
    render(<InstallPwaBanner onTrack={track} />);
    // Banner hidden initially (1.5 s delay to avoid being intrusive on load)
    expect(screen.queryByRole('dialog')).toBeNull();

    await act(async () => { vi.advanceTimersByTime(1500); });

    expect(screen.getByRole('dialog', { name: /installer/i })).toBeInTheDocument();
    expect(screen.getByText(/Sur l'écran d'accueil/i)).toBeInTheDocument();
    expect(track).toHaveBeenCalledWith('shown');
  });

  it('iOS dismiss writes cooldown and reports dismissed', async () => {
    const track = vi.fn();
    render(<InstallPwaBanner onTrack={track} />);
    await act(async () => { vi.advanceTimersByTime(1500); });

    fireEvent.click(screen.getByRole('button', { name: /fermer/i }));

    expect(track).toHaveBeenCalledWith('dismissed');
    expect(window.localStorage.getItem(DISMISS_KEY)).not.toBeNull();
    expect(screen.queryByRole('dialog')).toBeNull();
  });
});
