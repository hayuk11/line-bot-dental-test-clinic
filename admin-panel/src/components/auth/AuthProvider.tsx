"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Componente de autenticação que será usado em todas as páginas protegidas
export default function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Verificar se o usuário está autenticado
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token");
      const user = localStorage.getItem("user");
      
      if (token && user) {
        // Em uma implementação real, verificaríamos a validade do token com o backend
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        router.push("/login");
      }
      
      setIsLoading(false);
    };
    
    checkAuth();
  }, [router]);

  // Função para realizar login
  const login = (email, password) => {
    // Em uma implementação real, enviaríamos uma requisição para o backend
    return new Promise((resolve, reject) => {
      // Simulação de autenticação
      if (email === "admin@clinica.com" && password === "admin123") {
        const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ";
        const user = {
          id: 1,
          name: "Admin",
          email: "admin@clinica.com",
          role: "admin"
        };
        
        localStorage.setItem("auth_token", token);
        localStorage.setItem("user", JSON.stringify(user));
        
        setIsAuthenticated(true);
        resolve(user);
      } else {
        reject(new Error("Credenciais inválidas"));
      }
    });
  };

  // Função para realizar logout
  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    router.push("/login");
  };

  // Função para obter o usuário atual
  const getCurrentUser = () => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  };

  // Função para verificar se o usuário tem uma determinada permissão
  const hasPermission = (permission) => {
    const user = getCurrentUser();
    if (!user) return false;
    
    // Em uma implementação real, verificaríamos as permissões do usuário
    // Por enquanto, vamos assumir que admin tem todas as permissões
    return user.role === "admin";
  };

  // Contexto de autenticação que será disponibilizado para todos os componentes
  const authContext = {
    isAuthenticated,
    login,
    logout,
    getCurrentUser,
    hasPermission
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="auth-provider">
      {children}
    </div>
  );
}
