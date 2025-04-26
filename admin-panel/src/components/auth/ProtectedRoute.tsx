"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

// Componente de proteção de rota que verifica se o usuário está autenticado
export default function ProtectedRoute({ children }) {
  const router = useRouter();

  useEffect(() => {
    // Verificar se o usuário está autenticado
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token");
      const user = localStorage.getItem("user");
      
      if (!token || !user) {
        // Redirecionar para a página de login se não estiver autenticado
        router.push("/login");
      }
    };
    
    checkAuth();
  }, [router]);

  return <>{children}</>;
}
