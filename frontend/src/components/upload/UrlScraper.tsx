import React, { useState } from 'react';
import { Globe, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface UrlScraperProps {
  onScrapingComplete?: (datasetId: string) => void;
}

interface ScrapingResult {
  dataset_id: string;
  tables_found: number;
  rows_extracted: number;
  message: string;
}

export const UrlScraper: React.FC<UrlScraperProps> = ({ onScrapingComplete }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScrapingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScrape = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URL must start with http:// or https://');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/scrape/url', {
        url: url.trim(),
        extract_tables: true
      });

      setResult(response.data);
      
      if (response.data.dataset_id && onScrapingComplete) {
        onScrapingComplete(response.data.dataset_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to scrape URL. Please check the URL and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleScrape();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Globe className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Scrape Data from URL</h3>
      </div>

      <div className="space-y-3">
        <div>
          <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 mb-1">
            Website URL
          </label>
          <input
            id="url-input"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="https://example.com/data-table"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <p className="mt-1 text-xs text-gray-500">
            Enter a URL containing data tables. The scraper will automatically extract structured data.
          </p>
        </div>

        <button
          onClick={handleScrape}
          disabled={isLoading || !url.trim()}
          className={`
            w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium
            transition-colors
            ${isLoading || !url.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
            }
          `}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Scraping...</span>
            </>
          ) : (
            <>
              <Globe className="w-5 h-5" />
              <span>Scrape Data</span>
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-red-900">Error</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="flex items-start gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-green-900">Success!</h4>
            <p className="text-sm text-green-700 mt-1">{result.message}</p>
            <div className="mt-2 space-y-1 text-xs text-green-600">
              <div>Tables found: {result.tables_found}</div>
              <div>Rows extracted: {result.rows_extracted}</div>
              <div className="font-mono text-xs text-green-700 mt-2">
                Dataset ID: {result.dataset_id}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Tips for best results:</h4>
        <ul className="text-xs text-blue-800 space-y-1 list-disc list-inside">
          <li>Works best with pages containing HTML tables</li>
          <li>Supports JavaScript-rendered content</li>
          <li>Automatically handles pagination (up to 10 pages)</li>
          <li>Extracts structured lists and JSON-LD data</li>
        </ul>
      </div>
    </div>
  );
};
