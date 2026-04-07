import { apiClient } from './client';

export interface Dataset {
  id: string;
  name: string;
  source_type: string;
  row_count: number;
  column_count: number;
  created_at: string;
}

export interface DatasetDetail extends Dataset {
  source_path: string;
  schema: Record<string, any>;
  sample: any[];
  cleaning_log: string;
}

export interface DatasetPreview {
  columns: string[];
  data: Record<string, any>[];
  total_rows: number;
}

export const listDatasets = async (): Promise<Dataset[]> => {
  const response = await apiClient.get('/api/datasets');
  return response.data;
};

export const getDataset = async (datasetId: string): Promise<DatasetDetail> => {
  const response = await apiClient.get(`/api/datasets/${datasetId}`);
  return response.data;
};

export const previewDataset = async (
  datasetId: string,
  limit: number = 50
): Promise<DatasetPreview> => {
  const response = await apiClient.get(`/api/datasets/${datasetId}/preview`, {
    params: { limit }
  });
  return response.data;
};

export const getDatasetData = async (
  datasetId: string,
  limit: number = 100
): Promise<{ columns: string[]; rows: Record<string, any>[]; total_rows: number }> => {
  const response = await apiClient.get(`/api/datasets/${datasetId}/data`, {
    params: { limit }
  });
  return response.data;
};

export const deleteDataset = async (datasetId: string): Promise<void> => {
  await apiClient.delete(`/api/datasets/${datasetId}`);
};

export const removeOutliers = async (datasetId: string): Promise<{ message: string; new_row_count: number }> => {
  const response = await apiClient.post(`/api/datasets/${datasetId}/remove-outliers`);
  return response.data;
};

export const dropColumn = async (
  datasetId: string,
  columnName: string
): Promise<{ message: string }> => {
  const response = await apiClient.post(`/api/datasets/${datasetId}/drop-column`, null, {
    params: { column_name: columnName }
  });
  return response.data;
};
