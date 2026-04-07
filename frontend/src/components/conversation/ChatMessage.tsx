import { Bot, User, TrendingUp, Lightbulb, AlertCircle, BarChart3 } from 'lucide-react';

interface ChatMessageProps {
  type: 'user' | 'assistant';
  content?: string;
  insights?: {
    executive_summary?: string;
    key_insights?: string[];
    watch_out?: string[];
    overall_confidence?: number;
    data_quality?: string;
  };
  recommendations?: Array<{
    rank: number;
    action: string;
    expected_impact: string;
    timeline: string;
    risk_level: string;
    confidence: number;
    rationale?: string;
  }>;
  summary?: {
    kpis_analyzed?: number;
    charts_generated?: number;
    insights_found?: number;
    recommendations_count?: number;
    overall_confidence?: number;
  };
  timestamp?: Date;
}

export default function ChatMessage({ 
  type, 
  content, 
  insights, 
  recommendations,
  summary,
  timestamp 
}: ChatMessageProps) {
  const isUser = type === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-6`}>
      {/* Avatar */}
      <div className={`
        w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
        ${isUser ? 'bg-accent' : 'bg-surface-2 border border-border'}
      `}>
        {isUser ? (
          <User className="w-5 h-5 text-bg" />
        ) : (
          <Bot className="w-5 h-5 text-accent" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : 'text-left'}`}>
        {/* User Message */}
        {isUser && content && (
          <div className="inline-block px-4 py-3 bg-accent text-bg rounded-2xl rounded-tr-sm">
            <p className="text-sm">{content}</p>
          </div>
        )}

        {/* Assistant Message */}
        {!isUser && (
          <div className="space-y-4">
            {/* Text Response */}
            {content && (
              <div className="px-4 py-3 bg-surface-2 rounded-2xl rounded-tl-sm">
                <p className="text-sm leading-relaxed">{content}</p>
              </div>
            )}

            {/* Analysis Summary */}
            {summary && (
              <div className="px-4 py-3 bg-surface-2 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 className="w-4 h-4 text-accent" />
                  <span className="font-semibold text-sm">Analysis Complete</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="flex justify-between">
                    <span className="text-text-tertiary">KPIs Analyzed:</span>
                    <span className="font-mono font-semibold">{summary.kpis_analyzed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-tertiary">Charts Generated:</span>
                    <span className="font-mono font-semibold">{summary.charts_generated || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-tertiary">Insights Found:</span>
                    <span className="font-mono font-semibold">{summary.insights_found || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-tertiary">Confidence:</span>
                    <span className="font-mono font-semibold text-accent">{summary.overall_confidence || 0}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Executive Summary */}
            {insights?.executive_summary && (
              <div className="px-4 py-3 bg-surface-2 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-accent" />
                  <span className="font-semibold text-sm">Executive Summary</span>
                </div>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {insights.executive_summary}
                </p>
                {insights.overall_confidence !== undefined && (
                  <div className="mt-3 flex items-center gap-2">
                    <div className="flex-1 bg-surface rounded-full h-1.5">
                      <div
                        className="bg-accent h-1.5 rounded-full transition-all"
                        style={{ width: `${insights.overall_confidence}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-text-tertiary">
                      {insights.overall_confidence}% confidence
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Key Insights */}
            {insights?.key_insights && insights.key_insights.length > 0 && (
              <div className="px-4 py-3 bg-surface-2 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-accent" />
                  <span className="font-semibold text-sm">Key Insights</span>
                </div>
                <div className="space-y-2">
                  {insights.key_insights.map((insight, idx) => (
                    <div key={idx} className="flex gap-2 text-sm">
                      <span className="text-accent font-bold flex-shrink-0">{idx + 1}.</span>
                      <span className="text-text-secondary leading-relaxed">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Watch Out Items */}
            {insights?.watch_out && insights.watch_out.length > 0 && (
              <div className="px-4 py-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                  <span className="font-semibold text-sm text-yellow-500">Watch Out</span>
                </div>
                <div className="space-y-2">
                  {insights.watch_out.map((warning, idx) => (
                    <div key={idx} className="flex gap-2 text-sm">
                      <span className="text-yellow-500 font-bold flex-shrink-0">⚠</span>
                      <span className="text-text-secondary leading-relaxed">{warning}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {recommendations && recommendations.length > 0 && (
              <div className="px-4 py-3 bg-surface-2 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-accent" />
                  <span className="font-semibold text-sm">Strategic Recommendations</span>
                </div>
                <div className="space-y-3">
                  {recommendations.map((rec) => (
                    <div key={rec.rank} className="p-3 bg-surface rounded-lg border border-border">
                      <div className="flex items-start gap-3">
                        <div className="w-6 h-6 rounded-full bg-accent text-bg flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                          {rec.rank}
                        </div>
                        <div className="flex-1 space-y-2">
                          <div className="font-semibold text-sm">{rec.action}</div>
                          
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-text-tertiary">Impact: </span>
                              <span className="text-accent font-semibold">{rec.expected_impact}</span>
                            </div>
                            <div>
                              <span className="text-text-tertiary">Timeline: </span>
                              <span className="font-semibold">{rec.timeline}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-3 text-xs">
                            <div className="flex items-center gap-1">
                              <span className="text-text-tertiary">Risk:</span>
                              <span className={`
                                px-2 py-0.5 rounded font-semibold
                                ${rec.risk_level === 'low' ? 'bg-green-500/20 text-green-500' : ''}
                                ${rec.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-500' : ''}
                                ${rec.risk_level === 'high' ? 'bg-red-500/20 text-red-500' : ''}
                              `}>
                                {rec.risk_level}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-text-tertiary">Confidence:</span>
                              <span className="font-mono font-semibold">{rec.confidence}%</span>
                            </div>
                          </div>

                          {rec.rationale && (
                            <p className="text-xs text-text-tertiary leading-relaxed pt-2 border-t border-border">
                              {rec.rationale}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Data Quality Badge */}
            {insights?.data_quality && (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-surface-2 rounded-full text-xs">
                <span className="text-text-tertiary">Data Quality:</span>
                <span className={`
                  px-2 py-0.5 rounded-full font-semibold
                  ${insights.data_quality === 'high' ? 'bg-green-500/20 text-green-500' : ''}
                  ${insights.data_quality === 'medium' ? 'bg-yellow-500/20 text-yellow-500' : ''}
                  ${insights.data_quality === 'low' ? 'bg-red-500/20 text-red-500' : ''}
                `}>
                  {insights.data_quality.toUpperCase()}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        {timestamp && (
          <div className={`text-xs text-text-tertiary mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </div>
  );
}
