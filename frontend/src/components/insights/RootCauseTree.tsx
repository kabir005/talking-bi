import React from 'react';
import { ArrowRight, AlertCircle, TrendingDown, TrendingUp } from 'lucide-react';

export interface CausalLink {
  cause: string;
  effect: string;
  confidence: number;
  evidence: string;
  impact?: 'positive' | 'negative' | 'neutral';
}

interface RootCauseTreeProps {
  causalChain: CausalLink[];
  summary?: string;
  recommendations?: string[];
}

export const RootCauseTree: React.FC<RootCauseTreeProps> = ({
  causalChain,
  summary,
  recommendations
}) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 bg-green-100';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getImpactIcon = (impact?: string) => {
    switch (impact) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {summary && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Summary</h3>
          <p className="text-sm text-blue-800">{summary}</p>
        </div>
      )}

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-gray-900">Causal Chain</h3>
        
        <div className="relative">
          {causalChain.map((link, index) => (
            <div key={index} className="relative">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full font-semibold text-sm">
                  {index + 1}
                </div>

                <div className="flex-1 space-y-3">
                  <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getImpactIcon(link.impact)}
                        <h4 className="text-sm font-semibold text-gray-900">Cause</h4>
                      </div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getConfidenceColor(link.confidence)}`}>
                        {link.confidence}% confidence
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{link.cause}</p>
                    <div className="text-xs text-gray-500">
                      <span className="font-medium">Evidence:</span> {link.evidence}
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <ArrowRight className="w-5 h-5 text-gray-400" />
                  </div>

                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">Effect</h4>
                    <p className="text-sm text-gray-700">{link.effect}</p>
                  </div>
                </div>
              </div>

              {index < causalChain.length - 1 && (
                <div className="ml-4 mb-4 border-l-2 border-dashed border-gray-300 h-8" />
              )}
            </div>
          ))}
        </div>
      </div>

      {recommendations && recommendations.length > 0 && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 className="text-sm font-semibold text-green-900 mb-3">Recommended Actions</h3>
          <ul className="space-y-2">
            {recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-green-800">
                <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-green-200 text-green-700 rounded-full text-xs font-semibold">
                  {index + 1}
                </span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
