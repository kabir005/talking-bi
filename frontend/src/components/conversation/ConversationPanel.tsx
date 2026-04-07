// ConversationPanel.tsx — Multi-turn AI chat panel for dataset Q&A.
// Connected to POST /api/conversation/chat with sliding-window history.

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, MessageSquare, RotateCcw } from 'lucide-react';
import { apiClient } from '../../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ConversationPanelProps {
  datasetId: string;
  schema?: Record<string, any>;
  kpis?: Record<string, any>;
  className?: string;
}

export function ConversationPanel({ datasetId, schema = {}, kpis, className = '' }: ConversationPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [history, setHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const SUGGESTED_QUESTIONS = [
    'What are the key trends in this data?',
    'Which segment performs best?',
    'Summarize the top 3 insights',
    'What should I focus on to improve performance?',
  ];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const query = (text ?? input).trim();
    if (!query || loading) return;

    const userMsg: Message = { role: 'user', content: query, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post('/api/conversation/chat', {
        dataset_id: datasetId,
        query,
        history,
        schema,
        kpis: kpis ?? null,
      });

      const assistantMsg: Message = {
        role: 'assistant',
        content: res.data.answer,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
      setHistory(res.data.history);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to get response. Try again.');
      setMessages(prev => prev.slice(0, -1)); // remove optimistic user msg
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setHistory([]);
    setError(null);
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Analyst</h3>
            <p className="text-xs text-white/50">Ask anything about your data</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearConversation}
            className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-white/40 hover:text-white/70"
            title="Clear conversation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <p className="text-xs text-white/40 text-center pt-2">
              Ask questions about your data in plain English
            </p>
            <div className="grid gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-left text-xs px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div className={`w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center ${
                msg.role === 'user'
                  ? 'bg-indigo-500/30 border border-indigo-500/50'
                  : 'bg-purple-500/20 border border-purple-500/40'
              }`}>
                {msg.role === 'user'
                  ? <User className="w-3.5 h-3.5 text-indigo-300" />
                  : <Bot className="w-3.5 h-3.5 text-purple-300" />
                }
              </div>

              {/* Bubble */}
              <div className={`max-w-[80%] px-3 py-2 rounded-xl text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-indigo-500/20 border border-indigo-500/30 text-white ml-auto'
                  : 'bg-white/5 border border-white/10 text-white/85'
              }`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2.5"
          >
            <div className="w-7 h-7 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-purple-300" />
            </div>
            <div className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 flex items-center gap-2">
              <Loader2 className="w-3 h-3 text-purple-400 animate-spin" />
              <span className="text-xs text-white/40">Thinking...</span>
            </div>
          </motion.div>
        )}

        {/* Error */}
        {error && (
          <div className="text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2 border border-red-500/20">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* History badge */}
      {history.length > 0 && (
        <div className="px-4 pb-1">
          <span className="text-[10px] text-white/30">
            {Math.floor(history.length / 2)} turn{history.length > 2 ? 's' : ''} in context
          </span>
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4 pt-2 border-t border-white/10">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your data... (Enter to send)"
            rows={1}
            className="flex-1 resize-none bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white placeholder-white/30 outline-none focus:border-indigo-500/50 focus:bg-white/8 transition-all max-h-24 overflow-y-auto"
            style={{ lineHeight: '1.4' }}
            onInput={(e) => {
              const t = e.target as HTMLTextAreaElement;
              t.style.height = 'auto';
              t.style.height = Math.min(t.scrollHeight, 96) + 'px';
            }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
          >
            <Send className="w-3.5 h-3.5 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
