import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './contexts/ThemeContext';
import { ErrorBoundary } from './components/shared/ErrorBoundary';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import DatasetsPage from './pages/DatasetsPage';
import DashboardPage from './pages/DashboardPage';
import DashboardsPage from './pages/DashboardsPage';
import MLModelsPage from './pages/MLModelsPage';
import ForecastPage from './pages/ForecastPage';
import AlertsPage from './pages/AlertsPage';
import DatasetDiffPage from './pages/DatasetDiffPage';
import DataMeshPage from './pages/DataMeshPage';
import DatabaseAgentPage from './pages/DatabaseAgentPage';
import BriefingPage from './pages/BriefingPage';
import SettingsPage from './pages/SettingsPage';
import './styles/animations.css';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <Router>
          <Toaster 
            position="top-right"
            toastOptions={{
              style: {
                background: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
              },
            }}
          />
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="upload" element={<UploadPage />} />
              <Route path="datasets" element={<DatasetsPage />} />
              <Route path="dashboards" element={<DashboardsPage />} />
              <Route path="dashboard/:id" element={<DashboardPage />} />
              <Route path="ml" element={<MLModelsPage />} />
              <Route path="forecast" element={<ForecastPage />} />
              <Route path="alerts" element={<AlertsPage />} />
              <Route path="dataset-diff" element={<DatasetDiffPage />} />
              <Route path="data-mesh" element={<DataMeshPage />} />
              <Route path="database-agent" element={<DatabaseAgentPage />} />
              <Route path="briefing" element={<BriefingPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
