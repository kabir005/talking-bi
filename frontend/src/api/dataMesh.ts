import { apiClient } from "./client";

const BASE = "/api";

export interface JoinSuggestion {
  col_a: string;
  col_b: string;
  confidence: number;
  reason: string;
}

export interface MergeConfig {
  dataset_id_a: string;
  dataset_id_b: string;
  join_key_a: string;
  join_key_b: string;
  join_type: string;
  user_question?: string;
}

export interface Correlation {
  col_a: string;
  col_b: string;
  r: number;
  strength: string;
  direction: string;
}

export interface CrossAnalysisResult {
  success: boolean;
  merged_rows: number;
  correlations: Correlation[];
  top_correlation: Correlation | null;
  cross_chart: any;
  narrative: string;
  merged_columns: string[];
  insights?: any[];
  datasets: {
    a: { name: string; rows: number };
    b: { name: string; rows: number };
  };
  error?: string;
}

export async function suggestJoins(
  datasetIdA: string,
  datasetIdB: string
): Promise<{
  suggestions: JoinSuggestion[];
  dataset_a_name: string;
  dataset_b_name: string;
  dataset_a_cols: string[];
  dataset_b_cols: string[];
}> {
  const res = await apiClient.post(`${BASE}/data-mesh/suggest-joins`, null, {
    params: { dataset_id_a: datasetIdA, dataset_id_b: datasetIdB },
  });
  return res.data;
}

export async function analyzeCrossDataset(
  config: MergeConfig
): Promise<CrossAnalysisResult> {
  const res = await apiClient.post(`${BASE}/data-mesh/analyze`, config, {
    timeout: 60000,
  });
  return res.data;
}
