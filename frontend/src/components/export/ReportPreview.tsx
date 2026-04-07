import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, FileText, Download, Eye, Calendar, BarChart3 } from 'lucide-react';

interface ReportMetadata {
  report_id: string;
  file_path: string;
  format: string;
  dashboard_id: string;
  dataset_name: string;
  generated_at: string;
  page_count?: number;
  slide_count?: number;
  charts_embedded: number;
}

interface ReportPreviewProps {
  dashboardId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ReportPreview: React.FC<ReportPreviewProps> = ({ 
  dashboardId, 
  isOpen, 
  onClose 
}) => {
  const [generating, setGenerating] = useState(false);
  const [pdfReport, setPdfReport] = useState<ReportMetadata | null>(null);
  const [pptxReport, setPptxReport] = useState<ReportMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      generateReports();
    }
  }, [isOpen, dashboardId]);

  const generateReports = async () => {
    try {
      setGenerating(true);
      setError(null);

      const response = await axios.post('/api/reports/generate', {
        dashboard_id: dashboardId,
        format: 'both'
      });

      setPdfReport(response.data.pdf);
      setPptxReport(response.data.pptx);
    } catch (err: any) {
      console.error('Error generating reports:', err);
      setError(err.response?.data?.detail || 'Failed to generate reports');
    } finally {
      setGenerating(false);
    }
  };

  const downloadReport = async (reportId: string, format: 'pdf' | 'pptx') => {
    try {
      const response = await axios.get(`/api/reports/${reportId}/${format}`, {
        responseType: 'blob'
      });

      const mimeType = format === 'pdf' 
        ? 'application/pdf' 
        : 'application/vnd.openxmlformats-officedocument.presentationml.presentation';

      const blob = new Blob([response.data], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading report:', err);
      alert('Failed to download report');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-600" />
            Report Preview
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          {generating ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
              <div className="text-lg font-medium text-gray-800">Generating Reports...</div>
              <div className="text-sm text-gray-600 mt-2">This may take a few moments</div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-red-500 text-lg font-medium mb-2">Error</div>
              <div className="text-gray-600">{error}</div>
              <button
                onClick={generateReports}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* PDF Report Card */}
              {pdfReport && (
                <div className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-red-100 rounded-lg">
                        <FileText className="w-8 h-8 text-red-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">PDF Report</h3>
                        <p className="text-sm text-gray-600">Professional business report</p>
                      </div>
                    </div>
                    <button
                      onClick={() => downloadReport(pdfReport.report_id, 'pdf')}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Download PDF
                    </button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Pages</div>
                      <div className="text-lg font-semibold text-gray-800">
                        {pdfReport.page_count || 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Charts</div>
                      <div className="text-lg font-semibold text-gray-800">
                        {pdfReport.charts_embedded}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Dataset</div>
                      <div className="text-sm font-semibold text-gray-800 truncate">
                        {pdfReport.dataset_name}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Generated</div>
                      <div className="text-sm font-semibold text-gray-800">
                        {new Date(pdfReport.generated_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-2">Report Contents</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>✓ Cover page with branding</li>
                      <li>✓ Executive summary</li>
                      <li>✓ KPI table with indicators</li>
                      <li>✓ {pdfReport.charts_embedded} embedded charts</li>
                      <li>✓ Key insights and recommendations</li>
                      <li>✓ Data appendix</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* PowerPoint Report Card */}
              {pptxReport && (
                <div className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-orange-100 rounded-lg">
                        <BarChart3 className="w-8 h-8 text-orange-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">PowerPoint Presentation</h3>
                        <p className="text-sm text-gray-600">Executive presentation slides</p>
                      </div>
                    </div>
                    <button
                      onClick={() => downloadReport(pptxReport.report_id, 'pptx')}
                      className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Download PPTX
                    </button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Slides</div>
                      <div className="text-lg font-semibold text-gray-800">
                        {pptxReport.slide_count || 'N/A'}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Charts</div>
                      <div className="text-lg font-semibold text-gray-800">
                        {pptxReport.charts_embedded}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Dataset</div>
                      <div className="text-sm font-semibold text-gray-800 truncate">
                        {pptxReport.dataset_name}
                      </div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-600 mb-1">Generated</div>
                      <div className="text-sm font-semibold text-gray-800">
                        {new Date(pptxReport.generated_at).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <h4 className="font-semibold text-orange-900 mb-2">Presentation Contents</h4>
                    <ul className="text-sm text-orange-800 space-y-1">
                      <li>✓ Title slide with branding</li>
                      <li>✓ Executive summary slide</li>
                      <li>✓ KPI dashboard table</li>
                      <li>✓ {pptxReport.charts_embedded} chart slides</li>
                      <li>✓ Recommendations slide</li>
                      <li>✓ Corporate blue/white theme</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Info Box */}
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start gap-3">
                  <Eye className="w-5 h-5 text-gray-600 mt-0.5" />
                  <div className="text-sm text-gray-700">
                    <p className="font-medium mb-1">About These Reports</p>
                    <p>
                      Reports are generated from your dashboard data and include all insights, 
                      KPIs, charts, and recommendations. PDF reports are ideal for sharing via 
                      email, while PowerPoint presentations are perfect for meetings and presentations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4" />
            <span>Generated: {new Date().toLocaleString()}</span>
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
