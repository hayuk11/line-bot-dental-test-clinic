"use client";

import { useState, useEffect } from "react";

// Sistema de logs para registrar eventos do sistema
export default function LoggingSystem() {
  // Níveis de log
  const LOG_LEVELS = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
    CRITICAL: 4
  };

  // Configuração atual do nível de log
  const [currentLogLevel, setCurrentLogLevel] = useState(LOG_LEVELS.INFO);
  
  // Função para registrar logs
  const logEvent = (level, module, message, data = {}) => {
    // Verificar se o nível do log é igual ou maior que o nível configurado
    if (level < currentLogLevel) return;
    
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: Object.keys(LOG_LEVELS).find(key => LOG_LEVELS[key] === level) || "UNKNOWN",
      module,
      message,
      data,
    };
    
    // Em uma implementação real, enviaríamos para o backend ou serviço de logs
    console.log(`[${logEntry.level}] ${logEntry.module}: ${logEntry.message}`, data);
    
    // Armazenar localmente para demonstração
    const logs = JSON.parse(localStorage.getItem("system_logs") || "[]");
    logs.push(logEntry);
    
    // Limitar o número de logs armazenados localmente
    if (logs.length > 1000) {
      logs.shift(); // Remover o log mais antigo
    }
    
    localStorage.setItem("system_logs", JSON.stringify(logs));
    
    // Para erros críticos, podemos enviar notificações
    if (level === LOG_LEVELS.CRITICAL) {
      // Simulação de envio de notificação
      console.error("CRITICAL ERROR NOTIFICATION:", logEntry);
    }
  };
  
  // Métodos de log para diferentes níveis
  const debug = (module, message, data) => logEvent(LOG_LEVELS.DEBUG, module, message, data);
  const info = (module, message, data) => logEvent(LOG_LEVELS.INFO, module, message, data);
  const warn = (module, message, data) => logEvent(LOG_LEVELS.WARN, module, message, data);
  const error = (module, message, data) => logEvent(LOG_LEVELS.ERROR, module, message, data);
  const critical = (module, message, data) => logEvent(LOG_LEVELS.CRITICAL, module, message, data);
  
  // Expor métodos de log globalmente para uso em toda a aplicação
  useEffect(() => {
    window.logger = {
      debug,
      info,
      warn,
      error,
      critical,
      setLogLevel: setCurrentLogLevel,
      LOG_LEVELS
    };
    
    // Log inicial
    info("LoggingSystem", "Logging system initialized", { level: currentLogLevel });
    
    return () => {
      // Cleanup
      delete window.logger;
    };
  }, [currentLogLevel]);
  
  return null;
}
