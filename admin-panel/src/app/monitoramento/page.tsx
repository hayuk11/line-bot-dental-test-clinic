"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function MonitoringDashboard() {
  const [activeTab, setActiveTab] = useState("logs");
  const [logs, setLogs] = useState([]);
  const [activities, setActivities] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [filterLevel, setFilterLevel] = useState("all");
  const [filterModule, setFilterModule] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  
  useEffect(() => {
    // Carregar logs do sistema
    const systemLogs = JSON.parse(localStorage.getItem("system_logs") || "[]");
    setLogs(systemLogs);
    
    // Carregar logs de atividade
    const activityLogs = JSON.parse(localStorage.getItem("activity_logs") || "[]");
    setActivities(activityLogs);
    
    // Carregar métricas de desempenho
    const performanceMetrics = JSON.parse(localStorage.getItem("performance_metrics") || "null");
    setMetrics(performanceMetrics);
    
    // Atualizar dados a cada 5 segundos
    const interval = setInterval(() => {
      const updatedSystemLogs = JSON.parse(localStorage.getItem("system_logs") || "[]");
      setLogs(updatedSystemLogs);
      
      const updatedActivityLogs = JSON.parse(localStorage.getItem("activity_logs") || "[]");
      setActivities(updatedActivityLogs);
      
      const updatedPerformanceMetrics = JSON.parse(localStorage.getItem("performance_metrics") || "null");
      setMetrics(updatedPerformanceMetrics);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Filtrar logs com base nos critérios selecionados
  const filteredLogs = logs.filter(log => {
    if (filterLevel !== "all" && log.level !== filterLevel) return false;
    if (filterModule !== "all" && log.module !== filterModule) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });
  
  // Obter módulos únicos para o filtro
  const uniqueModules = [...new Set(logs.map(log => log.module))];
  
  // Obter níveis de log únicos para o filtro
  const uniqueLevels = [...new Set(logs.map(log => log.level))];
  
  // Calcular tempo médio de resposta
  const calculateAverageResponseTime = () => {
    if (!metrics || !metrics.responseTime || metrics.responseTime.length === 0) return 0;
    
    const sum = metrics.responseTime.reduce((acc, item) => acc + item.duration, 0);
    return (sum / metrics.responseTime.length).toFixed(2);
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Monitoramento do Sistema</h1>
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Voltar ao Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg">
              {/* Abas de navegação */}
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab("logs")}
                    className={`w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "logs"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Logs do Sistema
                  </button>
                  <button
                    onClick={() => setActiveTab("activities")}
                    className={`w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "activities"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Atividades dos Usuários
                  </button>
                  <button
                    onClick={() => setActiveTab("performance")}
                    className={`w-1/3 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "performance"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Desempenho do Sistema
                  </button>
                </nav>
              </div>
              
              {/* Conteúdo das abas */}
              <div className="p-6">
                {/* Aba de Logs do Sistema */}
                {activeTab === "logs" && (
                  <div>
                    <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
                      <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
                        <div>
                          <label htmlFor="filterLevel" className="block text-sm font-medium text-gray-700 mb-1">
                            Filtrar por Nível
                          </label>
                          <select
                            id="filterLevel"
                            value={filterLevel}
                            onChange={(e) => setFilterLevel(e.target.value)}
                            className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          >
                            <option value="all">Todos os Níveis</option>
                            {uniqueLevels.map(level => (
                              <option key={level} value={level}>{level}</option>
                            ))}
                          </select>
                        </div>
                        
                        <div>
                          <label htmlFor="filterModule" className="block text-sm font-medium text-gray-700 mb-1">
                            Filtrar por Módulo
                          </label>
                          <select
                            id="filterModule"
                            value={filterModule}
                            onChange={(e) => setFilterModule(e.target.value)}
                            className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          >
                            <option value="all">Todos os Módulos</option>
                            {uniqueModules.map(module => (
                              <option key={module} value={module}>{module}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div className="w-full md:w-1/3">
                        <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 mb-1">
                          Buscar nas Mensagens
                        </label>
                        <input
                          type="text"
                          id="searchQuery"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          placeholder="Digite para buscar..."
                          className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg mb-4">
                      <p className="text-sm text-gray-700">
                        Exibindo {filteredLogs.length} de {logs.length} logs
                      </p>
                    </div>
                    
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Timestamp
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Nível
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Módulo
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Mensagem
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {filteredLogs.length > 0 ? (
                            filteredLogs.map((log, index) => (
                              <tr key={index}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {new Date(log.timestamp).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                    log.level === "DEBUG" ? "bg-gray-100 text-gray-800" :
                                    log.level === "INFO" ? "bg-blue-100 text-blue-800" :
                                    log.level === "WARN" ? "bg-yellow-100 text-yellow-800" :
                                    log.level === "ERROR" ? "bg-red-100 text-red-800" :
                                    log.level === "CRITICAL" ? "bg-purple-100 text-purple-800" :
                                    "bg-gray-100 text-gray-800"
                                  }`}>
                                    {log.level}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {log.module}
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-500">
                                  {log.message}
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                                Nenhum log encontrado com os filtros atuais.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {/* Aba de Atividades dos Usuários */}
                {activeTab === "activities" && (
                  <div>
                    <div className="bg-gray-50 p-4 rounded-lg mb-4">
                      <p className="text-sm text-gray-700">
                        Total de {activities.length} atividades registradas
                      </p>
                    </div>
                    
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Timestamp
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Usuário
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Ação
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Caminho
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {activities.length > 0 ? (
                            activities.map((activity, index) => (
                              <tr key={index}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {new Date(activity.timestamp).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {activity.userName}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {activity.action}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {activity.path}
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                                Nenhuma atividade registrada.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {/* Aba de Desempenho do Sistema */}
                {activeTab === "performance" && (
                  <div>
                    {metrics ? (
                      <div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                          <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                              <div className="flex items-center">
                                <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                                  </svg>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                  <dt className="text-sm font-medium text-gray-500 truncate">
                                    Carregamentos de Página
                                  </dt>
                                  <dd className="flex items-baseline">
                                    <div className="text-2xl font-semibold text-gray-900">
                                      {metrics.pageLoads}
                                    </div>
                                  </dd>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                              <div className="flex items-center">
                                <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                                  </svg>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                  <dt className="text-sm font-medium text-gray-500 truncate">
                                    Chamadas de API
                                  </dt>
                                  <dd className="flex items-baseline">
                                    <div className="text-2xl font-semibold text-gray-900">
                                      {metrics.apiCalls}
                                    </div>
                                  </dd>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white overflow-hidden shadow rounded-lg">
                            <div className="px-4 py-5 sm:p-6">
                              <div className="flex items-center">
                                <div className="flex-shrink-0 bg-red-500 rounded-md p-3">
                                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                  <dt className="text-sm font-medium text-gray-500 truncate">
                                    Erros
                                  </dt>
                                  <dd className="flex items-baseline">
                                    <div className="text-2xl font-semibold text-gray-900">
                                      {metrics.errors}
                                    </div>
                                  </dd>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
                          <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900">
                              Tempo Médio de Resposta
                            </h3>
                            <div className="mt-2 max-w-xl text-sm text-gray-500">
                              <p>
                                Média de tempo de resposta para chamadas de API.
                              </p>
                            </div>
                            <div className="mt-3 text-3xl font-semibold text-gray-900">
                              {calculateAverageResponseTime()} ms
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-white overflow-hidden shadow rounded-lg">
                          <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                              Últimas Chamadas de API
                            </h3>
                            
                            {metrics.responseTime && metrics.responseTime.length > 0 ? (
                              <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                  <thead className="bg-gray-50">
                                    <tr>
                                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Timestamp
                                      </th>
                                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        URL
                                      </th>
                                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Duração (ms)
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody className="bg-white divide-y divide-gray-200">
                                    {metrics.responseTime.slice(-10).map((item, index) => (
                                      <tr key={index}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                          {new Date(item.timestamp).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                          {item.url}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                          {item.duration.toFixed(2)}
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            ) : (
                              <p className="text-sm text-gray-500">
                                Nenhuma chamada de API registrada.
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-10">
                        <p className="text-gray-500">
                          Nenhuma métrica de desempenho disponível.
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
