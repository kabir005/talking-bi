import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Upload, Database, LayoutDashboard, ArrowRight, Sparkles, X, ExternalLink } from 'lucide-react';
import { apiClient } from '../api/client';

interface Feature {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  status: string;
  route: string;
  capabilities: string[];
}

interface FeaturesData {
  features: Feature[];
  total_features: number;
  active_features: number;
  categories: Record<string, number>;
}

interface SystemStats {
  datasets: number;
  dashboards: number;
  total_rows: number;
}

export default function HomePage() {
  const [featuresData, setFeaturesData] = useState<FeaturesData | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [isSystemActive, setIsSystemActive] = useState(true);
  const [loading, setLoading] = useState(true);
  const [showFeaturesModal, setShowFeaturesModal] = useState(false);
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    // Fetch features and system status
    const fetchData = async () => {
      try {
        const [featuresRes, overviewRes] = await Promise.all([
          apiClient.get('/api/system/features'),
          apiClient.get('/api/system/overview')
        ]);
        
        setFeaturesData(featuresRes.data);
        setSystemStats(overviewRes.data.statistics);
        setIsSystemActive(overviewRes.data.system_active);
        setUptime(overviewRes.data.uptime_seconds);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setIsSystemActive(false);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getIconComponent = (_iconName: string) => {
    // Map icon names to components - simplified for now
    return <Sparkles className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-[#0A0E1A] text-white">
      {/* Header with System Status */}
      <div className="border-b border-gray-800 bg-[#0D1117]">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Talking BI</h1>
              <p className="text-xs text-gray-400">Agentic Intelligence Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {uptime > 0 && (
              <span className="text-xs text-gray-400">
                Uptime: {formatUptime(uptime)}
              </span>
            )}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isSystemActive ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              <span className="text-sm text-gray-300">{isSystemActive ? 'SYSTEM ACTIVE' : 'SYSTEM OFFLINE'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Hero Section */}
        <div className="mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-6">
            <Sparkles size={12} />
            V2.3 COGNITIVE ENGINE
          </div>
          
          <h2 className="text-5xl font-bold mb-4 leading-tight">
            Talking BI:<br />
            Your Data, Explained <span className="text-blue-400">by AI</span>
          </h2>
          
          <p className="text-gray-400 text-lg mb-8 max-w-2xl">
            Unlock deep insights through natural conversation. No complex SQL or rigid templates—just ask your data anything.
          </p>

          <div className="flex items-center gap-4">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-semibold transition-all duration-200 hover:scale-105"
            >
              Start Talking <ArrowRight size={18} />
            </Link>
            <button className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-all duration-200">
              Watch Demo
            </button>
          </div>
        </div>

        {/* Quick Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Link
            to="/upload"
            className="group p-6 bg-[#0D1117] rounded-xl border border-gray-800 hover:border-blue-500/50 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
              <Upload className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Upload Data</h3>
            <p className="text-sm text-gray-400 mb-4">
              Connect CSV, Excel, or direct SQL databases to execute with AI mapping.
            </p>
            {systemStats && (
              <div className="text-xs text-gray-500">
                {systemStats.datasets} datasets • {systemStats.total_rows.toLocaleString()} rows
              </div>
            )}
          </Link>

          <Link
            to="/datasets"
            className="group p-6 bg-[#0D1117] rounded-xl border border-gray-800 hover:border-green-500/50 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
              <Database className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Explore Datasets</h3>
            <p className="text-sm text-gray-400 mb-4">
              Browse your organization's verified data catalog and metadata layers.
            </p>
            {systemStats && (
              <div className="text-xs text-gray-500">
                {systemStats.datasets} datasets available
              </div>
            )}
          </Link>

          <Link
            to="/dashboards"
            className="group p-6 bg-[#0D1117] rounded-xl border border-gray-800 hover:border-purple-500/50 transition-all duration-300 hover:-translate-y-1"
          >
            <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
              <LayoutDashboard className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">View Dashboards</h3>
            <p className="text-sm text-gray-400 mb-4">
              Access visual reports generated through AI-driven analytical models.
            </p>
            {systemStats && (
              <div className="text-xs text-gray-500">
                {systemStats.dashboards} dashboards available
              </div>
            )}
          </Link>
        </div>

        {/* System Overview Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">PLATFORM</p>
              <h3 className="text-2xl font-bold">System Overview</h3>
            </div>
            <button
              onClick={() => setShowFeaturesModal(true)}
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
            >
              View All Features <ArrowRight size={14} />
            </button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="p-5 bg-[#0D1117] rounded-xl border border-gray-800 animate-pulse">
                  <div className="h-10 w-10 bg-gray-700 rounded-lg mb-4" />
                  <div className="h-4 bg-gray-700 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-700 rounded w-full" />
                </div>
              ))}
            </div>
          ) : featuresData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {featuresData.features.slice(0, 4).map((feature) => (
                <Link
                  key={feature.id}
                  to={feature.route}
                  className="p-5 bg-[#0D1117] rounded-xl border border-gray-800 hover:border-blue-500/50 transition-all duration-300 hover:-translate-y-1 group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                      {getIconComponent(feature.icon)}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      feature.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                    }`}>
                      {feature.status === 'active' ? 'Active' : 'Config Required'}
                    </span>
                  </div>
                  <h4 className="font-semibold mb-2 group-hover:text-blue-400 transition-colors">{feature.name}</h4>
                  <p className="text-xs text-gray-400 line-clamp-2">{feature.description}</p>
                </Link>
              ))}
            </div>
          ) : (
            <div className="p-8 bg-[#0D1117] rounded-xl border border-gray-800 text-center">
              <p className="text-gray-400">Unable to load features. Please check backend connection.</p>
            </div>
          )}

          {featuresData && (
            <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-400">
              <span>{featuresData.total_features} Total Features</span>
              <span className="w-1 h-1 rounded-full bg-gray-600" />
              <span>{featuresData.active_features} Active</span>
              <span className="w-1 h-1 rounded-full bg-gray-600" />
              <span>{Object.keys(featuresData.categories).length} Categories</span>
            </div>
          )}
        </div>
      </div>

      {/* Features Modal */}
      {showFeaturesModal && featuresData && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0D1117] rounded-xl border border-gray-800 max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-800">
              <div>
                <h3 className="text-2xl font-bold">Platform Features</h3>
                <p className="text-sm text-gray-400 mt-1">
                  {featuresData.active_features} of {featuresData.total_features} features active
                </p>
              </div>
              <button
                onClick={() => setShowFeaturesModal(false)}
                className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {featuresData.features.map((feature) => (
                  <div
                    key={feature.id}
                    className="p-5 bg-[#0A0E1A] rounded-lg border border-gray-800 hover:border-blue-500/50 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        {getIconComponent(feature.icon)}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        feature.status === 'active' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                      }`}>
                        {feature.status === 'active' ? 'Active' : 'Config Required'}
                      </span>
                    </div>
                    
                    <div className="mb-3">
                      <h4 className="font-semibold mb-1">{feature.name}</h4>
                      <p className="text-xs text-blue-400 mb-2">{feature.category}</p>
                      <p className="text-xs text-gray-400">{feature.description}</p>
                    </div>

                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-2">Capabilities:</p>
                      <ul className="space-y-1">
                        {feature.capabilities.slice(0, 3).map((cap, idx) => (
                          <li key={idx} className="text-xs text-gray-400 flex items-start gap-2">
                            <span className="text-blue-400 mt-0.5">•</span>
                            <span>{cap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <Link
                      to={feature.route}
                      onClick={() => setShowFeaturesModal(false)}
                      className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Try it now <ExternalLink size={12} />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
