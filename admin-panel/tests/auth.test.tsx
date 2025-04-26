import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AuthProvider from '../src/components/auth/AuthProvider';
import ProtectedRoute from '../src/components/auth/ProtectedRoute';

// Mock do useRouter
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Mock do localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: vi.fn((key) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('Componentes de Autenticação', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('AuthProvider', () => {
    it('renderiza o conteúdo quando o usuário está autenticado', () => {
      // Simular usuário autenticado
      localStorageMock.setItem('auth_token', 'fake-token');
      localStorageMock.setItem('user', JSON.stringify({
        id: 1,
        name: 'Admin',
        email: 'admin@clinica.com',
        role: 'admin'
      }));
      
      render(
        <AuthProvider>
          <div data-testid="protected-content">Conteúdo Protegido</div>
        </AuthProvider>
      );
      
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      expect(screen.getByText('Conteúdo Protegido')).toBeInTheDocument();
    });

    it('mostra tela de carregamento inicialmente', () => {
      render(
        <AuthProvider>
          <div data-testid="protected-content">Conteúdo Protegido</div>
        </AuthProvider>
      );
      
      // Inicialmente deve mostrar o spinner de carregamento
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('ProtectedRoute', () => {
    it('redireciona para login quando o usuário não está autenticado', () => {
      const { useRouter } = require('next/navigation');
      const pushMock = vi.fn();
      useRouter.mockImplementation(() => ({
        push: pushMock,
      }));
      
      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Conteúdo Protegido</div>
        </ProtectedRoute>
      );
      
      // Deve redirecionar para a página de login
      expect(pushMock).toHaveBeenCalledWith('/login');
    });

    it('renderiza o conteúdo quando o usuário está autenticado', () => {
      // Simular usuário autenticado
      localStorageMock.setItem('auth_token', 'fake-token');
      localStorageMock.setItem('user', JSON.stringify({
        id: 1,
        name: 'Admin',
        email: 'admin@clinica.com',
        role: 'admin'
      }));
      
      render(
        <ProtectedRoute>
          <div data-testid="protected-content">Conteúdo Protegido</div>
        </ProtectedRoute>
      );
      
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      expect(screen.getByText('Conteúdo Protegido')).toBeInTheDocument();
    });
  });
});
