"use client";

import { useState } from "react";
import Link from "next/link";

export default function Pacientes() {
  const [filtro, setFiltro] = useState("");
  const [ordenarPor, setOrdenarPor] = useState("nome");
  
  // Dados de exemplo para pacientes
  const pacientes = [
    { id: 1, nome: "Akira Tanaka", telefone: "+81 90-1234-5678", idioma: "Japonês", ultimaConsulta: "2025-04-10", proximaConsulta: "2025-04-26", status: "Ativo" },
    { id: 2, nome: "Maria Silva", telefone: "+81 80-8765-4321", idioma: "Português", ultimaConsulta: "2025-03-15", proximaConsulta: "2025-04-26", status: "Ativo" },
    { id: 3, nome: "John Doe", telefone: "+81 70-2468-1357", idioma: "Inglês", ultimaConsulta: "2025-04-05", proximaConsulta: "2025-04-26", status: "Ativo" },
    { id: 4, nome: "Yuki Sato", telefone: "+81 90-9876-5432", idioma: "Japonês", ultimaConsulta: "2025-02-20", proximaConsulta: "2025-04-27", status: "Ativo" },
    { id: 5, nome: "Carlos Oliveira", telefone: "+81 80-1357-2468", idioma: "Português", ultimaConsulta: "2025-01-30", proximaConsulta: "2025-04-27", status: "Inativo" },
    { id: 6, nome: "Hiroshi Yamamoto", telefone: "+81 70-5555-1234", idioma: "Japonês", ultimaConsulta: "2024-12-15", proximaConsulta: "2025-04-27", status: "Ativo" },
    { id: 7, nome: "Ana Pereira", telefone: "+81 90-4321-8765", idioma: "Português", ultimaConsulta: "2025-03-25", proximaConsulta: "2025-04-28", status: "Ativo" },
    { id: 8, nome: "Takashi Suzuki", telefone: "+81 80-9999-8888", idioma: "Japonês", ultimaConsulta: "2025-04-15", proximaConsulta: "2025-04-28", status: "Ativo" },
  ];

  // Filtrar pacientes
  const pacientesFiltrados = pacientes.filter(p => 
    p.nome.toLowerCase().includes(filtro.toLowerCase()) ||
    p.telefone.includes(filtro) ||
    p.idioma.toLowerCase().includes(filtro.toLowerCase())
  );

  // Ordenar pacientes
  const pacientesOrdenados = [...pacientesFiltrados].sort((a, b) => {
    if (ordenarPor === "nome") {
      return a.nome.localeCompare(b.nome);
    } else if (ordenarPor === "ultimaConsulta") {
      return new Date(b.ultimaConsulta).getTime() - new Date(a.ultimaConsulta).getTime();
    } else if (ordenarPor === "proximaConsulta") {
      return new Date(a.proximaConsulta).getTime() - new Date(b.proximaConsulta).getTime();
    }
    return 0;
  });

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Pacientes</h1>
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Voltar ao Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {/* Controles de busca e ordenação */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 space-y-4 md:space-y-0">
              <div className="w-full md:w-1/3">
                <label htmlFor="filtro" className="sr-only">Buscar pacientes</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    id="filtro"
                    type="text"
                    placeholder="Buscar por nome, telefone ou idioma"
                    value={filtro}
                    onChange={(e) => setFiltro(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <label htmlFor="ordenarPor" className="text-sm font-medium text-gray-700">
                  Ordenar por:
                </label>
                <select
                  id="ordenarPor"
                  value={ordenarPor}
                  onChange={(e) => setOrdenarPor(e.target.value)}
                  className="rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="nome">Nome</option>
                  <option value="ultimaConsulta">Última Consulta</option>
                  <option value="proximaConsulta">Próxima Consulta</option>
                </select>
              </div>

              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Adicionar Paciente
              </button>
            </div>

            {/* Lista de pacientes */}
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nome
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Telefone
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Idioma
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Última Consulta
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Próxima Consulta
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pacientesOrdenados.map((paciente) => (
                    <tr key={paciente.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-blue-600">{paciente.nome}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{paciente.telefone}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{paciente.idioma}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{paciente.ultimaConsulta}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{paciente.proximaConsulta}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          paciente.status === "Ativo" 
                            ? "bg-green-100 text-green-800" 
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          {paciente.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button className="text-blue-600 hover:text-blue-900">Detalhes</button>
                          <button className="text-green-600 hover:text-green-900">Mensagem</button>
                          <button className="text-red-600 hover:text-red-900">Desativar</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Paginação */}
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4 rounded-md shadow">
              <div className="flex-1 flex justify-between sm:hidden">
                <button className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Anterior
                </button>
                <button className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Próximo
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Mostrando <span className="font-medium">1</span> a <span className="font-medium">{pacientesOrdenados.length}</span> de <span className="font-medium">{pacientesOrdenados.length}</span> resultados
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                      <span className="sr-only">Anterior</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                    <button className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-blue-50 text-sm font-medium text-blue-600 hover:bg-blue-100">
                      1
                    </button>
                    <button className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                      <span className="sr-only">Próximo</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
