"use client";

import { useState } from "react";
import Link from "next/link";

export default function Relatorios() {
  const [periodoRelatorio, setPeriodoRelatorio] = useState("semana");
  const [dataInicio, setDataInicio] = useState("2025-04-20");
  const [dataFim, setDataFim] = useState("2025-04-26");
  const [tipoRelatorio, setTipoRelatorio] = useState("agendamentos");
  const [carregando, setCarregando] = useState(false);
  
  // Dados de exemplo para relatórios
  const dadosAgendamentos = [
    { data: "2025-04-20", total: 8, confirmados: 6, cancelados: 2 },
    { data: "2025-04-21", total: 12, confirmados: 10, cancelados: 2 },
    { data: "2025-04-22", total: 10, confirmados: 9, cancelados: 1 },
    { data: "2025-04-23", total: 14, confirmados: 12, cancelados: 2 },
    { data: "2025-04-24", total: 9, confirmados: 8, cancelados: 1 },
    { data: "2025-04-25", total: 11, confirmados: 10, cancelados: 1 },
    { data: "2025-04-26", total: 6, confirmados: 5, cancelados: 1 },
  ];
  
  const dadosIdiomas = {
    japones: 35,
    portugues: 18,
    ingles: 12,
    outros: 5
  };
  
  const horariosPopulares = [
    { horario: "09:00", quantidade: 8 },
    { horario: "09:30", quantidade: 6 },
    { horario: "10:00", quantidade: 12 },
    { horario: "10:30", quantidade: 9 },
    { horario: "11:00", quantidade: 7 },
    { horario: "14:00", quantidade: 10 },
    { horario: "14:30", quantidade: 8 },
    { horario: "15:00", quantidade: 11 },
    { horario: "15:30", quantidade: 7 },
    { horario: "16:00", quantidade: 5 },
    { horario: "16:30", quantidade: 4 },
    { horario: "17:00", quantidade: 3 },
  ];
  
  // Função para gerar relatório
  const gerarRelatorio = () => {
    setCarregando(true);
    
    // Simulação de carregamento
    setTimeout(() => {
      setCarregando(false);
    }, 1500);
  };
  
  // Função para exportar relatório
  const exportarRelatorio = (formato) => {
    alert(`Relatório exportado em formato ${formato}`);
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Relatórios e Estatísticas</h1>
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Voltar ao Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Gerar Relatório</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                  <label htmlFor="tipoRelatorio" className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Relatório
                  </label>
                  <select
                    id="tipoRelatorio"
                    value={tipoRelatorio}
                    onChange={(e) => setTipoRelatorio(e.target.value)}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="agendamentos">Agendamentos</option>
                    <option value="pacientes">Pacientes</option>
                    <option value="idiomas">Distribuição de Idiomas</option>
                    <option value="horarios">Horários Populares</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="periodoRelatorio" className="block text-sm font-medium text-gray-700 mb-1">
                    Período
                  </label>
                  <select
                    id="periodoRelatorio"
                    value={periodoRelatorio}
                    onChange={(e) => setPeriodoRelatorio(e.target.value)}
                    className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  >
                    <option value="dia">Dia</option>
                    <option value="semana">Semana</option>
                    <option value="mes">Mês</option>
                    <option value="personalizado">Personalizado</option>
                  </select>
                </div>
                
                <div className="md:col-span-1">
                  <button
                    onClick={gerarRelatorio}
                    disabled={carregando}
                    className={`w-full inline-flex justify-center items-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                      carregando ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"
                    } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                  >
                    {carregando ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Gerando...
                      </>
                    ) : (
                      "Gerar Relatório"
                    )}
                  </button>
                </div>
              </div>
              
              {periodoRelatorio === "personalizado" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <label htmlFor="dataInicio" className="block text-sm font-medium text-gray-700 mb-1">
                      Data de Início
                    </label>
                    <input
                      type="date"
                      id="dataInicio"
                      value={dataInicio}
                      onChange={(e) => setDataInicio(e.target.value)}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="dataFim" className="block text-sm font-medium text-gray-700 mb-1">
                      Data de Fim
                    </label>
                    <input
                      type="date"
                      id="dataFim"
                      value={dataFim}
                      onChange={(e) => setDataFim(e.target.value)}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              )}
              
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => exportarRelatorio("pdf")}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Exportar PDF
                </button>
                <button
                  onClick={() => exportarRelatorio("excel")}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Exportar Excel
                </button>
              </div>
            </div>
            
            {/* Resultados do Relatório */}
            <div className="mt-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Resultados</h2>
              
              {tipoRelatorio === "agendamentos" && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Relatório de Agendamentos - Semana de 20/04/2025 a 26/04/2025
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Total de agendamentos no período: 70
                    </p>
                  </div>
                  
                  <div className="px-6 py-5">
                    <div className="flex flex-col">
                      <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                          <div className="overflow-hidden border-b border-gray-200">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-50">
                                <tr>
                                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Data
                                  </th>
                                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Total
                                  </th>
                                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Confirmados
                                  </th>
                                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Cancelados
                                  </th>
                                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Taxa de Confirmação
                                  </th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {dadosAgendamentos.map((dia) => (
                                  <tr key={dia.data}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                      {dia.data}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      {dia.total}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      {dia.confirmados}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      {dia.cancelados}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      {Math.round((dia.confirmados / dia.total) * 100)}%
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-6">
                      <h4 className="text-base font-medium text-gray-900 mb-3">Resumo</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <p className="text-sm font-medium text-blue-800">Total de Agendamentos</p>
                          <p className="mt-1 text-3xl font-semibold text-blue-900">70</p>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <p className="text-sm font-medium text-green-800">Taxa de Confirmação</p>
                          <p className="mt-1 text-3xl font-semibold text-green-900">85.7%</p>
                        </div>
                        <div className="bg-yellow-50 p-4 rounded-lg">
                          <p className="text-sm font-medium text-yellow-800">Média Diária</p>
                          <p className="mt-1 text-3xl font-semibold text-yellow-900">10</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {tipoRelatorio === "idiomas" && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Distribuição de Idiomas - Semana de 20/04/2025 a 26/04/2025
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Total de pacientes no período: 70
                    </p>
                  </div>
                  
                  <div className="px-6 py-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-base font-medium text-gray-900 mb-3">Distribuição por Idioma</h4>
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Idioma
                              </th>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Quantidade
                              </th>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Porcentagem
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Japonês 🇯🇵
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {dadosIdiomas.japones}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round((dadosIdiomas.japones / 70) * 100)}%
                              </td>
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Português 🇧🇷
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {dadosIdiomas.portugues}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round((dadosIdiomas.portugues / 70) * 100)}%
                              </td>
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Inglês 🇺🇸
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {dadosIdiomas.ingles}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round((dadosIdiomas.ingles / 70) * 100)}%
                              </td>
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Outros 🌍
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {dadosIdiomas.outros}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round((dadosIdiomas.outros / 70) * 100)}%
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      
                      <div>
                        <h4 className="text-base font-medium text-gray-900 mb-3">Gráfico de Distribuição</h4>
                        <div className="bg-gray-50 p-4 rounded-lg h-64 flex items-end justify-around">
                          <div className="flex flex-col items-center">
                            <div className="bg-blue-500 w-16" style={{ height: `${(dadosIdiomas.japones / 70) * 100 * 2}px` }}></div>
                            <p className="mt-2 text-sm text-gray-500">Japonês</p>
                          </div>
                          <div className="flex flex-col items-center">
                            <div className="bg-green-500 w-16" style={{ height: `${(dadosIdiomas.portugues / 70) * 100 * 2}px` }}></div>
                            <p className="mt-2 text-sm text-gray-500">Português</p>
                          </div>
                          <div className="flex flex-col items-center">
                            <div className="bg-yellow-500 w-16" style={{ height: `${(dadosIdiomas.ingles / 70) * 100 * 2}px` }}></div>
                            <p className="mt-2 text-sm text-gray-500">Inglês</p>
                          </div>
                          <div className="flex flex-col items-center">
                            <div className="bg-purple-500 w-16" style={{ height: `${(dadosIdiomas.outros / 70) * 100 * 2}px` }}></div>
                            <p className="mt-2 text-sm text-gray-500">Outros</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {tipoRelatorio === "horarios" && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Horários Mais Populares - Semana de 20/04/2025 a 26/04/2025
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Análise de preferência de horários
                    </p>
                  </div>
                  
                  <div className="px-6 py-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-base font-medium text-gray-900 mb-3">Top 5 Horários Mais Agendados</h4>
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Posição
                              </th>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Horário
                              </th>
                              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Quantidade
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {horariosPopulares
                              .sort((a, b) => b.quantidade - a.quantidade)
                              .slice(0, 5)
                              .map((horario, index) => (
                                <tr key={horario.horario}>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {index + 1}º
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {horario.horario}
                                  </td>
                                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {horario.quantidade}
                                  </td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                      
                      <div>
                        <h4 className="text-base font-medium text-gray-900 mb-3">Distribuição por Período</h4>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="mb-4">
                            <h5 className="text-sm font-medium text-gray-700 mb-2">Manhã (09:00 - 12:00)</h5>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: "65%" }}></div>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">42 agendamentos (65%)</p>
                          </div>
                          
                          <div>
                            <h5 className="text-sm font-medium text-gray-700 mb-2">Tarde (14:00 - 18:00)</h5>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: "35%" }}></div>
                            </div>
                            <p className="mt-1 text-xs text-gray-500">28 agendamentos (35%)</p>
                          </div>
                        </div>
                        
                        <div className="mt-6">
                          <h4 className="text-base font-medium text-gray-900 mb-3">Conclusões</h4>
                          <ul className="list-disc pl-5 text-sm text-gray-700 space-y-2">
                            <li>O horário das 10:00 é o mais popular entre os pacientes</li>
                            <li>Período da manhã tem maior demanda que o período da tarde</li>
                            <li>Horários próximos ao almoço (11:00) e final da tarde (após 16:00) são menos procurados</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
