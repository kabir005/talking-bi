import { apiClient } from './client';

export interface BriefingConfig {
  name: string;
  dataset_id: string;
  recipients: string[];
  schedule: string;
  timezone: string;
  include_kpis: boolean;
  include_trends: boolean;
  include_anomalies: boolean;
}

export interface Briefing {
  briefing_id: string;
  name: string;
  dataset_id: string;
  dataset_name?: string;
  recipients: string[];
  schedule: string;
  timezone: string;
  include_kpis: boolean;
  include_trends: boolean;
  include_anomalies: boolean;
  created_at: string;
  next_run?: string;
}

export interface SchedulePreset {
  label: string;
  cron: string;
  description: string;
}

export async function createBriefing(config: BriefingConfig): Promise<Briefing> {
  const res = await apiClient.post('/api/briefing/briefings', config);
  return res.data;
}

export async function listBriefings(): Promise<{ briefings: Briefing[] }> {
  const res = await apiClient.get('/api/briefing/briefings');
  return res.data;
}

export async function getBriefing(briefingId: string): Promise<Briefing> {
  const res = await apiClient.get(`/api/briefing/briefings/${briefingId}`);
  return res.data;
}

export async function deleteBriefing(briefingId: string): Promise<void> {
  await apiClient.delete(`/api/briefing/briefings/${briefingId}`);
}

export async function sendBriefingNow(briefingId: string): Promise<{ success: boolean; message: string }> {
  const res = await apiClient.post(`/api/briefing/briefings/${briefingId}/send-now`);
  return res.data;
}

export async function getSchedulePresets(): Promise<{ presets: SchedulePreset[] }> {
  const res = await apiClient.get('/api/briefing/schedules/presets');
  return res.data;
}
