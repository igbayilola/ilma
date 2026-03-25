
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginPage } from '../../pages/auth/Login';
import { useAuthStore } from '../../store/authStore';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the Auth Store — vi.hoisted ensures these are available when vi.mock is hoisted
const { loginMock, mockStoreHook } = vi.hoisted(() => {
  const loginMock = vi.fn();
  const mockStoreHook: any = () => ({
    login: loginMock,
    isLoading: false,
    error: null,
  });
  mockStoreHook.getState = () => ({ user: { role: 'STUDENT' } });
  return { loginMock, mockStoreHook };
});

vi.mock('../../store/authStore', () => ({
  useAuthStore: mockStoreHook,
}));

// Mock Router navigation — vi.hoisted ensures navigateMock is available when vi.mock is hoisted
const { navigateMock } = vi.hoisted(() => {
  return { navigateMock: vi.fn() };
});

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual as any,
    useNavigate: () => navigateMock,
    useLocation: () => ({ state: null }),
  };
});

describe('Login Page Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('allows user to input credentials and submit', async () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    // 1. Check for Inputs
    const emailInput = screen.getByLabelText(/Email/i);
    const passInput = screen.getByLabelText(/Mot de passe/i);
    const submitBtn = screen.getByRole('button', { name: /se connecter/i });

    // 2. Simulate User Input
    fireEvent.change(emailInput, { target: { value: 'test@sitou.app' } });
    fireEvent.change(passInput, { target: { value: 'password123' } });

    // 3. Submit
    fireEvent.click(submitBtn);

    // 4. Assert Store Action was called
    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        identifier: 'test@sitou.app',
        password: 'password123'
      });
    });

    // 5. Assert Redirect (based on store mock return)
    await waitFor(() => {
        expect(navigateMock).toHaveBeenCalledWith('/app/student/dashboard');
    });
  });

  it('validates empty fields', async () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /se connecter/i });
    fireEvent.click(submitBtn);

    // Should not call login
    expect(loginMock).not.toHaveBeenCalled();
  });
});
