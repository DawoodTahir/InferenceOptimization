import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Cpu, Activity, Zap, Terminal } from 'lucide-react';

const App = () => {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'System online. RTX 4000 Ada detected. Engine ready.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ latency: '0ms', throughput: '0 t/s', status: 'Idle' });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);
    setStats(prev => ({ ...prev, status: 'Processing...' }));

    const startTime = performance.now();

    try {
      const response = await fetch('http://localhost:8000/Inference', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputs: userMessage }),
      });

      const data = await response.json();
      
      const endTime = performance.now();
      const latency = (endTime - startTime).toFixed(2);
      
      // Rough throughput estimation (chars / seconds)
      const throughput = (data.results.length / ((endTime - startTime) / 1000)).toFixed(1);

      if (data.status === '200' || data.status === 'good') {
        setMessages(prev => [...prev, { role: 'assistant', content: data.results }]);
        setStats({ 
          latency: `${latency}ms`, 
          throughput: `${throughput} char/s`, 
          status: 'Idle' 
        });
      } else {
        setMessages(prev => [...prev, { role: 'error', content: `Error: ${data.results || data.message}` }]);
        setStats(prev => ({ ...prev, status: 'Error' }));
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'error', content: `Network Error: ${error.message}` }]);
      setStats(prev => ({ ...prev, status: 'Offline' }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0a0a0a] text-gray-100 font-mono overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-[#111] border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-green-500" />
          <h1 className="text-lg font-bold tracking-tight text-white">
            INFERENCE<span className="text-green-500">_OPT</span>
          </h1>
        </div>
        <div className="flex items-center gap-6 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-500" />
            <span>RTX 4000 Ada</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-500" />
            <span>{stats.status}</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            <span>{stats.latency}</span>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role !== 'user' && (
              <div className={`w-8 h-8 rounded flex items-center justify-center shrink-0 ${
                msg.role === 'error' ? 'bg-red-900/20 text-red-500' : 'bg-green-900/20 text-green-500'
              }`}>
                {msg.role === 'system' ? <Terminal size={16} /> : <Bot size={16} />}
              </div>
            )}
            
            <div className={`px-4 py-3 rounded-lg max-w-[80%] text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-blue-600/10 text-blue-100 border border-blue-500/20' 
                : msg.role === 'error'
                ? 'bg-red-900/10 text-red-200 border border-red-500/20'
                : 'bg-gray-900 text-gray-300 border border-gray-800'
            }`}>
              {msg.content}
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded bg-blue-900/20 text-blue-500 flex items-center justify-center shrink-0">
                <User size={16} />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 max-w-4xl mx-auto">
            <div className="w-8 h-8 rounded bg-green-900/20 text-green-500 flex items-center justify-center shrink-0 animate-pulse">
              <Bot size={16} />
            </div>
            <div className="px-4 py-3 rounded-lg bg-gray-900 border border-gray-800 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-green-500 rounded-full animate-bounce delay-75"></span>
              <span className="w-2 h-2 bg-green-500 rounded-full animate-bounce delay-150"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-[#111] border-t border-gray-800">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command or prompt..."
            className="flex-1 bg-black border border-gray-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 transition-colors placeholder-gray-600"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed text-black font-semibold rounded-lg transition-colors flex items-center gap-2"
          >
            <Send size={16} />
            <span className="hidden sm:inline">GENERATE</span>
          </button>
        </form>
        <div className="max-w-4xl mx-auto mt-2 text-center">
          <p className="text-[10px] text-gray-600">
            Powered by SGLang / vLLM • Inference Optimization Engine v1.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;
