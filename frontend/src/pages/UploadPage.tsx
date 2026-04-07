import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, AlertCircle, Link, Database, CloudUpload, FileText, X } from 'lucide-react';
import { uploadFile } from '../api/client';
import { useDatasetStore } from '../stores/datasetStore';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { UrlScraper } from '../components/upload/UrlScraper';
import { ApiConnector } from '../components/upload/ApiConnector';
import { PipelineProgressBar } from '../components/shared/PipelineProgressBar';

type UploadMethod = 'file' | 'url' | 'api';

interface StagedFile {
  file: File;
  status: 'staged' | 'uploading' | 'done' | 'error';
}

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [activeMethod, setActiveMethod] = useState<UploadMethod>('file');
  const [uploadedDatasetId, setUploadedDatasetId] = useState<string | null>(null);
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const addDataset = useDatasetStore((state) => state.addDataset);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newStaged = acceptedFiles.map(f => ({ file: f, status: 'staged' as const }));
    setStagedFiles(prev => [...prev, ...newStaged]);
  }, []);

  const handleUploadAll = async () => {
    if (stagedFiles.length === 0) return;

    const fileToUpload = stagedFiles[0];
    setUploading(true);
    setUploadResult(null);

    try {
      const result = await uploadFile(fileToUpload.file);
      setUploadResult(result);
      setUploadedDatasetId(result.dataset_id || result.id);
      addDataset(result);
      setStagedFiles(prev => prev.map((f, i) => i === 0 ? { ...f, status: 'done' as const } : f));
      toast.success('File uploaded! Running analysis...');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Upload failed');
      setStagedFiles(prev => prev.map((f, i) => i === 0 ? { ...f, status: 'error' as const } : f));
    } finally {
      setUploading(false);
    }
  };

  const removeStagedFile = (index: number) => {
    setStagedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
    },
    multiple: true,
  });

  const handleUrlSuccess = (datasetId: string) => {
    const result = { 
      id: datasetId, 
      dataset_id: datasetId, 
      name: 'URL Dataset',
      source_type: 'url' as const,
      row_count: 0, 
      column_count: 0 
    };
    setUploadResult(result);
    addDataset(result);
    toast.success('URL scraped and data extracted successfully!');
  };

  const handleApiSuccess = (datasetId: string) => {
    const result = { 
      id: datasetId, 
      dataset_id: datasetId,
      name: 'API Dataset',
      source_type: 'api' as const,
      row_count: 0, 
      column_count: 0 
    };
    setUploadResult(result);
    addDataset(result);
    toast.success('API data fetched successfully!');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
    if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
    if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(1)} KB`;
    return `${bytes} B`;
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold mb-1">Ingest Data Intelligence</h1>
          <p className="text-text-secondary text-sm max-w-2xl">
            Connect your raw data streams. Our AI Cleaning Agent will automatically normalize, type-cast, and sanitize your records in real-time.
          </p>
        </div>

        <div className="grid grid-cols-5 gap-6">
          {/* Left Column */}
          <div className="col-span-3 space-y-6">
            {/* Method Tabs */}
            <div className="flex gap-1 bg-surface-2 p-1 rounded-lg w-fit">
              {[
                { key: 'file' as const, label: 'File Upload', icon: Upload },
                { key: 'url' as const, label: 'URL Scraper', icon: Link },
                { key: 'api' as const, label: 'API Connector', icon: Database },
              ].map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveMethod(key)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-xs font-medium transition-all
                    ${activeMethod === key
                      ? 'bg-surface text-text-primary shadow-sm'
                      : 'text-text-secondary hover:text-text-primary'
                    }`}
                >
                  <Icon size={14} />
                  {label}
                </button>
              ))}
            </div>

            {/* File Upload Dropzone */}
            {activeMethod === 'file' && (
              <div
                {...getRootProps()}
                className={`
                  border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all bg-surface
                  ${isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:border-primary/30 hover:bg-white/[0.02]'
                  }
                  ${uploading ? 'opacity-50 pointer-events-none' : ''}
                `}
              >
                <input {...getInputProps()} />
                <div className="w-14 h-14 rounded-2xl bg-surface-2 border border-border flex items-center justify-center mx-auto mb-4">
                  <CloudUpload className="w-6 h-6 text-text-secondary" />
                </div>
                <h3 className="font-heading text-lg font-semibold mb-2">
                  {isDragActive ? 'Drop file here' : 'Drop files here'}
                </h3>
                <p className="text-text-secondary text-sm mb-3">
                  Or click to browse from your workstation.
                </p>
                <p className="text-xs text-text-tertiary mb-4">
                  Maximum file size: 512MB
                </p>
                <div className="flex items-center justify-center gap-2">
                  {['CSV', 'XLSX', 'JSON'].map(ext => (
                    <span key={ext} className="px-2.5 py-1 bg-surface-2 rounded text-[10px] font-mono text-text-secondary border border-border">
                      .{ext}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* URL Scraper */}
            {activeMethod === 'url' && <UrlScraper onScrapingComplete={handleUrlSuccess} />}

            {/* API Connector */}
            {activeMethod === 'api' && <ApiConnector onConnectionComplete={handleApiSuccess} />}

            {/* Staged Files */}
            {stagedFiles.length > 0 && (
              <div className="bg-surface rounded-xl border border-border p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold">
                    Staged for Upload ({stagedFiles.length})
                  </h3>
                  <button
                    onClick={() => setStagedFiles([])}
                    className="text-xs text-text-secondary hover:text-text-primary transition-colors"
                  >
                    CLEAR ALL
                  </button>
                </div>
                <div className="space-y-3">
                  {stagedFiles.map((sf, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 bg-surface-2 rounded-lg">
                      <FileText size={16} className="text-primary flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{sf.file.name}</p>
                        <p className="text-[11px] text-text-tertiary">
                          {formatFileSize(sf.file.size)} · {Math.floor(sf.file.size / 100)} Rows
                        </p>
                      </div>
                      <span className={`text-[10px] font-medium px-2 py-0.5 rounded
                        ${sf.status === 'staged' ? 'bg-primary/10 text-primary' : ''}
                        ${sf.status === 'done' ? 'bg-tertiary/10 text-tertiary' : ''}
                        ${sf.status === 'error' ? 'bg-[#FF453A]/10 text-[#FF453A]' : ''}
                      `}>
                        {sf.status.toUpperCase()}
                      </span>
                      {sf.status === 'staged' && (
                        <button onClick={() => removeStagedFile(idx)} className="text-text-tertiary hover:text-text-secondary">
                          <X size={14} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Live Pipeline Progress */}
            {uploadedDatasetId && !uploading && (
              <PipelineProgressBar
                datasetId={uploadedDatasetId}
                onComplete={() => toast.success('Analysis complete! 🎉')}
                className="mt-2"
              />
            )}

            {/* Upload Result */}
            {uploadResult && (
              <div className="bg-surface rounded-xl border border-border p-6 space-y-5">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-tertiary" />
                  <h2 className="font-heading text-lg font-semibold">Upload Successful</h2>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-surface-2 rounded-lg border border-border">
                    <div className="text-text-secondary text-xs mb-1 uppercase tracking-wider">Rows</div>
                    <div className="font-mono text-xl font-semibold">{uploadResult.row_count?.toLocaleString() || 0}</div>
                  </div>
                  <div className="p-4 bg-surface-2 rounded-lg border border-border">
                    <div className="text-text-secondary text-xs mb-1 uppercase tracking-wider">Columns</div>
                    <div className="font-mono text-xl font-semibold">{uploadResult.column_count || 0}</div>
                  </div>
                  <div className="p-4 bg-surface-2 rounded-lg border border-border">
                    <div className="text-text-secondary text-xs mb-1 uppercase tracking-wider">Changes</div>
                    <div className="font-mono text-xl font-semibold">
                      {uploadResult.cleaning_report?.total_changes || 0}
                    </div>
                  </div>
                </div>

                {uploadResult.cleaning_report && uploadResult.cleaning_report.cleaning_log?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-3">Cleaning Report</h3>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {uploadResult.cleaning_report.cleaning_log.map((log: any, idx: number) => (
                        <div key={idx} className="flex items-start gap-3 p-3 bg-surface-2 rounded-lg text-sm border border-border">
                          {log.action?.includes('flag') ? (
                            <AlertCircle className="w-4 h-4 text-[#FF9F0A] mt-0.5 flex-shrink-0" />
                          ) : (
                            <CheckCircle className="w-4 h-4 text-tertiary mt-0.5 flex-shrink-0" />
                          )}
                          <div className="flex-1">
                            <div className="font-medium text-sm">{log.column || 'Dataset'}</div>
                            <div className="text-text-secondary text-xs">
                              {log.action === 'fill_missing' && `${log.pct_affected}% missing → filled with ${log.method} (${log.value_used})`}
                              {log.action === 'remove_duplicates' && `${log.rows_removed} duplicate rows removed`}
                              {log.action === 'fix_dtype' && `Type changed: ${log.from} → ${log.to}`}
                              {log.action === 'outlier_flagged' && `${log.count} outliers detected (${log.method})`}
                              {log.action === 'flag_high_missingness' && `${log.pct_missing}% missing - ${log.recommendation}`}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => navigate('/datasets')}
                    className="px-5 py-2.5 bg-gradient-to-r from-primary to-[#5AC8FA] text-white rounded-lg text-sm font-medium hover:shadow-glow-sm transition-all"
                  >
                    View Dataset
                  </button>
                  <button
                    onClick={() => { setUploadResult(null); setStagedFiles([]); }}
                    className="px-5 py-2.5 bg-surface-2 border border-border text-text-primary rounded-lg text-sm font-medium hover:bg-surface-3 transition-colors"
                  >
                    Upload Another
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column — Cleaning Agent Panel */}
          <div className="col-span-2 space-y-5">
            {/* Cleaning Agent Card */}
            <div className="bg-surface rounded-xl border border-border p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold">Cleaning Agent</h3>
                <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-tertiary/10 text-tertiary">
                  Autonomous Mode Active
                </span>
              </div>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-tertiary mt-2 flex-shrink-0" />
                  <div className="text-xs text-text-secondary leading-relaxed">
                    <span className="font-medium text-text-primary">Detecting schema</span> for uploaded files. Columns identified: <span className="text-primary">info, types, quantity, revenue</span>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-tertiary mt-2 flex-shrink-0" />
                  <div className="text-xs text-text-secondary leading-relaxed">
                    <span className="font-medium text-text-primary">Type-casting revenue</span> from string to decimal. Handling currency symbols ($, €) automatically.
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-tertiary mt-2 flex-shrink-0" />
                  <div className="text-xs text-text-secondary leading-relaxed">
                    <span className="font-medium text-text-primary">Detected 12 missing entries</span> in uploaded data. Imputing via mean-averaging historical trends.
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-5 space-y-3">
                <button
                  onClick={handleUploadAll}
                  disabled={stagedFiles.length === 0 || uploading}
                  className="w-full py-2.5 bg-gradient-to-r from-tertiary to-[#30D158] text-white rounded-lg text-sm font-medium hover:shadow-[0_0_20px_rgba(52,199,89,0.2)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Processing...' : 'Confirm & Start Ingestion'}
                </button>
                <button className="w-full py-2 text-center text-xs text-text-secondary hover:text-text-primary transition-colors">
                  View Full Cleaning Log
                </button>
              </div>
            </div>

            {/* Ingestion Estimates */}
            <div className="bg-surface rounded-xl border border-border p-5">
              <span className="text-xs text-text-secondary uppercase tracking-wider font-medium">Ingestion Estimates</span>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <div className="font-mono text-2xl font-bold">1.6M</div>
                  <div className="text-[10px] text-text-tertiary uppercase mt-0.5">Total Rows</div>
                </div>
                <div>
                  <div className="font-mono text-2xl font-bold text-primary">~45s</div>
                  <div className="text-[10px] text-text-tertiary uppercase mt-0.5">Proc. Time</div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <div className="progress-bar flex-1">
                    <div className="progress-bar__fill progress-bar__fill--primary" style={{ width: '72%' }} />
                  </div>
                </div>
                <p className="text-[10px] text-text-tertiary mt-2">Resource utilization: High intensity</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
