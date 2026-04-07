import { CheckCircle, Loader2, Circle, XCircle } from 'lucide-react';
import { AgentStatus } from '../../types';

interface AgentStatusBarProps {
  agents: AgentStatus[];
  isOpen: boolean;
  onClose: () => void;
}

export default function AgentStatusBar({ agents, isOpen, onClose }: AgentStatusBarProps) {
  if (!isOpen) return null;

  const getStatusIcon = (status: AgentStatus['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-accent animate-spin" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Circle className="w-5 h-5 text-text-tertiary" />;
    }
  };

  const completedCount = agents.filter(a => a.status === 'completed').length;
  const totalCount = agents.length;
  const progress = (completedCount / totalCount) * 100;

  return (
    <div className="fixed right-0 top-0 bottom-0 w-96 bg-surface border-l border-border shadow-2xl z-40 overflow-y-auto">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-heading text-xl font-semibold">Analyzing your data...</h2>
            <p className="text-sm text-text-secondary mt-1">
              {completedCount} of {totalCount} agents completed
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-text-tertiary hover:text-text-primary transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="w-full bg-surface-2 rounded-full h-2">
            <div
              className="bg-accent h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Agent List */}
        <div className="space-y-3">
          {agents.map((agent, idx) => (
            <div
              key={idx}
              className={`
                p-4 rounded-lg border transition-all
                ${agent.status === 'completed' ? 'bg-green-500/5 border-green-500/20' : ''}
                ${agent.status === 'running' ? 'bg-accent-dim border-accent/20' : ''}
                ${agent.status === 'error' ? 'bg-red-500/5 border-red-500/20' : ''}
                ${agent.status === 'waiting' ? 'bg-surface-2 border-border' : ''}
              `}
            >
              <div className="flex items-center gap-3">
                {getStatusIcon(agent.status)}
                <div className="flex-1">
                  <div className="font-semibold">{agent.name}</div>
                  {agent.duration && (
                    <div className="text-xs text-text-tertiary mt-1">
                      {agent.duration.toFixed(1)}s
                    </div>
                  )}
                </div>
                {agent.status === 'completed' && agent.output && (
                  <div className="text-xs text-green-500 font-mono">
                    ✓
                  </div>
                )}
              </div>
              
              {agent.status === 'running' && (
                <div className="mt-2 text-xs text-text-secondary">
                  Processing...
                </div>
              )}
              
              {agent.status === 'error' && (
                <div className="mt-2 text-xs text-red-500">
                  Failed to complete
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        {completedCount === totalCount && (
          <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="flex items-center gap-2 text-green-500 font-semibold mb-2">
              <CheckCircle className="w-5 h-5" />
              Analysis Complete
            </div>
            <p className="text-sm text-text-secondary">
              All agents have finished processing your data. Check the insights panel for results.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
