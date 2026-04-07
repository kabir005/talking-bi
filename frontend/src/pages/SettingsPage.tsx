import { useState, useEffect } from 'react';
import { Settings, Shield, Cloud, Server, CheckCircle, XCircle, Loader } from 'lucide-react';
import { getLLMStatus, getPrivacyMode, testLLM, listOllamaModels } from '../api/client';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const [llmStatus, setLlmStatus] = useState<any>(null);
  const [privacyMode, setPrivacyMode] = useState<any>(null);
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [status, privacy] = await Promise.all([
        getLLMStatus(),
        getPrivacyMode()
      ]);
      
      setLlmStatus(status);
      setPrivacyMode(privacy);

      // Load Ollama models if available
      if (status.ollama?.available) {
        try {
          const models = await listOllamaModels();
          setOllamaModels(models.models || []);
        } catch (error) {
          console.error('Failed to load Ollama models:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const runTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testLLM('Say hello in one sentence.');
      setTestResult(result);
      toast.success('LLM test successful');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'LLM test failed');
      setTestResult({ success: false, error: error.message });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="animate-spin text-primary" size={32} />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-heading font-bold text-text-primary">Settings</h1>
        <p className="text-sm text-text-secondary mt-1">
          Configure LLM providers and privacy settings
        </p>
      </div>

      {/* Privacy Mode Status */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Shield size={24} className={privacyMode?.privacy_mode_enabled ? 'text-green-500' : 'text-gray-500'} />
          <div>
            <h2 className="text-lg font-semibold text-text-primary">Privacy Mode</h2>
            <p className="text-sm text-text-secondary">
              {privacyMode?.description}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className={`px-3 py-1.5 rounded-full text-sm font-medium ${
            privacyMode?.privacy_mode_enabled 
              ? 'bg-green-500/10 text-green-500' 
              : 'bg-gray-500/10 text-gray-500'
          }`}>
            {privacyMode?.privacy_mode_enabled ? 'Enabled' : 'Disabled'}
          </div>
          {privacyMode?.using_local_llm && (
            <div className="px-3 py-1.5 rounded-full text-sm font-medium bg-blue-500/10 text-blue-500">
              Using Local LLM
            </div>
          )}
        </div>
      </div>

      {/* LLM Providers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Groq (Cloud) */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Cloud size={24} className={llmStatus?.groq?.available ? 'text-blue-500' : 'text-gray-500'} />
            <div>
              <h3 className="text-lg font-semibold text-text-primary">Groq (Cloud)</h3>
              <p className="text-xs text-text-secondary">Cloud-based LLM API</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-text-secondary">Status</span>
              <div className="flex items-center gap-2">
                {llmStatus?.groq?.available ? (
                  <>
                    <CheckCircle size={16} className="text-green-500" />
                    <span className="text-sm text-green-500">Available</span>
                  </>
                ) : (
                  <>
                    <XCircle size={16} className="text-red-500" />
                    <span className="text-sm text-red-500">Not Configured</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-text-secondary">Current Provider</span>
              <span className={`text-sm font-medium ${
                llmStatus?.current_provider === 'groq' ? 'text-primary' : 'text-text-secondary'
              }`}>
                {llmStatus?.current_provider === 'groq' ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* Ollama (Local) */}
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Server size={24} className={llmStatus?.ollama?.available ? 'text-green-500' : 'text-gray-500'} />
            <div>
              <h3 className="text-lg font-semibold text-text-primary">Ollama (Local)</h3>
              <p className="text-xs text-text-secondary">Local LLM for privacy</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-text-secondary">Status</span>
              <div className="flex items-center gap-2">
                {llmStatus?.ollama?.available ? (
                  <>
                    <CheckCircle size={16} className="text-green-500" />
                    <span className="text-sm text-green-500">Running</span>
                  </>
                ) : (
                  <>
                    <XCircle size={16} className="text-red-500" />
                    <span className="text-sm text-red-500">Not Running</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-text-secondary">Current Provider</span>
              <span className={`text-sm font-medium ${
                llmStatus?.current_provider === 'ollama' ? 'text-primary' : 'text-text-secondary'
              }`}>
                {llmStatus?.current_provider === 'ollama' ? 'Active' : 'Inactive'}
              </span>
            </div>

            {llmStatus?.ollama?.available && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Base URL</span>
                  <span className="text-xs text-text-primary font-mono">
                    {llmStatus?.ollama?.base_url}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-secondary">Default Model</span>
                  <span className="text-xs text-text-primary font-mono">
                    {llmStatus?.ollama?.default_model}
                  </span>
                </div>

                {ollamaModels.length > 0 && (
                  <div>
                    <span className="text-sm text-text-secondary block mb-2">
                      Available Models ({ollamaModels.length})
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {ollamaModels.slice(0, 5).map((model) => (
                        <span
                          key={model}
                          className="px-2 py-1 rounded text-xs bg-surface-elevated text-text-primary font-mono"
                        >
                          {model}
                        </span>
                      ))}
                      {ollamaModels.length > 5 && (
                        <span className="px-2 py-1 rounded text-xs text-text-secondary">
                          +{ollamaModels.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Test LLM */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Test LLM</h3>
        <p className="text-sm text-text-secondary mb-4">
          Test the current LLM provider with a simple prompt
        </p>

        <button
          onClick={runTest}
          disabled={testing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            bg-primary text-white hover:bg-primary/90 transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {testing ? (
            <>
              <Loader className="animate-spin" size={16} />
              Testing...
            </>
          ) : (
            <>
              <Settings size={16} />
              Run Test
            </>
          )}
        </button>

        {testResult && (
          <div className={`mt-4 p-4 rounded-lg border ${
            testResult.success 
              ? 'bg-green-500/10 border-green-500/20' 
              : 'bg-red-500/10 border-red-500/20'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {testResult.success ? (
                <CheckCircle size={16} className="text-green-500" />
              ) : (
                <XCircle size={16} className="text-red-500" />
              )}
              <span className="text-sm font-medium text-text-primary">
                {testResult.success ? 'Test Successful' : 'Test Failed'}
              </span>
            </div>
            {testResult.provider_used && (
              <p className="text-xs text-text-secondary mb-2">
                Provider: {testResult.provider_used}
              </p>
            )}
            {testResult.response && (
              <p className="text-sm text-text-primary mt-2 p-3 rounded bg-surface-elevated">
                {testResult.response}
              </p>
            )}
            {testResult.error && (
              <p className="text-sm text-red-500 mt-2">
                Error: {testResult.error}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Setup Instructions */}
      {!llmStatus?.ollama?.available && (
        <div className="card p-6 bg-blue-500/5 border-blue-500/20">
          <h3 className="text-lg font-semibold text-text-primary mb-3">
            Enable Privacy Mode with Ollama
          </h3>
          <div className="space-y-2 text-sm text-text-secondary">
            <p>To use local LLM for enhanced privacy:</p>
            <ol className="list-decimal list-inside space-y-1 ml-2">
              <li>Install Ollama from <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">ollama.ai</a></li>
              <li>Run: <code className="px-2 py-0.5 rounded bg-surface-elevated font-mono text-xs">ollama pull llama2</code></li>
              <li>Start Ollama service</li>
              <li>Refresh this page</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
