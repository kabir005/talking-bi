import React, { useState } from 'react';
import { apiClient } from '../../api/client';
import { Download, FileJson, FileImage, FileText, Package, CheckCircle } from 'lucide-react';

interface ExportMenuProps {
  dashboardId: string;
  datasetId: string;
  onExportComplete?: (result: any) => void;
}

export const ExportMenu: React.FC<ExportMenuProps> = ({ 
  dashboardId, 
  datasetId,
  onExportComplete 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleExport = async (type: string) => {
    setExportType(type);
    setExporting(true);
    setSuccess(false);

    try {
      let result;

      switch (type) {
        case 'dashboard-json':
          result = await exportDashboardJSON();
          break;
        case 'chart-png':
          result = await exportChartPNG();
          break;
        case 'data-csv':
          result = await exportDataCSV();
          break;
        case 'bundle':
          result = await exportBundle();
          break;
        case 'pdf':
          result = await exportPDF();
          break;
        case 'pptx':
          result = await exportPPTX();
          break;
        default:
          throw new Error('Unknown export type');
      }

      setSuccess(true);
      
      if (onExportComplete) {
        onExportComplete(result);
      }

      setTimeout(() => {
        setSuccess(false);
        setIsOpen(false);
      }, 2000);
    } catch (error: any) {
      console.error('Export error:', error);
      alert(`Export failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExporting(false);
      setExportType(null);
    }
  };

  const exportDashboardJSON = async () => {
    const response = await apiClient.post('/api/export-v2/dashboard/json', {
      dashboard_id: dashboardId,
      include_data: false
    });

    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard_${dashboardId}.json`;
    a.click();
    URL.revokeObjectURL(url);

    return response.data;
  };

  const exportChartPNG = async () => {
    // This would need chart data from the dashboard
    // For now, show a message
    alert('Chart PNG export: Select a specific chart to export');
    return null;
  };

  const exportDataCSV = async () => {
    const response = await apiClient.post('/api/export-v2/data/csv', {
      dataset_id: datasetId
    }, {
      responseType: 'blob'
    });

    const blob = new Blob([response.data], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data_${datasetId}.csv`;
    a.click();
    URL.revokeObjectURL(url);

    return { success: true };
  };

  const exportBundle = async () => {
    const response = await apiClient.post('/api/export-v2/dashboard/bundle', {
      dashboard_id: dashboardId
    });

    alert(`Bundle exported successfully!\nLocation: ${response.data.export_dir}\nFiles: ${response.data.chart_count} charts + dashboard JSON + data CSV`);
    
    return response.data;
  };

  const exportPDF = async () => {
    const response = await apiClient.post('/api/reports/generate', {
      dashboard_id: dashboardId,
      format: 'pdf'
    });

    const reportId = response.data.pdf.report_id;
    
    // Download PDF
    const pdfResponse = await apiClient.get(`/api/reports/${reportId}/pdf`, {
      responseType: 'blob'
    });

    const blob = new Blob([pdfResponse.data], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${reportId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);

    return response.data;
  };

  const exportPPTX = async () => {
    const response = await apiClient.post('/api/reports/generate', {
      dashboard_id: dashboardId,
      format: 'pptx'
    });

    const reportId = response.data.pptx.report_id;
    
    // Download PowerPoint
    const pptxResponse = await apiClient.get(`/api/reports/${reportId}/pptx`, {
      responseType: 'blob'
    });

    const blob = new Blob([pptxResponse.data], { 
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${reportId}.pptx`;
    a.click();
    URL.revokeObjectURL(url);

    return response.data;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Download className="w-5 h-5" />
        Export
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-800">Export Options</h3>
              <p className="text-xs text-gray-600 mt-1">Choose export format</p>
            </div>

            <div className="p-2">
              {/* Dashboard JSON */}
              <button
                onClick={() => handleExport('dashboard-json')}
                disabled={exporting}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left disabled:opacity-50"
              >
                <FileJson className="w-5 h-5 text-blue-600" />
                <div className="flex-1">
                  <div className="font-medium text-gray-800">Dashboard JSON</div>
                  <div className="text-xs text-gray-600">Configuration only</div>
                </div>
                {exporting && exportType === 'dashboard-json' && (
                  <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                )}
                {success && exportType === 'dashboard-json' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </button>

              {/* Data CSV */}
              <button
                onClick={() => handleExport('data-csv')}
                disabled={exporting}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left disabled:opacity-50"
              >
                <FileText className="w-5 h-5 text-green-600" />
                <div className="flex-1">
                  <div className="font-medium text-gray-800">Data CSV</div>
                  <div className="text-xs text-gray-600">Raw data export</div>
                </div>
                {exporting && exportType === 'data-csv' && (
                  <div className="w-5 h-5 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
                )}
                {success && exportType === 'data-csv' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </button>

              {/* PDF Report */}
              <button
                onClick={() => handleExport('pdf')}
                disabled={exporting}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left disabled:opacity-50"
              >
                <FileText className="w-5 h-5 text-red-600" />
                <div className="flex-1">
                  <div className="font-medium text-gray-800">PDF Report</div>
                  <div className="text-xs text-gray-600">Professional report</div>
                </div>
                {exporting && exportType === 'pdf' && (
                  <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                )}
                {success && exportType === 'pdf' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </button>

              {/* PowerPoint Report */}
              <button
                onClick={() => handleExport('pptx')}
                disabled={exporting}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left disabled:opacity-50"
              >
                <FileImage className="w-5 h-5 text-orange-600" />
                <div className="flex-1">
                  <div className="font-medium text-gray-800">PowerPoint</div>
                  <div className="text-xs text-gray-600">Presentation slides</div>
                </div>
                {exporting && exportType === 'pptx' && (
                  <div className="w-5 h-5 border-2 border-orange-600 border-t-transparent rounded-full animate-spin" />
                )}
                {success && exportType === 'pptx' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </button>

              {/* Complete Bundle */}
              <button
                onClick={() => handleExport('bundle')}
                disabled={exporting}
                className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors text-left disabled:opacity-50"
              >
                <Package className="w-5 h-5 text-purple-600" />
                <div className="flex-1">
                  <div className="font-medium text-gray-800">Complete Bundle</div>
                  <div className="text-xs text-gray-600">All files + charts</div>
                </div>
                {exporting && exportType === 'bundle' && (
                  <div className="w-5 h-5 border-2 border-purple-600 border-t-transparent rounded-full animate-spin" />
                )}
                {success && exportType === 'bundle' && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </button>
            </div>

            <div className="p-3 border-t border-gray-200 bg-gray-50 rounded-b-lg">
              <p className="text-xs text-gray-600">
                Exports are saved to your downloads folder
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
