// src/components/chat/ChatInterface.jsx
import { Heart, Loader2, Phone, Send, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { apiService } from '../../services/apiService';

const MessageBubble = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-sm'
            : 'bg-gray-100 text-gray-800 rounded-bl-sm'
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-1">
            <Heart className="w-4 h-4 text-blue-500" />
            <span className="text-xs font-medium text-gray-500">Apoyo Mental</span>
          </div>
        )}
        <p className="text-sm whitespace-pre-wrap">{message.text}</p>
        <div className={`text-xs mt-1 ${isUser ? 'text-white/70' : 'text-gray-400'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};

const HelpLinesModal = ({ lines, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full">
        <div className="border-b px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Phone className="w-5 h-5 text-red-500" />
            <h3 className="font-semibold">Líneas de Ayuda</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="p-4 space-y-3">
          {lines.map((line, idx) => (
            <div key={idx} className="bg-gray-50 rounded-xl p-3">
              <div className="font-medium">{line.name}</div>
              <a href={`tel:${line.number.replace(/\s/g, '')}`} className="text-2xl font-bold text-blue-600">
                {line.number}
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      text: 'Hola, soy tu asistente de apoyo emocional. ¿Cómo te sientes hoy?',
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showHelpLines, setShowHelpLines] = useState(false);
  const [crisisLines, setCrisisLines] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const loadLines = async () => {
      const lines = await apiService.getLinesOfHelp();
      setCrisisLines(lines);
    };
    loadLines();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const text = inputText.trim();
    if (!text || isLoading) return;

    setInputText('');
    
    const userMessage = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const analysis = await apiService.analyzeRisk(text);
      
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: analysis.response.message,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);

      if (analysis.risk_analysis.requires_immediate_action) {
        setShowHelpLines(true);
      }
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Lo siento, hubo un problema. Si estás en crisis, llama a la Línea de la Vida: 800 911 2000',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Heart className="w-6 h-6" />
              <h1 className="font-semibold">Apoyo Mental</h1>
            </div>
            <button
              onClick={() => setShowHelpLines(true)}
              className="bg-white/20 px-3 py-1 rounded-full text-sm hover:bg-white/30"
            >
              Ayuda
            </button>
            <button
              onClick={() => {
                const isDark = document.documentElement.classList.toggle('dark');
                localStorage.setItem('darkMode', isDark);
              }}
              className="bg-white/20 px-3 py-1 rounded-full text-sm hover:bg-white/30"
            >
              {document.documentElement.classList.contains('dark') ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="max-w-3xl mx-auto">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t bg-white p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe cómo te sientes..."
            className="flex-1 border border-gray-300 rounded-2xl px-4 py-2 text-sm focus:outline-none focus:border-blue-500 resize-none"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputText.trim() || isLoading}
            className={`p-3 rounded-full transition-colors ${
              inputText.trim() && !isLoading
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          Esta app es una herramienta de apoyo. En crisis: Línea de la Vida 800 911 2000
        </p>
      </div>

      {/* Modal */}
      {showHelpLines && (
        <HelpLinesModal lines={crisisLines} onClose={() => setShowHelpLines(false)} />
      )}
    </div>
  );
};

export default ChatInterface;