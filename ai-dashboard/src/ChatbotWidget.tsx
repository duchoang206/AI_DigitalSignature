import { useState, useRef, useEffect } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import { Send, Bot, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

type Message = {
  id: string;
  sender: 'user' | 'bot';
  text: string;
};

type ChatbotWidgetProps = {
  messages: Message[];
  setMessages: Dispatch<SetStateAction<Message[]>>;
  onOpenFile: (preferredFile?: string) => void;
  onStartFaceNetSign: () => void;
};

export default function ChatbotWidget({ messages, setMessages, onOpenFile, onStartFaceNetSign }: ChatbotWidgetProps) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const rawInput = inputValue.trim();
    const userMsg = rawInput.toLowerCase();
    const newId = Date.now().toString();
    
    setMessages(prev => [...prev, { id: newId, sender: 'user', text: rawInput }]);
    setInputValue('');

    try {
      // Call backend for command processing
      const response = await fetch('/api/chatbot/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: rawInput })
      });
      const data = await response.json();
      
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: data.response
        }]);

        // Action triggers based on command
        if (data.command === 'command_open_sign_doc') {
          const pref = userMsg.includes('pipeline_config.json') ? 'pipeline_config.json' : undefined;
          onOpenFile(pref);
        } else if (data.command === 'command_verify') {
          // You could trigger verification mode here
        } else if (userMsg.includes('xác thực') || userMsg.includes('face') || userMsg.includes('ký')) {
          // Fallback triggers if command processing is simple
          if (userMsg.includes('ký') && !userMsg.includes('file')) {
             onStartFaceNetSign();
          }
        }
      }, 600);
    } catch (err) {
      // Fallback local logic if API fails
      setTimeout(() => {
        if (userMsg.includes('pipeline_config.json')) {
          setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Tôi sẽ mở hộp thoại chọn file cấu hình pipeline_config.json cho bạn.' }]);
          onOpenFile('pipeline_config.json');
        } else {
          setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'bot', text: 'Xin lỗi, tôi gặp sự cố kết nối. Hãy thử lại sau.' }]);
        }
      }, 600);
    }
  };

  return (
    <div className="chatbot-wrapper h-full w-[350px]">
      <motion.div 
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="chatbot-window glass-panel h-full flex flex-col overflow-hidden border-[#00f0ff]/20"
      >
        <div className="chatbot-header bg-gradient-to-r from-[#00f0ff]/10 to-[#8a2be2]/10 p-4 border-b border-white/10">
          <div className="chatbot-title flex items-center gap-3">
            <div className="relative">
              <div className="status-dot bg-green-400 w-3 h-3 rounded-full"></div>
              <div className="status-dot bg-green-400 w-3 h-3 rounded-full absolute inset-0 animate-ping opacity-75"></div>
            </div>
            <span className="font-bold tracking-wider text-white/90 uppercase text-xs">AI Copilot Security</span>
          </div>
        </div>

        <div className="chatbot-messages flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div 
                key={msg.id}
                initial={{ opacity: 0, x: msg.sender === 'user' ? 10 : -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-2 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.sender === 'bot' ? 'bg-[#00f0ff]/20 text-[#00f0ff]' : 'bg-white/10 text-white/70'}`}>
                    {msg.sender === 'bot' ? <Bot size={16} /> : <UserIcon size={16} />}
                  </div>
                  <div className={`chat-bubble p-3 rounded-2xl text-sm leading-relaxed ${
                    msg.sender === 'user' 
                      ? 'bg-[#00f0ff]/20 text-white border border-[#00f0ff]/20 rounded-tr-none' 
                      : 'bg-white/5 text-white/90 border border-white/5 rounded-tl-none'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input-area p-4 bg-black/40 border-t border-white/10 backdrop-blur-md">
          <div className="w-full relative flex items-center gap-2">
            <input 
              type="text" 
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Hỏi AI Copilot..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-[#00f0ff]/50 transition-all placeholder:text-white/20"
            />
            <button 
              className="p-3 bg-[#00f0ff] text-black rounded-xl hover:bg-[#00f0ff]/80 transition-all active:scale-95 shadow-[0_0_15px_rgba(0,240,255,0.4)]" 
              onClick={handleSend}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
