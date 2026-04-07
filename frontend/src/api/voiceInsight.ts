import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "/api";

export interface VoiceInsightResult {
  success: boolean;
  transcript: string;
  intent: { op: string; [key: string]: any };
  summary: string;
  chart_config: any | null;
  result: Record<string, any>[];
  columns: string[];
  total_rows: number;
  truncated: boolean;
  suggested_tile: {
    title: string;
    source: "voice";
    chart_config: any | null;
  };
  error?: string;
}

export async function transcribeAndRender(
  audioBlob: Blob,
  datasetId: string
): Promise<VoiceInsightResult> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "voice.webm");
  formData.append("dataset_id", datasetId);

  const res = await axios.post(`${BASE}/voice-insight/transcribe-and-render`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 60000,
  });

  return res.data;
}

export async function speakInsight(text: string): Promise<string> {
  // Returns base64 WAV audio string
  const res = await axios.post(`${BASE}/voice-insight/speak-insight`, null, {
    params: { text: text.slice(0, 800) },
    timeout: 30000,
  });

  return res.data.audio_base64;
}

// Helper: play base64 WAV in browser
export function playBase64Audio(base64: string): void {
  const audio = new Audio(`data:audio/wav;base64,${base64}`);
  audio.play().catch(() => {}); // Ignore autoplay restrictions gracefully
}
