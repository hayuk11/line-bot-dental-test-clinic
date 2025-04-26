import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AgendamentosPage from '../src/app/agendamentos/page';

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

describe('AgendamentosPage', () => {
  beforeEach(() => {
    localStorageMock.clear();
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
    render(<AgendamentosPage />);
    
    expect(screen.getByText('Gerenciamento de Agendamentos')).toBeInTheDocument();
    expect(screen.getByText('Visualização em Lista')).toBeInTheDocument();
    expect(screen.getByText('Visualização em Calendário')).toBeInTheDocument();
  });

  it('alterna entre visualizações de lista e calendário', () => {
    render(<AgendamentosPage />);
    
    // Por padrão, a visualização em lista deve estar ativa
    expect(screen.getByText('Akira Tanaka')).toBeInTheDocument();
    
    // Clicar no botão de visualização em calendário
    const calendarViewButton = screen.getByText('Visualização em Calendário');
    fireEvent.click(calendarViewButton);
    
    // Deve mostrar o calendário
    expect(screen.getByText('Abril 2025')).toBeInTheDocument();
    
    // Voltar para visualização em lista
    const listViewButton = screen.getByText('Visualização em Lista');
    fireEvent.click(listViewButton);
    
    // Deve mostrar a lista novamente
    expect(screen.getByText('Akira Tanaka')).toBeInTheDocument();
  });

  it('filtra agendamentos por status', () => {
    render(<AgendamentosPage />);
    
    // Inicialmente, todos os agendamentos devem estar visíveis
    expect(screen.getByText('Akira Tanaka')).toBeInTheDocument();
    expect(screen.getByText('Maria Silva')).toBeInTheDocument();
    
    // Filtrar por status "Confirmado"
    const filterSelect = screen.getByLabelText('Filtrar por status:');
    fireEvent.change(filterSelect, { target: { value: 'Confirmado' } });
    
    // Apenas agendamentos confirmados devem estar visíveis
    expect(screen.getByText('Akira Tanaka')).toBeInTheDocument();
    expect(screen.queryByText('Maria Silva')).not.toBeInTheDocument();
    
    // Filtrar por status "Aguardando"
    fireEvent.change(filterSelect, { target: { value: 'Aguardando' } });
    
    // Apenas agendamentos aguardando devem estar visíveis
    expect(screen.queryByText('Akira Tanaka')).not.toBeInTheDocument();
    expect(screen.getByText('Maria Silva')).toBeInTheDocument();
  });

  it('permite alterar o status de um agendamento', () => {
    // Mock da função console.log para verificar se foi chamada
    const consoleSpy = vi.spyOn(console, 'log');
    
    render(<AgendamentosPage />);
    
    // Encontrar o select de status do primeiro agendamento
    const statusSelect = screen.getAllByRole('combobox')[1]; // O primeiro é o filtro de status
    
    // Alterar o status para "Recusado"
    fireEvent.change(statusSelect, { target: { value: 'Recusado' } });
    
    // Verificar se a função de alteração de status foi chamada
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Alterando status do agendamento'));
  });
});
