import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './components/shared/NotificationSystem';
import { ErrorBoundary } from './components/shared/ErrorBoundary';
import { ThemeToggle } from './components/shared/ThemeToggle';
import './styles/animations.css';

// Example usage of IntegratedDashboard
import { IntegratedDashboard } from './components/dashboard/IntegratedDashboard';

function App() {
  // In a real app, these would come from routing or state management
  const dashboardId = 'example-dashboard-id';
  const datasetId = 'example-dataset-id';

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <NotificationProvider>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 transition-colors">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg" />
                    <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                      Talking BI
                    </h1>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <ThemeToggle />
                  </div>
                </div>
              </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <IntegratedDashboard
                dashboardId={dashboardId}
                datasetId={datasetId}
                onRefresh={() => {
                  console.log('Dashboard refreshed');
                }}
              />
            </main>

            {/* Footer */}
            <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12 transition-colors">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <p className="text-center text-sm text-gray-600 dark:text-gray-400">
                  Talking BI - Agentic AI Business Intelligence Platform
                </p>
              </div>
            </footer>
          </div>
        </NotificationProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
