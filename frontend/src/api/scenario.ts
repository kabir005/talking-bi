import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface SliderParam {
  column: string;
  label: string;
  change_pct: number;
  change_type: "multiply" | "add" | "set";
}

export interface ScenarioRequest {
  dataset_id: string;
  parameters: SliderParam[];
  target_columns?: string[];
}

export interface ScenarioResult {
  baseline_kpis: Record<string, any>;
  projected_kpis: Record<string, any>;
  delta_kpis: Record<string, number>;
  chart_configs: any[];
  narrative: string;
}

export interface ParameterConfig {
  column: string;
  label: string;
  min_pct: number;
  max_pct: number;
  default_pct: number;
  step: number;
  current_mean: number;
  change_type: string;
}

export async function getScenarioParameters(datasetId: string): Promise<{
  parameters: ParameterConfig[];
  watch_columns: string[];
  note: string;
}> {
  const res = await axios.get(`${BASE}/scenario/parameters/${datasetId}`);
  return res.data;
}

export async function simulateScenario(request: ScenarioRequest): Promise<ScenarioResult> {
  const res = await axios.post(`${BASE}/scenario/simulate`, request);
  return res.data;
}
