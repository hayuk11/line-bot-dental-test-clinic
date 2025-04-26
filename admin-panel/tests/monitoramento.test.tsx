import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MonitoringDashboard from '../src/app/monitoramento/page';

// Mock do useRouter
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

// Mock do localStorage
const localStorageMock = (() => {
  let store = {
    'system_logs': JSON.stringify([
      {
        timestamp: '2025-04-26T15:00:00.000Z',
        level: 'INFO',
        module: 'LoggingSystem',
        message: 'Logging system initialized',
        data: { level: 1 }
      },
      {
        timestamp: '2025-04-26T15:05:00.000Z',
        level: 'ERROR',
        module: 'AuthProvider',
        message: 'Failed login attempt',
        data: { email: 'test@example.com' }
      }
    ]),
    'activity_logs': JSON.stringify([
      {
        userId: 1,
        userName: 'Admin',
        timestamp: '2025-04-26T15:10:00.000Z',
        path: '/dashboard',
        action: 'page_view',
        userAgent: 'Mozilla/5.0'
      }
    ]),
    'performance_metrics': JSON.stringify({
      pageLoads: 10,
      apiCalls: 5,
      errors: 1,
      responseTime: [
        { url: '/api/users', duration: 120, timestamp: '2025-04-26T15:15:00.000Z' }
      ]
    })
  };
  
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

describe('MonitoringDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Simular usuário autenticado
    localStorageMock.setItem('auth_token', 'fake-token');
    localStorageMock.setItem('user', JSON.stringify({
      id: 1,
      name: 'Admin',
      email: 'admin@clinica.com',
      role: 'admin'
    }));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renderiza corretamente', () => {
    render(<MonitoringDashboard />);
    
    expect(screen.getByText('Monitoramento do Sistema')).toBeInTheDocument();
    expect(screen.getByText('Logs do Sistema')).toBeInTheDocument();
    expect(screen.getByText('Atividades dos Usuários')).toBeInTheDocument();
    expect(screen.getByText('Desempenho do Sistema')).toBeInTheDocument();
  });

  it('exibe logs do sistema', () => {
    render(<MonitoringDashboard />);
    
    // Por padrão, a aba de logs do sistema deve estar ativa
    expect(screen.getByText('Logging system initialized')).toBeInTheDocument();
    expect(screen.getByText('Failed login attempt')).toBeInTheDocument();
  });

  it('permite filtrar logs por nível', () => {
    render(<MonitoringDashboard />);
    
    // Filtrar por nível ERROR
    const filterSelect = screen.getByLabelText('Filtrar por Nível');
    fireEvent.change(filterSelect, { target: { value: 'ERROR' } });
    
    // Apenas logs de erro devem estar visíveis
    expect(screen.queryByText('Logging system initialized')).not.toBeInTheDocument();
    expect(screen.getByText('Failed login attempt')).toBeInTheDocument();
  });

  it('alterna entre as abas de monitoramento', () => {
    render(<MonitoringDashboard />);
    
    // Clicar na aba de atividades dos usuários
    const activitiesTab = screen.getByText('Atividades dos Usuários');
    fireEvent.click(activitiesTab);
    
    // Deve mostrar as atividades dos usuários
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByText('/dashboard')).toBeInTheDocument();
    
    // Clicar na aba de desempenho do sistema
    const performanceTab = screen.getByText('Desempenho do Sistema');
    fireEvent.click(performanceTab);
    
    // Deve mostrar as métricas de desempenho
    expect(screen.getByText('Carregamentos de Página')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument(); // pageLoads
    expect(screen.getByText('5')).toBeInTheDocument(); // apiCalls
    expect(screen.getByText('1')).toBeInTheDocument(); // errors
  });

  it('permite buscar nas mensagens de log', () => {
    render(<MonitoringDashboard />);
    
    // Buscar por "login"
    const searchInput = screen.getByLabelText('Buscar nas Mensagens');
    fireEvent.change(searchInput, { target: { value: 'login' } });
    
    // Apenas logs com "login" devem estar visíveis
    expect(screen.queryByText('Logging system initialized')).not.toBeInTheDocument();
    expect(screen.getByText('Failed login attempt')).toBeInTheDocument();
  });
});
