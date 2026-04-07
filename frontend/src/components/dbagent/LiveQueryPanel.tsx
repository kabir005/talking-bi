import { useState, useEffect } from 'react';
import { Play, Loader, Database, FileText, CheckCircle } from 'lucide-react';
import { executeNLQuery, getSchema, Schema } from '../../api/dbAgent';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

interface LiveQueryPanelProps {
  connectionId: string;
}

export default function LiveQueryPanel({ connectionId }: LiveQueryPanelProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [schema, setSchema] = useState<Schema | null>(null);
  const [loadingSchema, setLoadingSchema] = useState(false);

  useEffect(() => {
    if (connectionId) {
      loadSchema();
    }
  }, [connectionId]);

  const loadSchema = async () => {
    setLoadingSchema(true);
    try {
      const data = await getSchema(connectionId);
      setSchema(data);
    } catch (error) {
      console.error('Failed to load schema:', error);
    } finally {
      setLoadingSchema(false);
    }
  };

  const handleExecute = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setExecuting(true);
    setResult(null);

    try {
      const data = await executeNLQuery({
        connection_id: connectionId,
        natural_language_query: query
      });
      
      setResult(data);
      toast.success(data.message);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Query execution failed';
      toast.error(errorMessage, { duration: 6000 });
      
      // If it's a validation error about tables, show the schema panel
      if (errorMessage.includes('references tables that don\'t exist') || 
          errorMessage.includes('Cannot answer this query')) {
        toast('💡 Check the available tables above', { 
          icon: '📊',
          duration: 4000 
        });
      }
    } finally {
      setExecuting(false);
    }
  };

  const handleCreateDashboard = () => {
    if (result?.dataset_id) {
      navigate(`/dashboard/${result.dataset_id}`);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2 text-text-primary">
          <FileText className="w-5 h-5" />
          Natural Language Query
        </h3>
        {schema && (
          <div className="text-sm text-text-secondary">
            {schema.table_count} tables available
          </div>
        )}
      </div>

      {loadingSchema ? (
        <div className="flex items-center justify-center py-8">
          <Loader className="w-6 h-6 animate-spin text-accent" />
          <span className="ml-2 text-text-secondary">Loading schema...</span>
        </div>
      ) : schema && schema.table_count === 0 ? (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
          <div className="text-sm text-yellow-600 dark:text-yellow-400">
            ⚠️ No tables found in this database. Please check your connection or add some data first.
          </div>
        </div>
      ) : (
        <>
          {/* Show available tables first with example queries */}
          {schema && schema.table_count > 0 && (
            <div className="bg-accent/10 border border-accent/20 rounded-lg p-4">
              <div className="text-sm font-medium mb-2 text-text-primary">💡 Available Tables & Example Queries:</div>
              <div className="space-y-2">
                {Object.entries(schema.schema).slice(0, 5).map(([table, columns]) => (
                  <details key={table} className="bg-surface-elevated rounded-lg border border-border">
                    <summary className="px-3 py-2 cursor-pointer font-medium text-sm hover:bg-white/[0.04] text-text-primary">
                      📊 {table} ({columns.length} columns)
                    </summary>
                    <div className="px-3 pb-2 space-y-2">
                      <div className="text-xs text-text-secondary space-y-1">
                        {columns.slice(0, 8).map((col) => (
                          <div key={col.name} className="flex justify-between">
                            <span>{col.name}</span>
                            <span className="text-text-tertiary">{col.type}</span>
                          </div>
                        ))}
                        {columns.length > 8 && (
                          <div className="text-text-tertiary">+{columns.length - 8} more columns...</div>
                        )}
                      </div>
                      <div className="pt-2 border-t border-border">
                        <div className="text-xs font-medium text-accent mb-1">Try asking:</div>
                        <button
                          onClick={() => setQuery(`Show me all data from ${table}`)}
                          className="text-xs text-text-secondary hover:text-accent cursor-pointer block mb-1"
                        >
                          • "Show me all data from {table}"
                        </button>
                        <button
                          onClick={() => setQuery(`Show me the first 10 rows from ${table}`)}
                          className="text-xs text-text-secondary hover:text-accent cursor-pointer block"
                        >
                          • "Show me the first 10 rows from {table}"
                        </button>
                      </div>
                    </div>
                  </details>
                ))}
                {Object.keys(schema.schema).length > 5 && (
                  <p className="text-xs text-text-secondary px-3">
                    +{Object.keys(schema.schema).length - 5} more tables...
                  </p>
                )}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2 text-text-primary">
              Ask a question about your data
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg resize-none bg-surface text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              rows={3}
              placeholder={schema && Object.keys(schema.schema).length > 0 
                ? `e.g., Show me all records from ${Object.keys(schema.schema)[0]}`
                : "e.g., Show me the top 10 rows"}
            />
            <p className="text-xs text-text-secondary mt-1">
              💡 Tip: Click example queries above or use the table names shown
            </p>
          </div>

          <button
            onClick={handleExecute}
            disabled={executing || !query.trim()}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-accent text-bg rounded-lg hover:bg-accent/90 disabled:opacity-50 transition-colors"
          >
            {executing ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Execute Query
              </>
            )}
          </button>

          {result && (
            <div className="space-y-4">
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-medium text-text-primary">Query Successful</div>
                    <div className="text-sm text-text-secondary mt-1">{result.explanation}</div>
                  </div>
                </div>
              </div>

              <div className="bg-surface-elevated p-4 rounded-lg border border-border">
                <div className="text-sm font-medium text-text-primary mb-2">Generated SQL:</div>
                <pre className="text-xs bg-surface p-3 rounded border border-border overflow-x-auto text-text-primary">
                  {result.sql}
                </pre>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
                  <div className="text-sm text-blue-500 font-medium">Rows</div>
                  <div className="text-2xl font-bold text-text-primary">{result.rows}</div>
                </div>
                <div className="bg-purple-500/10 p-3 rounded-lg border border-purple-500/20">
                  <div className="text-sm text-purple-500 font-medium">Columns</div>
                  <div className="text-2xl font-bold text-text-primary">{result.columns.length}</div>
                </div>
                <div className="bg-green-500/10 p-3 rounded-lg border border-green-500/20">
                  <div className="text-sm text-green-500 font-medium">Dataset</div>
                  <div className="text-xs font-medium text-text-primary mt-1">Created</div>
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2 text-text-primary">Preview (first 10 rows):</div>
                <div className="overflow-x-auto border border-border rounded-lg">
                  <table className="min-w-full divide-y divide-border">
                    <thead className="bg-surface-elevated">
                      <tr>
                        {result.columns.map((col: string) => (
                          <th
                            key={col}
                            className="px-4 py-2 text-left text-xs font-medium text-text-secondary uppercase"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-surface divide-y divide-border">
                      {result.preview.map((row: any, idx: number) => (
                        <tr key={idx}>
                          {result.columns.map((col: string) => (
                            <td key={col} className="px-4 py-2 text-sm text-text-primary">
                              {row[col] !== null ? String(row[col]) : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <button
                onClick={handleCreateDashboard}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Database className="w-4 h-4" />
                Create Dashboard from Results
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
