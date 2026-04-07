// usePipelineSSE.ts — React hook for real-time pipeline progress via SSE.
// Usage: const { status, progress, error, isDone } = usePipelineSSE(datasetId)

import { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface PipelineState {
  status: string;   // idle | cleaning | schema | kpi | visualization | insights | eval | complete | failed
  progress: number; // 0-100
  error: string | null;
  isDone: boolean;
  isRunning: boolean;
}

const TERMINAL_STATES = new Set(['complete', 'failed', 'not_found', 'idle']);

const STAGE_LABELS: Record<string, string> = {
  idle: 'Waiting...',
  uploaded: 'File uploaded',
  cleaning: '🧹 Cleaning data...',
  schema: '🔍 Detecting schema...',
  kpi: '📊 Computing KPIs...',
  visualization: '📈 Building charts...',
  insights: '🧠 Generating insights...',
  eval: '✅ Validating results...',
  complete: '✅ Analysis complete!',
  failed: '❌ Pipeline failed',
  not_found: 'Dataset not found',
};

export function usePipelineSSE(datasetId: string | null): PipelineState & { label: string } {
  const [state, setState] = useState<PipelineState>({
    status: 'idle',
    progress: 0,
    error: null,
    isDone: false,
    isRunning: false,
  });

  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!datasetId) return;

    // Close any existing SSE connection
    if (esRef.current) {
      esRef.current.close();
    }

    const url = `${API_BASE}/api/pipeline/status/${datasetId}`;
    const es = new EventSource(url);
    esRef.current = es;

    es.onopen = () => {
      setState(prev => ({ ...prev, isRunning: true }));
    };

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const done = TERMINAL_STATES.has(data.status);
        setState({
          status: data.status || 'idle',
          progress: data.progress ?? 0,
          error: data.error || null,
          isDone: done,
          isRunning: !done,
        });

        if (done) {
          es.close();
          esRef.current = null;
        }
      } catch (e) {
        console.error('[SSE] Parse error:', e);
      }
    };

    es.onerror = () => {
      // EventSource auto-reconnects — log but don't crash
      console.warn('[SSE] Connection issue, auto-reconnecting...');
    };

    // Cleanup on unmount or datasetId change
    return () => {
      es.close();
      esRef.current = null;
    };
  }, [datasetId]);

  return {
    ...state,
    label: STAGE_LABELS[state.status] || state.status,
  };
}
