"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Sistema de monitoramento para acompanhar o desempenho e saúde do sistema
export default function PerformanceMonitor() {
  const router = useRouter();
  const [metrics, setMetrics] = useState({
    pageLoads: 0,
    apiCalls: 0,
    errors: 0,
    responseTime: []
  });
  
  useEffect(() => {
    // Inicializar o monitoramento
    const initMonitoring = () => {
      // Carregar métricas existentes do localStorage
      const savedMetrics = localStorage.getItem("performance_metrics");
      if (savedMetrics) {
        setMetrics(JSON.parse(savedMetrics));
      }
      
      // Registrar carregamento de página
      trackPageLoad();
      
      // Monitorar erros não tratados
      window.addEventListener("error", handleError);
      
      // Monitorar chamadas de API
      const originalFetch = window.fetch;
      window.fetch = async function(input, init) {
        const startTime = performance.now();
        try {
          const response = await originalFetch(input, init);
          const endTime = performance.now();
          trackApiCall(input.toString(), endTime - startTime, response.status);
          return response;
        } catch (error) {
          trackError("API_CALL", error.message, { url: input.toString() });
          throw error;
        }
      };
      
      // Log de inicialização
      if (window.logger) {
        window.logger.info("PerformanceMonitor", "Performance monitoring initialized");
      }
    };
    
    // Função para registrar carregamento de página
    const trackPageLoad = () => {
      setMetrics(prev => {
        const updated = {
          ...prev,
          pageLoads: prev.pageLoads + 1
        };
        localStorage.setItem("performance_metrics", JSON.stringify(updated));
        return updated;
      });
    };
    
    // Função para registrar chamadas de API
    const trackApiCall = (url, duration, status) => {
      setMetrics(prev => {
        const updated = {
          ...prev,
          apiCalls: prev.apiCalls + 1,
          responseTime: [...prev.responseTime, { url, duration, timestamp: new Date().toISOString() }]
        };
        
        // Limitar o número de registros de tempo de resposta
        if (updated.responseTime.length > 100) {
          updated.responseTime.shift();
        }
        
        localStorage.setItem("performance_metrics", JSON.stringify(updated));
        return updated;
      });
      
      // Registrar no sistema de logs
      if (window.logger) {
        window.logger.debug("PerformanceMonitor", `API call to ${url}`, { 
          duration, 
          status,
          timestamp: new Date().toISOString()
        });
      }
    };
    
    // Função para registrar erros
    const trackError = (type, message, details = {}) => {
      setMetrics(prev => {
        const updated = {
          ...prev,
          errors: prev.errors + 1
        };
        localStorage.setItem("performance_metrics", JSON.stringify(updated));
        return updated;
      });
      
      // Registrar no sistema de logs
      if (window.logger) {
        window.logger.error("PerformanceMonitor", message, { 
          type, 
          details,
          timestamp: new Date().toISOString()
        });
      }
    };
    
    // Handler para erros não tratados
    const handleError = (event) => {
      trackError("UNHANDLED", event.message, { 
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
    };
    
    initMonitoring();
    
    // Cleanup
    return () => {
      window.removeEventListener("error", handleError);
      window.fetch = originalFetch;
    };
  }, [router]);
  
  // Expor métodos de monitoramento globalmente
  useEffect(() => {
    window.performanceMonitor = {
      getMetrics: () => metrics,
      clearMetrics: () => {
        setMetrics({
          pageLoads: 0,
          apiCalls: 0,
          errors: 0,
          responseTime: []
        });
        localStorage.removeItem("performance_metrics");
      }
    };
    
    return () => {
      delete window.performanceMonitor;
    };
  }, [metrics]);
  
  return null;
}
