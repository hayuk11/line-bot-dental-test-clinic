"use client";

import { useState } from "react";
import Link from "next/link";

export default function Agendamentos() {
  const [view, setView] = useState<"lista" | "calendario">("lista");
  const [filtroStatus, setFiltroStatus] = useState<string>("todos");
  
  // Dados de exemplo para agendamentos
  const agendamentos = [
    { id: 1, nome: "Akira Tanaka", data: "2025-04-26", hora: "14:30", motivo: "Consulta de rotina", status: "Confirmado", telefone: "+81 90-1234-5678", idioma: "Japonês" },
    { id: 2, nome: "Maria Silva", data: "2025-04-26", hora: "15:00", motivo: "Dor de dente", status: "Aguardando", telefone: "+81 80-8765-4321", idioma: "Português" },
    { id: 3, nome: "John Doe", data: "2025-04-26", hora: "16:30", motivo: "Limpeza", status: "Confirmado", telefone: "+81 70-2468-1357", idioma: "Inglês" },
    { id: 4, nome: "Yuki Sato", data: "2025-04-27", hora: "09:00", motivo: "Extração", status: "Confirmado", telefone: "+81 90-9876-5432", idioma: "Japonês" },
    { id: 5, nome: "Carlos Oliveira", data: "2025-04-27", hora: "10:30", motivo: "Consulta de rotina", status: "Aguardando", telefone: "+81 80-1357-2468", idioma: "Português" },
    { id: 6, nome: "Hiroshi Yamamoto", data: "2025-04-27", hora: "11:00", motivo: "Dor de dente", status: "Recusado", telefone: "+81 70-5555-1234", idioma: "Japonês" },
    { id: 7, nome: "Ana Pereira", data: "2025-04-28", hora: "14:00", motivo: "Consulta de rotina", status: "Confirmado", telefone: "+81 90-4321-8765", idioma: "Português" },
    { id: 8, nome: "Takashi Suzuki", data: "2025-04-28", hora: "15:30", motivo: "Limpeza", status: "Aguardando", telefone: "+81 80-9999-8888", idioma: "Japonês" },
  ];

  // Filtrar agendamentos por status
  const agendamentosFiltrados = filtroStatus === "todos" 
    ? agendamentos 
    : agendamentos.filter(a => a.status === filtroStatus);

  // Função para alterar o status de um agendamento
  const alterarStatus = (id: number, novoStatus: string) => {
    // Em uma implementação real, isso enviaria uma requisição para o backend
    console.log(`Alterando status do agendamento ${id} para ${novoStatus}`);
    // Aqui atualizaríamos o estado local após a confirmação do backend
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Agendamentos</h1>
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Voltar ao Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {/* Controles de visualização e filtros */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 space-y-4 md:space-y-0">
              <div className="flex space-x-4">
                <button
                  onClick={() => setView("lista")}
                  className={`px-4 py-2 rounded ${
                    view === "lista" 
                      ? "bg-blue-600 text-white" 
                      : "bg-white text-gray-700 border border-gray-300"
                  }`}
                >
                  Visualização em Lista
                </button>
                <button
                  onClick={() => setView("calendario")}
                  className={`px-4 py-2 rounded ${
                    view === "calendario" 
                      ? "bg-blue-600 text-white" 
                      : "bg-white text-gray-700 border border-gray-300"
                  }`}
                >
                  Visualização em Calendário
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <label htmlFor="filtroStatus" className="text-sm font-medium text-gray-700">
                  Filtrar por status:
                </label>
                <select
                  id="filtroStatus"
                  value={filtroStatus}
                  onChange={(e) => setFiltroStatus(e.target.value)}
                  className="rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="todos">Todos</option>
                  <option value="Aguardando">Aguardando</option>
                  <option value="Confirmado">Confirmado</option>
                  <option value="Recusado">Recusado</option>
                </select>
              </div>
            </div>

            {/* Visualização em Lista */}
            {view === "lista" && (
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {agendamentosFiltrados.map((agendamento) => (
                    <li key={agendamento.id}>
                      <div className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-blue-600 truncate">{agendamento.nome}</p>
                          <div className="ml-2 flex-shrink-0 flex">
                            <select
                              value={agendamento.status}
                              onChange={(e) => alterarStatus(agendamento.id, e.target.value)}
                              className={`text-xs font-semibold rounded-full px-2 py-1 ${
                                agendamento.status === "Confirmado" 
                                  ? "bg-green-100 text-green-800" 
                                  : agendamento.status === "Recusado"
                                  ? "bg-red-100 text-red-800"
                                  : "bg-yellow-100 text-yellow-800"
                              }`}
                            >
                              <option value="Aguardando">Aguardando</option>
                              <option value="Confirmado">Confirmado</option>
                              <option value="Recusado">Recusado</option>
                            </select>
                          </div>
                        </div>
                        <div className="mt-2 sm:flex sm:justify-between">
                          <div className="sm:flex">
                            <p className="flex items-center text-sm text-gray-500">
                              <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                              </svg>
                              {agendamento.motivo}
                            </p>
                            <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                              <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                              </svg>
                              {agendamento.telefone}
                            </p>
                            <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                              <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                              </svg>
                              {agendamento.idioma}
                            </p>
                          </div>
                          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                            <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <p>
                              {agendamento.data} às {agendamento.hora}
                            </p>
                          </div>
                        </div>
                        <div className="mt-2 flex justify-end space-x-2">
                          <button className="text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 px-2 py-1 rounded">
                            Detalhes
                          </button>
                          <button className="text-xs bg-green-50 text-green-700 hover:bg-green-100 px-2 py-1 rounded">
                            Enviar Mensagem
                          </button>
                          <button className="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-2 py-1 rounded">
                            Cancelar
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Visualização em Calendário */}
            {view === "calendario" && (
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-center mb-4">
                  <h2 className="text-xl font-semibold">Abril 2025</h2>
                </div>
                <div className="grid grid-cols-7 gap-px bg-gray-200 border border-gray-200 rounded">
                  {/* Cabeçalho dos dias da semana */}
                  {["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"].map((dia) => (
                    <div key={dia} className="bg-gray-100 p-2 text-center text-sm font-medium text-gray-500">
                      {dia}
                    </div>
                  ))}
                  
                  {/* Dias do mês (simplificado para demonstração) */}
                  {Array.from({ length: 30 }, (_, i) => i + 1).map((dia) => {
                    // Verificar se há agendamentos neste dia
                    const agendamentosDoDia = agendamentos.filter(a => {
                      const dataDia = a.data.split("-")[2];
                      return parseInt(dataDia) === dia;
                    });
                    
                    const temAgendamento = agendamentosDoDia.length > 0;
                    
                    return (
                      <div 
                        key={dia} 
                        className={`bg-white p-2 min-h-[80px] ${temAgendamento ? 'cursor-pointer hover:bg-blue-50' : ''}`}
                      >
                        <div className="text-right text-sm text-gray-500">{dia}</div>
                        {temAgendamento && (
                          <div className="mt-1">
                            {agendamentosDoDia.slice(0, 2).map((a) => (
                              <div 
                                key={a.id} 
                                className={`text-xs p-1 mb-1 rounded truncate ${
                                  a.status === "Confirmado" 
                                    ? "bg-green-100 text-green-800" 
                                    : a.status === "Recusado"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-yellow-100 text-yellow-800"
                                }`}
                              >
                                {a.hora} - {a.nome}
                              </div>
                            ))}
                            {agendamentosDoDia.length > 2 && (
                              <div className="text-xs text-blue-600">
                                +{agendamentosDoDia.length - 2} mais
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
