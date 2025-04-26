import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ConfiguracoesPage from '../src/app/configuracoes/page';

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

// Mock do alert
window.alert = vi.fn();

describe('ConfiguracoesPage', () => {
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
    render(<ConfiguracoesPage />);
    
    expect(screen.getByText('Configurações do Sistema')).toBeInTheDocument();
    expect(screen.getByText('Informações Gerais')).toBeInTheDocument();
    expect(screen.getByText('Horários de Funcionamento')).toBeInTheDocument();
    expect(screen.getByText('Configurações do Chatbot')).toBeInTheDocument();
    expect(screen.getByText('Notificações')).toBeInTheDocument();
  });

  it('alterna entre as abas de configuração', () => {
    render(<ConfiguracoesPage />);
    
    // Por padrão, a aba de informações gerais deve estar ativa
    expect(screen.getByLabelText('Nome da Clínica')).toBeInTheDocument();
    
    // Clicar na aba de horários de funcionamento
    const horariosTab = screen.getByText('Horários de Funcionamento');
    fireEvent.click(horariosTab);
    
    // Deve mostrar as configurações de horários
    expect(screen.getByText('Dias de Funcionamento')).toBeInTheDocument();
    
    // Clicar na aba de configurações do chatbot
    const chatbotTab = screen.getByText('Configurações do Chatbot');
    fireEvent.click(chatbotTab);
    
    // Deve mostrar as configurações do chatbot
    expect(screen.getByText('Mensagem de Boas-vindas')).toBeInTheDocument();
    
    // Clicar na aba de notificações
    const notificacoesTab = screen.getByText('Notificações');
    fireEvent.click(notificacoesTab);
    
    // Deve mostrar as configurações de notificações
    expect(screen.getByText('Notificações para Pacientes')).toBeInTheDocument();
  });

  it('permite editar informações da clínica', () => {
    render(<ConfiguracoesPage />);
    
    // Encontrar o campo de nome da clínica
    const nomeClinicaInput = screen.getByLabelText('Nome da Clínica');
    
    // Alterar o valor
    fireEvent.change(nomeClinicaInput, { target: { value: 'Nova Clínica Tanaka' } });
    
    // Verificar se o valor foi alterado
    expect(nomeClinicaInput).toHaveValue('Nova Clínica Tanaka');
  });

  it('permite salvar as configurações', async () => {
    render(<ConfiguracoesPage />);
    
    // Encontrar o botão de salvar
    const salvarButton = screen.getByText('Salvar Configurações');
    
    // Clicar no botão
    fireEvent.click(salvarButton);
    
    // Verificar se o botão fica desabilitado durante o salvamento
    expect(salvarButton).toBeDisabled();
    
    // Verificar se o alerta é exibido após o salvamento
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Configurações salvas com sucesso!');
    });
  });

  it('permite configurar dias de funcionamento', () => {
    render(<ConfiguracoesPage />);
    
    // Clicar na aba de horários de funcionamento
    const horariosTab = screen.getByText('Horários de Funcionamento');
    fireEvent.click(horariosTab);
    
    // Encontrar o checkbox de domingo
    const domingoCheckbox = screen.getByLabelText('Dom');
    
    // Por padrão, domingo deve estar desmarcado
    expect(domingoCheckbox).not.toBeChecked();
    
    // Marcar o checkbox
    fireEvent.click(domingoCheckbox);
    
    // Verificar se o checkbox foi marcado
    expect(domingoCheckbox).toBeChecked();
  });
});
