"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Middleware para registrar atividades do usuário
export default function ActivityLogger() {
  const router = useRouter();

  useEffect(() => {
    // Função para registrar atividade
    const logActivity = (path, action) => {
      const user = localStorage.getItem("user");
      const userData = user ? JSON.parse(user) : { id: "anonymous" };
      
      const activityLog = {
        userId: userData.id,
        userName: userData.name || "Anônimo",
        timestamp: new Date().toISOString(),
        path: path,
        action: action,
        userAgent: navigator.userAgent
      };
      
      // Em uma implementação real, enviaríamos para o backend
      console.log("Activity logged:", activityLog);
      
      // Armazenar localmente para demonstração
      const logs = JSON.parse(localStorage.getItem("activity_logs") || "[]");
      logs.push(activityLog);
      localStorage.setItem("activity_logs", JSON.stringify(logs));
    };
    
    // Registrar navegação inicial
    logActivity(window.location.pathname, "page_view");
    
    // Adicionar listener para mudanças de rota
    const handleRouteChange = (url) => {
      logActivity(url, "page_view");
    };
    
    // Cleanup function
    return () => {
      // Remover listener em caso de desmontagem do componente
    };
  }, [router]);

  return null;
}
