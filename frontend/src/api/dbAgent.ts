import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || '';

export interface ConnectionConfig {
  name: string;
  db_type: 'postgresql' | 'mysql' | 'sqlite';
  host?: string;
  port?: number;
  database: string;
  username?: string;
  password?: string;
  ssl?: boolean;
}

export interface Connection {
  connection_id: string;
  name: string;
  db_type: string;
  database: string;
  host?: string;
}

export interface SchemaColumn {
  name: string;
  type: string;
}

export interface Schema {
  schema: Record<string, SchemaColumn[]>;
  table_count: number;
}

export interface QueryRequest {
  connection_id: string;
  natural_language_query: string;
}

export interface QueryResult {
  success: boolean;
  sql: string;
  explanation: string;
  dataset_id: string;
  rows: number;
  columns: string[];
  preview: Record<string, any>[];
  message: string;
}

export async function testConnection(config: ConnectionConfig): Promise<{ success: boolean; message: string }> {
  const res = await axios.post(`${BASE}/api/db-agent/connections/test`, { config });
  return res.data;
}

export async function createConnection(config: ConnectionConfig): Promise<Connection> {
  const res = await axios.post(`${BASE}/api/db-agent/connections`, config);
  return res.data;
}

export async function listConnections(): Promise<{ connections: Connection[] }> {
  const res = await axios.get(`${BASE}/api/db-agent/connections`);
  return res.data;
}

export async function deleteConnection(connectionId: string): Promise<void> {
  await axios.delete(`${BASE}/api/db-agent/connections/${connectionId}`);
}

export async function getSchema(connectionId: string): Promise<Schema> {
  const res = await axios.get(`${BASE}/api/db-agent/schema/${connectionId}`);
  return res.data;
}

export async function executeNLQuery(request: QueryRequest): Promise<QueryResult> {
  const res = await axios.post(`${BASE}/api/db-agent/query`, request);
  return res.data;
}
