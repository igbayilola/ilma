import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ClassInviteShare, buildInviteShareText } from '../../components/teacher/ClassInviteShare';

describe('buildInviteShareText', () => {
  it('includes the class name in the greeting', () => {
    const txt = buildInviteShareText('CM2-A', 'XK4Z8P2T');
    expect(txt).toContain('CM2-A');
  });

  it('uppercases the invite code in the message', () => {
    const txt = buildInviteShareText('CM2', 'xk4z8p2t');
    expect(txt).toContain('XK4Z8P2T');
    expect(txt).not.toContain('xk4z8p2t');
  });

  it('mentions the parent-dashboard step so the recipient knows what to do', () => {
    const txt = buildInviteShareText('CM2', 'X');
    // Must mention "Rejoindre une classe" to match the parent-dashboard CTA
    // label — if the FE rewords that button this test catches the drift.
    expect(txt).toMatch(/Rejoindre une classe/);
  });
});

describe('ClassInviteShare', () => {
  beforeEach(() => {
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    });
  });

  it('renders the code and three share buttons', () => {
    render(<ClassInviteShare className="CM2-A" inviteCode="XK4Z8P2T" />);
    expect(screen.getByText('XK4Z8P2T')).toBeInTheDocument();
    expect(screen.getByLabelText(/copier/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/whatsapp/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sms/i)).toBeInTheDocument();
  });

  it('copy button calls navigator.clipboard.writeText with the code', () => {
    render(<ClassInviteShare className="CM2-A" inviteCode="XK4Z8P2T" />);
    fireEvent.click(screen.getByLabelText(/copier/i));
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('XK4Z8P2T');
  });

  it('whatsapp button opens wa.me with the pre-filled message', () => {
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null);
    render(<ClassInviteShare className="CM2-A" inviteCode="XK4Z8P2T" />);
    fireEvent.click(screen.getByLabelText(/whatsapp/i));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url, target] = openSpy.mock.calls[0];
    expect(url).toMatch(/^https:\/\/wa\.me\/\?text=/);
    expect(decodeURIComponent(String(url))).toContain('XK4Z8P2T');
    expect(decodeURIComponent(String(url))).toContain('CM2-A');
    expect(target).toBe('_blank');
    openSpy.mockRestore();
  });
});
