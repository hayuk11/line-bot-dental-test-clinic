import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoggingSystem from '../src/components/monitoring/LoggingSystem';
import PerformanceMonitor from '../src/components/monitoring/PerformanceMonitor';

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

// Mock do console
const originalConsole = { ...console };
beforeEach(() => {
  console.log = vi.fn();
  console.error = vi.fn();
});
afterEach(() => {
  console.log = originalConsole.log;
  console.error = originalConsole.error;
});

describe('Componentes de Monitoramento', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
    
    // Limpar window.logger e window.performanceMonitor
    delete window.logger;
    delete window.performanceMonitor;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('LoggingSystem', () => {
    it('inicializa o sistema de logs corretamente', () => {
      // Renderizar o componente
      render(<LoggingSystem />);
      
      // Verificar se o logger global foi criado
      expect(window.logger).toBeDefined();
      expect(typeof window.logger.debug).toBe('function');
      expect(typeof window.logger.info).toBe('function');
      expect(typeof window.logger.warn).toBe('function');
      expect(typeof window.logger.error).toBe('function');
      expect(typeof window.logger.critical).toBe('function');
      
      // Verificar se o log inicial foi registrado
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[INFO] LoggingSystem: Logging system initialized')
      );
    });

    it('registra logs com diferentes níveis', () => {
      // Renderizar o componente
      render(<LoggingSystem />);
      
      // Usar o logger para registrar logs
      window.logger.debug('TestModule', 'Debug message');
      window.logger.info('TestModule', 'Info message');
      window.logger.warn('TestModule', 'Warning message');
      window.logger.error('TestModule', 'Error message');
      window.logger.critical('TestModule', 'Critical message');
      
      // Verificar se os logs foram registrados no console
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[INFO] TestModule: Info message')
      );
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[WARN] TestModule: Warning message')
      );
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('[ERROR] TestModule: Error message')
      );
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining('CRITICAL ERROR NOTIFICATION:')
      );
      
      // Verificar se os logs foram armazenados no localStorage
      const storedLogs = JSON.parse(localStorageMock.setItem.mock.calls.find(
        call => call[0] === 'system_logs'
      )[1]);
      
      expect(storedLogs.length).toBeGreaterThan(0);
      expect(storedLogs.some(log => log.level === 'INFO' && log.message === 'Info message')).toBe(true);
    });
  });

  describe('PerformanceMonitor', () => {
    it('inicializa o monitor de desempenho corretamente', () => {
      // Renderizar o componente
      render(<PerformanceMonitor />);
      
      // Verificar se o performanceMonitor global foi criado
      expect(window.performanceMonitor).toBeDefined();
      expect(typeof window.performanceMonitor.getMetrics).toBe('function');
      expect(typeof window.performanceMonitor.clearMetrics).toBe('function');
      
      // Verificar se as métricas iniciais foram armazenadas no localStorage
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'performance_metrics',
        expect.stringContaining('pageLoads')
      );
    });

    it('rastreia carregamentos de página', () => {
      // Renderizar o componente
      render(<PerformanceMonitor />);
      
      // Obter as métricas
      const metrics = window.performanceMonitor.getMetrics();
      
      // Verificar se o carregamento de página foi registrado
      expect(metrics.pageLoads).toBe(1);
    });

    it('permite limpar métricas', () => {
      // Renderizar o componente
      render(<PerformanceMonitor />);
      
      // Limpar as métricas
      window.performanceMonitor.clearMetrics();
      
      // Verificar se as métricas foram limpas
      const metrics = window.performanceMonitor.getMetrics();
      expect(metrics.pageLoads).toBe(0);
      expect(metrics.apiCalls).toBe(0);
      expect(metrics.errors).toBe(0);
      expect(metrics.responseTime.length).toBe(0);
      
      // Verificar se o localStorage foi limpo
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('performance_metrics');
    });
  });
});
