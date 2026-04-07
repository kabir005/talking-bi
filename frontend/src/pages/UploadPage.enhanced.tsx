import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, AlertCircle, Link, Database } from 'lucide-react';
import { uploadFile } from '../api/client';
import { useDatasetStore } from '../stores/datasetStore';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { UrlScraper } from '../components/upload/UrlScraper';
import { ApiConnector } from '../components/upload/ApiConnector';

type UploadMethod = 'file' | 'url' | 'api';

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [activeMethod, setActiveMethod] = useState<UploadMethod>('file');
  const addDataset = useDatasetStore((state) => state.addDataset);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setUploadResult(null);

    try {
      const result = await uploadFile(file);
      setUploadResult(result);
      addDataset(result);
      toast.success('File uploaded and cleaned successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  }, [addDataset]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
    },
    multiple: false,
  });

  const handleUrlSuccess = (result: any) => {
    setUploadResult(result);
    addDataset(result);
    toast.success('URL scraped and data extracted successfully!');
  };

  const handleApiSuccess = (result: any) => {
    setUploadResult(result);
    addDataset(result);
    toast.success('API data fetched successfully!');
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="font-heading text-4xl font-bold mb-2">Upload Data</h1>
          <p className="text-text-secondary">
            Upload files, scrape URLs, or connect to APIs. We'll automatically clean and analyze your data.
          </p>
        </div>

        {/* Method Tabs */}
        <div className="flex gap-2 border-b border-border">
          <button
            onClick={() => setActiveMethod('file')}
            className={`
              px-6 py-3 font-semibold transition-colors flex items-center gap-2
              ${activeMethod === 'file'
                ? 'text-accent border-b-2 border-accent'
                : 'text-text-secondary hover:text-text'
              }
            `}
          >
            <Upload className="w-5 h-5" />
            File Upload
          </button>
          <button
            onClick={() => setActiveMethod('url')}
            className={`
              px-6 py-3 font-semibold transition-colors flex items-center gap-2
              ${activeMethod === 'url'
                ? 'text-accent border-b-2 border-accent'
                : 'text-text-secondary hover:text-text'
              }
            `}
          >
            <Link className="w-5 h-5" />
            URL Scraper
          </button>
          <button
            onClick={() => setActiveMethod('api')}
            className={`
              px-6 py-3 font-semibold transition-colors flex items-center gap-2
              ${activeMethod === 'api'
                ? 'text-accent border-b-2 border-accent'
                : 'text-text-secondary hover:text-text'
              }
            `}
          >
            <Database className="w-5 h-5" />
            API Connector
          </button>
        </div>

        {/* File Upload */}
        {activeMethod === 'file' && (
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all
              ${isDragActive 
                ? 'border-accent bg-accent-dim' 
                : 'border-border hover:border-accent hover:bg-accent-dim/50'
              }
              ${uploading ? 'opacity-50 pointer-events-none' : ''}
            `}
          >
            <input {...getInputProps()} />
            <Upload className="w-16 h-16 text-accent mx-auto mb-4" />
            <h3 className="font-heading text-2xl font-semibold mb-2">
              {isDragActive ? 'Drop file here' : 'Drop files here'}
            </h3>
            <p className="text-text-secondary mb-4">
              CSV · XLSX · JSON
            </p>
            <p className="text-sm text-text-tertiary">
              or click to browse
            </p>
            {uploading && (
              <div className="mt-4">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
                <p className="mt-2 text-text-secondary">Processing...</p>
              </div>
            )}
          </div>
        )}

        {/* URL Scraper */}
        {activeMethod === 'url' && (
          <UrlScraper onScrapingComplete={handleUrlSuccess} />
        )}

        {/* API Connector */}
        {activeMethod === 'api' && (
          <ApiConnector onConnectionComplete={handleApiSuccess} />
        )}

        {/* Upload Result */}
        {uploadResult && (
          <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-500" />
              <h2 className="font-heading text-2xl font-semibold">Upload Successful</h2>
            </div>

            {/* Dataset Info */}
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-surface-2 rounded-lg">
                <div className="text-text-secondary text-sm mb-1">Rows</div>
                <div className="font-mono text-2xl font-semibold">{uploadResult.row_count?.toLocaleString() || 0}</div>
              </div>
              <div className="p-4 bg-surface-2 rounded-lg">
                <div className="text-text-secondary text-sm mb-1">Columns</div>
                <div className="font-mono text-2xl font-semibold">{uploadResult.column_count || 0}</div>
              </div>
              <div className="p-4 bg-surface-2 rounded-lg">
                <div className="text-text-secondary text-sm mb-1">Changes</div>
                <div className="font-mono text-2xl font-semibold">
                  {uploadResult.cleaning_report?.total_changes || 0}
                </div>
              </div>
            </div>

            {/* Cleaning Report */}
            {uploadResult.cleaning_report && uploadResult.cleaning_report.cleaning_log?.length > 0 && (
              <div>
                <h3 className="font-heading text-lg font-semibold mb-3">Cleaning Report</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {uploadResult.cleaning_report.cleaning_log.map((log: any, idx: number) => (
                    <div key={idx} className="flex items-start gap-3 p-3 bg-surface-2 rounded-lg text-sm">
                      {log.action?.includes('flag') ? (
                        <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <div className="font-semibold">{log.column || 'Dataset'}</div>
                        <div className="text-text-secondary">
                          {log.action === 'fill_missing' && 
                            `${log.pct_affected}% missing → filled with ${log.method} (${log.value_used})`
                          }
                          {log.action === 'remove_duplicates' && 
                            `${log.rows_removed} duplicate rows removed`
                          }
                          {log.action === 'fix_dtype' && 
                            `Type changed: ${log.from} → ${log.to}`
                          }
                          {log.action === 'outlier_flagged' && 
                            `${log.count} outliers detected (${log.method})`
                          }
                          {log.action === 'flag_high_missingness' && 
                            `${log.pct_missing}% missing - ${log.recommendation}`
                          }
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/datasets')}
                className="px-6 py-3 bg-accent text-bg rounded-lg font-semibold hover:bg-accent/90 transition-colors"
              >
                View Dataset
              </button>
              <button
                onClick={() => setUploadResult(null)}
                className="px-6 py-3 bg-surface-2 rounded-lg font-semibold hover:bg-surface transition-colors"
              >
                Upload Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
