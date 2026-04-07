import { AlertCircle, TrendingUp, Lightbulb, CheckCircle } from 'lucide-react';

interface InsightPanelProps {
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
  }>;
}

export default function InsightPanel({ insights, recommendations }: InsightPanelProps) {
  if (!insights && !recommendations) {
    return (
      <aside className="w-80 bg-surface border-l border-border p-6 overflow-y-auto">
        <div className="text-center text-text-tertiary">
          <Lightbulb className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Run analysis to see AI insights</p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-80 bg-surface border-l border-border overflow-y-auto">
      <div className="p-6 space-y-6">
        {/* Header */}
        <div>
          <h2 className="font-heading text-xl font-semibold mb-2">AI Insights</h2>
          {insights?.overall_confidence !== undefined && (
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-surface-2 rounded-full h-2">
                <div
                  className="bg-accent h-2 rounded-full transition-all"
                  style={{ width: `${insights.overall_confidence}%` }}
                />
              </div>
              <span className="text-sm font-mono">{insights.overall_confidence}%</span>
            </div>
          )}
        </div>

        {/* Executive Summary */}
        {insights?.executive_summary && (
          <div className="p-4 bg-surface-2 rounded-lg">
            <h3 className="font-heading font-semibold mb-2 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-accent" />
              Executive Summary
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed">
              {insights.executive_summary}
            </p>
          </div>
        )}

        {/* Key Findings */}
        {insights?.key_insights && insights.key_insights.length > 0 && (
          <div>
            <h3 className="font-heading font-semibold mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-accent" />
              Key Findings
            </h3>
            <div className="space-y-2">
              {insights.key_insights.map((insight, idx) => (
                <div key={idx} className="p-3 bg-surface-2 rounded-lg text-sm">
                  <span className="text-accent font-semibold mr-2">•</span>
                  {insight}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Watch Out */}
        {insights?.watch_out && insights.watch_out.length > 0 && (
          <div>
            <h3 className="font-heading font-semibold mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-500" />
              Watch Out
            </h3>
            <div className="space-y-2">
              {insights.watch_out.map((warning, idx) => (
                <div key={idx} className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-sm">
                  <span className="text-yellow-500 font-semibold mr-2">⚠</span>
                  {warning}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div>
            <h3 className="font-heading font-semibold mb-3 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-accent" />
              Recommendations
            </h3>
            <div className="space-y-3">
              {recommendations.map((rec) => (
                <div key={rec.rank} className="p-4 bg-surface-2 rounded-lg">
                  <div className="flex items-start gap-3 mb-2">
                    <div className="w-6 h-6 rounded-full bg-accent text-bg flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {rec.rank}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-sm mb-1">{rec.action}</div>
                      <div className="text-xs text-text-secondary space-y-1">
                        <div>Impact: <span className="text-accent">{rec.expected_impact}</span></div>
                        <div>Timeline: {rec.timeline}</div>
                        <div className="flex items-center gap-2">
                          <span>Risk:</span>
                          <span className={`
                            px-2 py-0.5 rounded text-xs
                            ${rec.risk_level === 'low' ? 'bg-green-500/20 text-green-500' : ''}
                            ${rec.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-500' : ''}
                            ${rec.risk_level === 'high' ? 'bg-red-500/20 text-red-500' : ''}
                          `}>
                            {rec.risk_level}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 bg-surface rounded-full h-1.5">
                      <div
                        className="bg-accent h-1.5 rounded-full"
                        style={{ width: `${rec.confidence}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono">{rec.confidence}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Data Quality Badge */}
        {insights?.data_quality && (
          <div className="p-3 bg-surface-2 rounded-lg text-center">
            <div className="text-xs text-text-tertiary mb-1">Data Quality</div>
            <div className={`
              inline-block px-3 py-1 rounded-full text-sm font-semibold
              ${insights.data_quality === 'high' ? 'bg-green-500/20 text-green-500' : ''}
              ${insights.data_quality === 'medium' ? 'bg-yellow-500/20 text-yellow-500' : ''}
              ${insights.data_quality === 'low' ? 'bg-red-500/20 text-red-500' : ''}
            `}>
              {insights.data_quality.toUpperCase()}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
