"use client";

import { useState } from "react";
import Link from "next/link";

export default function Configuracoes() {
  const [activeTab, setActiveTab] = useState("geral");
  const [salvando, setSalvando] = useState(false);
  
  // Estados para configurações gerais
  const [nomeClinica, setNomeClinica] = useState("Clínica Tanaka");
  const [telefoneClinica, setTelefoneClinica] = useState("+81 90-1234-5678");
  const [emailClinica, setEmailClinica] = useState("contato@clinicatanaka.jp");
  const [enderecoClinica, setEnderecoClinica] = useState("1-2-3 Shibuya, Tóquio, Japão");
  
  // Estados para configurações de horários
  const [diasFuncionamento, setDiasFuncionamento] = useState({
    segunda: true,
    terca: true,
    quarta: true,
    quinta: true,
    sexta: true,
    sabado: true,
    domingo: false
  });
  const [horarioInicio, setHorarioInicio] = useState("09:00");
  const [horarioFim, setHorarioFim] = useState("18:00");
  const [intervaloConsulta, setIntervaloConsulta] = useState("30");
  const [horarioAlmoco, setHorarioAlmoco] = useState({
    inicio: "12:00",
    fim: "14:00"
  });
  
  // Estados para configurações do chatbot
  const [mensagemBoasVindas, setMensagemBoasVindas] = useState({
    japones: "クリニカ・タナカへようこそ！このチャットボットでは、診療予約や診療所とのコミュニケーションをサポートします。",
    ingles: "Welcome to Clínica Tanaka! This chatbot will help you schedule appointments or communicate with the clinic.",
    portugues: "Bem-vindo à Clínica Tanaka! Este chatbot irá ajudá-lo a agendar consultas ou se comunicar com a clínica."
  });
  
  const [corPrimaria, setCorPrimaria] = useState("#0088cc");
  const [logoURL, setLogoURL] = useState("/logo-clinica.png");
  
  // Função para salvar configurações
  const salvarConfiguracoes = () => {
    setSalvando(true);
    
    // Simulação de salvamento no backend
    setTimeout(() => {
      setSalvando(false);
      alert("Configurações salvas com sucesso!");
    }, 1500);
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Configurações do Sistema</h1>
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
                    onClick={() => setActiveTab("geral")}
                    className={`w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "geral"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Informações Gerais
                  </button>
                  <button
                    onClick={() => setActiveTab("horarios")}
                    className={`w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "horarios"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Horários de Funcionamento
                  </button>
                  <button
                    onClick={() => setActiveTab("chatbot")}
                    className={`w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "chatbot"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Configurações do Chatbot
                  </button>
                  <button
                    onClick={() => setActiveTab("notificacoes")}
                    className={`w-1/4 py-4 px-1 text-center border-b-2 font-medium text-sm ${
                      activeTab === "notificacoes"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    Notificações
                  </button>
                </nav>
              </div>
              
              {/* Conteúdo das abas */}
              <div className="p-6">
                {/* Aba de Informações Gerais */}
                {activeTab === "geral" && (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Informações da Clínica</h2>
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="nomeClinica" className="block text-sm font-medium text-gray-700">
                          Nome da Clínica
                        </label>
                        <input
                          type="text"
                          id="nomeClinica"
                          value={nomeClinica}
                          onChange={(e) => setNomeClinica(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                      
                      <div>
                        <label htmlFor="telefoneClinica" className="block text-sm font-medium text-gray-700">
                          Telefone
                        </label>
                        <input
                          type="text"
                          id="telefoneClinica"
                          value={telefoneClinica}
                          onChange={(e) => setTelefoneClinica(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                      
                      <div>
                        <label htmlFor="emailClinica" className="block text-sm font-medium text-gray-700">
                          E-mail
                        </label>
                        <input
                          type="email"
                          id="emailClinica"
                          value={emailClinica}
                          onChange={(e) => setEmailClinica(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                      
                      <div>
                        <label htmlFor="enderecoClinica" className="block text-sm font-medium text-gray-700">
                          Endereço
                        </label>
                        <textarea
                          id="enderecoClinica"
                          value={enderecoClinica}
                          onChange={(e) => setEnderecoClinica(e.target.value)}
                          rows={3}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Aba de Horários de Funcionamento */}
                {activeTab === "horarios" && (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Horários de Funcionamento</h2>
                    
                    <div className="mb-6">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Dias de Funcionamento</h3>
                      <div className="grid grid-cols-7 gap-2">
                        {Object.entries({
                          segunda: "Seg",
                          terca: "Ter",
                          quarta: "Qua",
                          quinta: "Qui",
                          sexta: "Sex",
                          sabado: "Sáb",
                          domingo: "Dom"
                        }).map(([key, label]) => (
                          <div key={key} className="flex items-center">
                            <input
                              id={`dia-${key}`}
                              type="checkbox"
                              checked={diasFuncionamento[key as keyof typeof diasFuncionamento]}
                              onChange={(e) => setDiasFuncionamento({
                                ...diasFuncionamento,
                                [key]: e.target.checked
                              })}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label htmlFor={`dia-${key}`} className="ml-2 block text-sm text-gray-900">
                              {label}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="horarioInicio" className="block text-sm font-medium text-gray-700">
                          Horário de Início
                        </label>
                        <input
                          type="time"
                          id="horarioInicio"
                          value={horarioInicio}
                          onChange={(e) => setHorarioInicio(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                      
                      <div>
                        <label htmlFor="horarioFim" className="block text-sm font-medium text-gray-700">
                          Horário de Término
                        </label>
                        <input
                          type="time"
                          id="horarioFim"
                          value={horarioFim}
                          onChange={(e) => setHorarioFim(e.target.value)}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                    
                    <div className="mt-6">
                      <label htmlFor="intervaloConsulta" className="block text-sm font-medium text-gray-700">
                        Intervalo entre Consultas (minutos)
                      </label>
                      <select
                        id="intervaloConsulta"
                        value={intervaloConsulta}
                        onChange={(e) => setIntervaloConsulta(e.target.value)}
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      >
                        <option value="15">15 minutos</option>
                        <option value="30">30 minutos</option>
                        <option value="45">45 minutos</option>
                        <option value="60">60 minutos</option>
                      </select>
                    </div>
                    
                    <div className="mt-6">
                      <h3 className="text-sm font-medium text-gray-700 mb-2">Horário de Almoço/Intervalo</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label htmlFor="horarioAlmocoInicio" className="block text-sm font-medium text-gray-700">
                            Início
                          </label>
                          <input
                            type="time"
                            id="horarioAlmocoInicio"
                            value={horarioAlmoco.inicio}
                            onChange={(e) => setHorarioAlmoco({...horarioAlmoco, inicio: e.target.value})}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          />
                        </div>
                        
                        <div>
                          <label htmlFor="horarioAlmocoFim" className="block text-sm font-medium text-gray-700">
                            Fim
                          </label>
                          <input
                            type="time"
                            id="horarioAlmocoFim"
                            value={horarioAlmoco.fim}
                            onChange={(e) => setHorarioAlmoco({...horarioAlmoco, fim: e.target.value})}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Aba de Configurações do Chatbot */}
                {activeTab === "chatbot" && (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Configurações do Chatbot</h2>
                    
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">Mensagem de Boas-vindas</h3>
                        
                        <div className="space-y-4">
                          <div>
                            <label htmlFor="mensagemJapones" className="block text-sm font-medium text-gray-700">
                              Japonês 🇯🇵
                            </label>
                            <textarea
                              id="mensagemJapones"
                              value={mensagemBoasVindas.japones}
                              onChange={(e) => setMensagemBoasVindas({...mensagemBoasVindas, japones: e.target.value})}
                              rows={3}
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                          
                          <div>
                            <label htmlFor="mensagemIngles" className="block text-sm font-medium text-gray-700">
                              Inglês 🇺🇸
                            </label>
                            <textarea
                              id="mensagemIngles"
                              value={mensagemBoasVindas.ingles}
                              onChange={(e) => setMensagemBoasVindas({...mensagemBoasVindas, ingles: e.target.value})}
                              rows={3}
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                          
                          <div>
                            <label htmlFor="mensagemPortugues" className="block text-sm font-medium text-gray-700">
                              Português 🇧🇷
                            </label>
                            <textarea
                              id="mensagemPortugues"
                              value={mensagemBoasVindas.portugues}
                              onChange={(e) => setMensagemBoasVindas({...mensagemBoasVindas, portugues: e.target.value})}
                              rows={3}
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">Personalização Visual</h3>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label htmlFor="corPrimaria" className="block text-sm font-medium text-gray-700">
                              Cor Primária
                            </label>
                            <div className="mt-1 flex items-center">
                              <input
                                type="color"
                                id="corPrimaria"
                                value={corPrimaria}
                                onChange={(e) => setCorPrimaria(e.target.value)}
                                className="h-8 w-8 border border-gray-300 rounded-md shadow-sm"
                              />
                              <input
                                type="text"
                                value={corPrimaria}
                                onChange={(e) => setCorPrimaria(e.target.value)}
                                className="ml-2 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                              />
                            </div>
                          </div>
                          
                          <div>
                            <label htmlFor="logoURL" className="block text-sm font-medium text-gray-700">
                              URL do Logo
                            </label>
                            <input
                              type="text"
                              id="logoURL"
                              value={logoURL}
                              onChange={(e) => setLogoURL(e.target.value)}
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                        </div>
                        
                        <div className="mt-4">
                          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                            Fazer Upload de Logo
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Aba de Notificações */}
                {activeTab === "notificacoes" && (
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">Configurações de Notificações</h2>
                    
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">Notificações para Pacientes</h3>
                        
                        <div className="space-y-4">
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoConfirmacao"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoConfirmacao" className="font-medium text-gray-700">Confirmação de Agendamento</label>
                              <p className="text-gray-500">Enviar mensagem quando um agendamento for confirmado</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoLembrete"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoLembrete" className="font-medium text-gray-700">Lembrete de Consulta</label>
                              <p className="text-gray-500">Enviar lembrete 24 horas antes da consulta</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoCancelamento"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoCancelamento" className="font-medium text-gray-700">Cancelamento de Consulta</label>
                              <p className="text-gray-500">Enviar mensagem quando uma consulta for cancelada</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">Notificações para a Clínica</h3>
                        
                        <div className="space-y-4">
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoNovoAgendamento"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoNovoAgendamento" className="font-medium text-gray-700">Novo Agendamento</label>
                              <p className="text-gray-500">Receber notificação quando um novo agendamento for solicitado</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoCancelamentoPaciente"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoCancelamentoPaciente" className="font-medium text-gray-700">Cancelamento pelo Paciente</label>
                              <p className="text-gray-500">Receber notificação quando um paciente cancelar uma consulta</p>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="notificacaoRelatorioDiario"
                                type="checkbox"
                                checked={true}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="notificacaoRelatorioDiario" className="font-medium text-gray-700">Relatório Diário</label>
                              <p className="text-gray-500">Receber um resumo diário dos agendamentos do dia seguinte</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">Configurações de LINE</h3>
                        
                        <div className="space-y-4">
                          <div>
                            <label htmlFor="lineChannelToken" className="block text-sm font-medium text-gray-700">
                              LINE Channel Access Token
                            </label>
                            <input
                              type="password"
                              id="lineChannelToken"
                              value="••••••••••••••••••••••••••••••••••••••••"
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                          
                          <div>
                            <label htmlFor="lineChannelSecret" className="block text-sm font-medium text-gray-700">
                              LINE Channel Secret
                            </label>
                            <input
                              type="password"
                              id="lineChannelSecret"
                              value="••••••••••••••••••••••"
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                          
                          <div>
                            <label htmlFor="lineOwnerID" className="block text-sm font-medium text-gray-700">
                              ID do Dono da Clínica no LINE
                            </label>
                            <input
                              type="text"
                              id="lineOwnerID"
                              value="U1234567890abcdef1234567890abcdef"
                              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Botões de ação */}
              <div className="px-6 py-3 bg-gray-50 text-right sm:px-6 rounded-b-lg">
                <button
                  onClick={salvarConfiguracoes}
                  disabled={salvando}
                  className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                    salvando ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"
                  } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                >
                  {salvando ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Salvando...
                    </>
                  ) : (
                    "Salvar Configurações"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
