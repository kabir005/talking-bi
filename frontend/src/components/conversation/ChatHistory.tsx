import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import { QueryResultCard } from '../query/QueryResultCard';
import { NLQueryResult } from '../../types';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content?: string;
  insights?: any;
  recommendations?: any[];
  summary?: any;
  queryResult?: NLQueryResult;
  timestamp: Date;
}

interface ChatHistoryProps {
  messages: Message[];
}

export default function ChatHistory({ messages }: ChatHistoryProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-text-tertiary">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-surface-2 flex items-center justify-center">
            <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="font-heading text-lg font-semibold mb-2">Start a Conversation</h3>
          <p className="text-sm">
            Ask me anything about your data. I can analyze trends, find insights, 
            and provide strategic recommendations.
          </p>
          <div className="mt-4 text-xs space-y-1">
            <p className="text-accent">Try asking:</p>
            <p>"What are the top performing products?"</p>
            <p>"Show me sales trends over time"</p>
            <p>"Which regions need attention?"</p>
            <p>"top 10 by revenue"</p>
            <p>"last 30 days"</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6">
      <div className="max-w-5xl mx-auto">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage
              type={message.type}
              content={message.content}
              insights={message.insights}
              recommendations={message.recommendations}
              summary={message.summary}
              timestamp={message.timestamp}
            />
            {/* Render query result if present */}
            {message.queryResult && (
              <div className="mt-4 mb-6">
                <QueryResultCard result={message.queryResult} />
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
