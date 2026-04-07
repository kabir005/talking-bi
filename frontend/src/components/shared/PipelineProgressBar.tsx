// PipelineProgressBar.tsx — Real-time pipeline progress display component.
// Shows animated progress bar + stage label during dataset analysis.

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { usePipelineSSE } from '../../hooks/usePipelineSSE';
import { useNavigate } from 'react-router-dom';

interface PipelineProgressBarProps {
  datasetId: string | null;
  onComplete?: () => void;                    // fires when pipeline reaches 100%
  navigateToDashboard?: boolean;              // auto-navigate on complete
  dashboardId?: string;                       // target dashboard for navigation
  className?: string;
}

const STAGE_COLORS: Record<string, string> = {
  cleaning: 'from-blue-500 to-cyan-500',
  schema: 'from-purple-500 to-blue-500',
  kpi: 'from-pink-500 to-purple-500',
  visualization: 'from-orange-500 to-pink-500',
  insights: 'from-green-500 to-teal-500',
  eval: 'from-teal-500 to-green-400',
  complete: 'from-green-400 to-emerald-500',
  failed: 'from-red-500 to-red-700',
};

export function PipelineProgressBar({
  datasetId,
  onComplete,
  navigateToDashboard,
  dashboardId,
  className = '',
}: PipelineProgressBarProps) {
  const navigate = useNavigate();
  const { status, progress, error, isDone, isRunning, label } = usePipelineSSE(datasetId);

  useEffect(() => {
    if (status === 'complete') {
      onComplete?.();
      if (navigateToDashboard && dashboardId) {
        setTimeout(() => navigate(`/dashboard/${dashboardId}`), 1200);
      }
    }
  }, [status]);

  if (!datasetId || (isDone && status === 'idle')) return null;

  const gradientClass = STAGE_COLORS[status] || 'from-indigo-500 to-purple-500';
  const isFailed = status === 'failed';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        className={`rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md p-5 ${className}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {isFailed ? (
              <XCircle className="w-5 h-5 text-red-400" />
            ) : isDone ? (
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            ) : (
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            )}
            <span className="text-sm font-semibold text-white">
              {isFailed ? 'Analysis Failed' : isDone ? 'Analysis Complete' : 'Analyzing Dataset'}
            </span>
          </div>
          <span className="text-xs font-mono text-white/60">{progress}%</span>
        </div>

        {/* Progress bar track */}
        <div className="h-2.5 w-full bg-white/10 rounded-full overflow-hidden mb-3">
          <motion.div
            className={`h-full rounded-full bg-gradient-to-r ${gradientClass}`}
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        {/* Stage label */}
        <motion.p
          key={label}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-white/70"
        >
          {label}
        </motion.p>

        {/* Error message */}
        {isFailed && error && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2"
          >
            {error}
          </motion.p>
        )}

        {/* Stage dots */}
        {isRunning && (
          <div className="mt-3 flex gap-1.5 flex-wrap">
            {['cleaning', 'schema', 'kpi', 'visualization', 'insights', 'eval'].map((stage) => {
              const stageProgress: Record<string, number> = {
                cleaning: 15, schema: 25, kpi: 45,
                visualization: 60, insights: 75, eval: 90,
              };
              const reached = progress >= stageProgress[stage];
              return (
                <div
                  key={stage}
                  className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                    reached ? `bg-gradient-to-r ${gradientClass}` : 'bg-white/10'
                  }`}
                />
              );
            })}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
