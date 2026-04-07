export interface Dataset {
  id: string;
  name: string;
  source_type: string;
  row_count: number;
  column_count: number;
  schema?: Record<string, string>;
  sample?: any[];
  created_at?: string;
}

export interface Dashboard {
  id: string;
  name: string;
  dataset_id: string;
  preset: 'executive' | 'operational' | 'trend' | 'comparison';
  layout: any[];
  tiles: ChartTile[];
  filters: Record<string, any>;
  role: string;
}

export interface ChartTile {
  id: string;
  type: ChartType;
  x_column: string;
  y_column?: string;
  aggregation?: string;
  title: string;
  color_by?: string;
  filters?: any[];
  options?: Record<string, any>;
  config?: any;
}

export type ChartType = 
  | 'line' 
  | 'bar' 
  | 'area' 
  | 'pie' 
  | 'scatter' 
  | 'heatmap' 
  | 'histogram' 
  | 'waterfall' 
  | 'treemap' 
  | 'map' 
  | 'sparkline';

export interface KPI {
  label: string;
  value: number;
  change?: number;
  trend?: 'up' | 'down' | 'flat';
  sparkline?: number[];
}

export interface AgentStatus {
  name: string;
  status: 'waiting' | 'running' | 'completed' | 'error';
  duration?: number;
  output?: any;
}

export interface Insight {
  type: string;
  content: string;
  confidence: number;
  validation_status: 'validated' | 'uncertain' | 'rejected';
  caveats?: string[];
}

export interface NLQueryResult {
  success: boolean;
  query: string;
  intent: { op: string; [key: string]: any };
  result: Record<string, any>[];
  total_rows: number;
  displayed_rows: number;
  truncated: boolean;
  columns: string[];
  summary: string;
  chart_config?: ChartConfig | null;
}

export interface ChartConfig {
  type: string;
  title: string;
  data: any;
  options?: Record<string, any>;
}

export interface VoiceInsightResult {
  success: boolean;
  transcript: string;
  intent: { op: string; [key: string]: any };
  summary: string;
  chart_config: ChartConfig | null;
  result: Record<string, any>[];
  columns: string[];
  total_rows: number;
  truncated: boolean;
  suggested_tile: {
    title: string;
    source: "voice";
    chart_config: ChartConfig | null;
  };
  error?: string;
}
