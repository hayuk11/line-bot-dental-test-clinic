import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RelatoriosPage from '../src/app/relatorios/page';

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

describe('RelatoriosPage', () => {
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
    render(<RelatoriosPage />);
    
    expect(screen.getByText('Relatórios e Estatísticas')).toBeInTheDocument();
    expect(screen.getByText('Gerar Relatório')).toBeInTheDocument();
    expect(screen.getByText('Tipo de Relatório')).toBeInTheDocument();
    expect(screen.getByText('Período')).toBeInTheDocument();
  });

  it('permite selecionar diferentes tipos de relatório', () => {
    render(<RelatoriosPage />);
    
    // Selecionar tipo de relatório "Idiomas"
    const tipoRelatorioSelect = screen.getByLabelText('Tipo de Relatório');
    fireEvent.change(tipoRelatorioSelect, { target: { value: 'idiomas' } });
    
    // Gerar o relatório
    const gerarButton = screen.getByText('Gerar Relatório');
    fireEvent.click(gerarButton);
    
    // Verificar se o botão fica desabilitado durante o carregamento
    expect(gerarButton).toBeDisabled();
    
    // Após o carregamento, deve mostrar o relatório de idiomas
    return waitFor(() => {
      expect(screen.getByText('Distribuição de Idiomas')).toBeInTheDocument();
      expect(screen.getByText('Japonês 🇯🇵')).toBeInTheDocument();
      expect(screen.getByText('Português 🇧🇷')).toBeInTheDocument();
    });
  });

  it('mostra campos de data personalizados quando período personalizado é selecionado', () => {
    render(<RelatoriosPage />);
    
    // Inicialmente, os campos de data não devem estar visíveis
    expect(screen.queryByLabelText('Data de Início')).not.toBeInTheDocument();
    
    // Selecionar período personalizado
    const periodoSelect = screen.getByLabelText('Período');
    fireEvent.change(periodoSelect, { target: { value: 'personalizado' } });
    
    // Os campos de data devem estar visíveis
    expect(screen.getByLabelText('Data de Início')).toBeInTheDocument();
    expect(screen.getByLabelText('Data de Fim')).toBeInTheDocument();
  });

  it('permite exportar relatórios em diferentes formatos', () => {
    render(<RelatoriosPage />);
    
    // Gerar o relatório
    const gerarButton = screen.getByText('Gerar Relatório');
    fireEvent.click(gerarButton);
    
    // Após o carregamento, exportar em PDF
    return waitFor(() => {
      const exportarPDFButton = screen.getByText('Exportar PDF');
      fireEvent.click(exportarPDFButton);
      
      // Verificar se o alerta foi exibido
      expect(window.alert).toHaveBeenCalledWith('Relatório exportado em formato pdf');
      
      // Exportar em Excel
      const exportarExcelButton = screen.getByText('Exportar Excel');
      fireEvent.click(exportarExcelButton);
      
      // Verificar se o alerta foi exibido
      expect(window.alert).toHaveBeenCalledWith('Relatório exportado em formato excel');
    });
  });

  it('exibe resumo de agendamentos quando tipo de relatório é agendamentos', async () => {
    render(<RelatoriosPage />);
    
    // Selecionar tipo de relatório "Agendamentos" (já é o padrão)
    
    // Gerar o relatório
    const gerarButton = screen.getByText('Gerar Relatório');
    fireEvent.click(gerarButton);
    
    // Após o carregamento, deve mostrar o resumo de agendamentos
    await waitFor(() => {
      expect(screen.getByText('Relatório de Agendamentos')).toBeInTheDocument();
    });
    
    // Verificar se o resumo está correto
    expect(screen.getByText('Total de Agendamentos')).toBeInTheDocument();
    expect(screen.getByText('70')).toBeInTheDocument();
    expect(screen.getByText('Taxa de Confirmação')).toBeInTheDocument();
    expect(screen.getByText('85.7%')).toBeInTheDocument();
  });
});
