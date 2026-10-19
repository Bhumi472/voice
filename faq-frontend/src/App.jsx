import React, { useState, useRef } from 'react';
import { Send, Volume2, Mic, Bot, User, Globe } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! Ask me any FAQ question in English, Hindi, or Marathi.' }
  ]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const audioRef = useRef(null);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage, language: language })
      });
      const data = await res.json();

      setMessages(prev => [...prev, { sender: 'bot', text: data.response }]);
      setLoading(false);

      // Play audio response automatically
      if (audioRef.current) {
        audioRef.current.src = `${data.audio_url}?t=${new Date().getTime()}`;
        audioRef.current.play();
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { sender: 'bot', text: 'Error connecting to backend server.' }]);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-800 border-b border-slate-700 shadow-md">
        <div className="flex items-center space-x-3">
          <Bot className="w-8 h-8 text-indigo-400" />
          <h1 className="text-xl font-bold tracking-wide">AI FAQ Chatbot (Multilingual & Voice)</h1>
        </div>
        
        {/* Language Selector */}
        <div className="flex items-center space-x-2 bg-slate-700 px-3 py-1.5 rounded-lg">
          <Globe className="w-4 h-4 text-indigo-300" />
          <select 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-transparent text-sm focus:outline-none cursor-pointer"
          >
            <option value="en" className="bg-slate-800">English (Indian Accent)</option>
            <option value="hi" className="bg-slate-800">Hindi (हिंदी)</option>
            <option value="mr" className="bg-slate-800">Marathi (मराठी)</option>
          </select>
        </div>
      </header>

      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 max-w-3xl w-full mx-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`flex items-start space-x-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.sender === 'bot' && (
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shadow">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`max-w-md px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-md ${
              msg.sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none' 
                : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none'
            }`}>
              {msg.text}
            </div>
            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shadow">
                <User className="w-5 h-5 text-slate-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-slate-400 text-sm italic">
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-100"></div>
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-200"></div>
            <span>Bot is thinking & generating voice...</span>
          </div>
        )}
      </div>

      {/* Hidden Audio Player for Speech Output */}
      <audio ref={audioRef} hidden />

      {/* Input Form */}
      <div className="bg-slate-800 border-t border-slate-700 p-4">
        <form onSubmit={sendMessage} className="max-w-3xl mx-auto flex items-center space-x-3">
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question here (or in Hindi/Marathi)..." 
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 transition"
          />
          <button 
            type="submit" 
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-3 rounded-xl flex items-center space-x-2 font-medium transition shadow-lg"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;