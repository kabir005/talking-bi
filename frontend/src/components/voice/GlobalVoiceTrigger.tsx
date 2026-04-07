import { useState, useRef } from 'react';
import { Mic, Square, Loader, CheckCircle } from 'lucide-react';
import { transcribeAndRender, speakInsight, playBase64Audio, type VoiceInsightResult } from '../../api/voiceInsight';
import { useDashboardStore } from '../../stores/dashboardStore';
import toast from 'react-hot-toast';

type Status = 'idle' | 'recording' | 'processing' | 'done' | 'error';

export default function GlobalVoiceTrigger() {
  const [status, setStatus] = useState<Status>('idle');
  const [_transcript, setTranscript] = useState('');
  const [previewResult, setPreviewResult] = useState<VoiceInsightResult | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  const { addVoiceTile, currentDashboard } = useDashboardStore();
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingTimeoutRef = useRef<number | null>(null);

  // Get dataset ID from current dashboard
  const getDatasetId = () => {
    return currentDashboard?.dataset_id || '';
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        await processRecording();
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setStatus('recording');
      
      // Auto-stop after 15 seconds
      recordingTimeoutRef.current = setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          stopRecording();
        }
      }, 15000);
      
    } catch (error) {
      toast.error('Microphone access required');
      setStatus('idle');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current);
      }
    }
  };

  const processRecording = async () => {
    setStatus('processing');
    
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    const datasetId = getDatasetId();
    
    if (!datasetId) {
      toast.error('Load a dataset first');
      setStatus('idle');
      return;
    }
    
    try {
      const result = await transcribeAndRender(audioBlob, datasetId);
      
      if (!result.success) {
        toast.error(result.error || 'Failed to process audio');
        setStatus('error');
        setTimeout(() => setStatus('idle'), 2000);
        return;
      }
      
      setTranscript(result.transcript);
      setPreviewResult(result);
      setShowPreview(true);
      setStatus('done');
      
      toast.success(`Heard: ${result.transcript}`);
      
      // Speak summary
      if (result.summary) {
        try {
          const audioBase64 = await speakInsight(result.summary);
          playBase64Audio(audioBase64);
        } catch (error) {
          // Fail silently for TTS
        }
      }
      
      // Auto-dismiss after 8 seconds
      setTimeout(() => {
        setShowPreview(false);
        setStatus('idle');
      }, 8000);
      
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Voice query failed');
      setStatus('error');
      setTimeout(() => setStatus('idle'), 2000);
    }
  };

  const handleClick = () => {
    if (status === 'idle') {
      startRecording();
    } else if (status === 'recording') {
      stopRecording();
    }
  };

  const addToDashboard = () => {
    if (previewResult?.suggested_tile) {
      addVoiceTile(previewResult.suggested_tile);
      toast.success('Chart added to dashboard');
      setShowPreview(false);
      setStatus('idle');
    }
  };

  const getButtonClass = () => {
    const base = 'fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 cursor-pointer';
    
    switch (status) {
      case 'recording':
        return `${base} bg-red-500 animate-pulse`;
      case 'processing':
        return `${base} bg-blue-500`;
      case 'done':
        return `${base} bg-green-500`;
      case 'error':
        return `${base} bg-red-600`;
      default:
        return `${base} bg-primary hover:bg-primary/90`;
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'recording':
        return <Square size={24} className="text-white" />;
      case 'processing':
        return <Loader size={24} className="text-white animate-spin" />;
      case 'done':
        return <CheckCircle size={24} className="text-white" />;
      default:
        return <Mic size={24} className="text-white" />;
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <div
        onClick={handleClick}
        className={getButtonClass()}
        style={{ zIndex: 9999 }}
        title="Ask your data anything"
      >
        {getIcon()}
      </div>

      {/* Status Label */}
      {status === 'recording' && (
        <div
          className="fixed bottom-24 right-6 px-4 py-2 bg-red-500 text-white text-sm rounded-lg shadow-lg"
          style={{ zIndex: 9999 }}
        >
          Listening...
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && previewResult && (
        <div
          className="fixed bottom-24 right-6 w-96 bg-surface border border-border rounded-lg shadow-xl p-4 space-y-3"
          style={{ zIndex: 9999 }}
        >
          <div className="flex items-start justify-between">
            <h3 className="text-sm font-semibold text-text-primary">Voice Query Result</h3>
            <button
              onClick={() => setShowPreview(false)}
              className="text-text-secondary hover:text-text-primary"
            >
              ×
            </button>
          </div>

          <div className="text-xs text-text-secondary">
            <strong>You said:</strong> {previewResult.transcript}
          </div>

          <div className="text-sm text-text-primary">
            {previewResult.summary}
          </div>

          {previewResult.chart_config && (
            <div className="text-xs text-text-secondary">
              Chart: {previewResult.chart_config.type}
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={addToDashboard}
              className="flex-1 px-3 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary/90 transition-colors"
            >
              Add to Dashboard
            </button>
            <button
              onClick={() => setShowPreview(false)}
              className="px-3 py-2 bg-surface-elevated text-text-primary text-sm rounded-lg hover:bg-white/[0.04] transition-colors"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </>
  );
}
