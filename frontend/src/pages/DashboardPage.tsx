import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getDashboard, submitQuery, apiClient, runNLQuery } from '../api/client';
import { AgentStatus, NLQueryResult } from '../types';
import DashboardCanvas from '../components/dashboard/DashboardCanvas';
import InsightPanel from '../components/insights/InsightPanel';
import ConversationBar from '../components/conversation/ConversationBar';
import ChatHistory from '../components/conversation/ChatHistory';
import AgentStatusBar from '../components/shared/AgentStatusBar';
import KPICard from '../components/dashboard/KPICard';
import { ExportMenu } from '../components/export/ExportMenu';
import { FilterBar } from '../components/dashboard/FilterBar';
import { DrillDown } from '../components/dashboard/DrillDown';
import { QuerySuggestions } from '../components/query/QuerySuggestions';
import GlobalVoiceTrigger from '../components/voice/GlobalVoiceTrigger';
import WhatIfPanel from '../components/scenario/WhatIfPanel';
import { useDrillDown } from '../hooks/useDrillDown';
import { useFilters } from '../hooks/useFilters';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [queryLoading, setQueryLoading] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus[]>([]);
  const [showAgentStatus, setShowAgentStatus] = useState(false);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [showChat, setShowChat] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string>('executive');
  const [showQuerySuggestions, setShowQuerySuggestions] = useState(true);
  const [showWhatIf, setShowWhatIf] = useState(false);
  
  // Use drill-down and filter hooks
  const drillDownHook = useDrillDown(dashboard?.dataset_id);
  const filtersHook = useFilters(dashboard?.dataset_id);

  // Detect if query is a data query (for NL2Pandas routing)
  const isDataQuery = (query: string): boolean => {
    const patterns = [
      /^(show|display|get|give me|fetch|find|list)/i,
      /^(top|bottom|first|last|head|tail)\s+\d*/i,
      /\b(filter|where|group by|sort|sum|count|average|mean|max|min)\b/i,
      /\b(previous|last|this)\s+(year|month|week|quarter|day|days)\b/i,
      /\b(rolling|cumulative|trend|growth|change|pct|percent)\b/i,
      /\b(pivot|distinct|unique|duplicate|null|missing)\b/i,
      /\b(describe|stats|statistics|correlation|distribution)\b/i,
      /^(how many|how much)\b/i,
    ];
    return patterns.some(p => p.test(query));
  };

  useEffect(() => {
    if (id) {
      loadDashboard(id);
    }
  }, [id]);

  const handlePresetChange = async (preset: string) => {
    if (!dashboard?.dataset_id || !id) return;
    
    setSelectedPreset(preset);
    setLoading(true);
    
    try {
      console.log('Changing preset to:', preset);
      console.log('Dataset ID:', dashboard.dataset_id);
      console.log('Dashboard ID:', id);
      
      // Regenerate dashboard with new preset
      const response = await apiClient.post('/api/dashboards/generate', {
        name: dashboard.name,
        dataset_id: dashboard.dataset_id,
        preset: preset,
        role: dashboard.role || 'default'
      });
      
      console.log('Generate response:', response.data);
      
      // Update current dashboard with new data
      setDashboard(response.data);
      toast.success(`Switched to ${preset} view`);
    } catch (error: any) {
      console.error('Preset change error:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to change preset');
      setSelectedPreset(dashboard.preset || 'executive'); // Revert on error
    } finally {
      setLoading(false);
    }
  };

  const loadDashboard = async (dashboardId: string) => {
    try {
      const data = await getDashboard(dashboardId);
      console.log('Dashboard loaded:', data);
      console.log('Dashboard tiles:', data.tiles?.length);
      if (data.tiles && data.tiles.length > 0) {
        console.log('First tile:', data.tiles[0]);
      }
      setDashboard(data);
    } catch (error) {
      toast.error('Failed to load dashboard');
      console.error('Dashboard load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async (query: string) => {
    if (!dashboard?.dataset_id) return;

    // Hide suggestions after first query
    setShowQuerySuggestions(false);

    // Add user message to chat
    const userMessage = {
      id: `user-${Date.now()}`,
      type: 'user' as const,
      content: query,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setShowChat(true);

    setQueryLoading(true);

    // Route query based on type
    if (isDataQuery(query)) {
      // Route to NL2Pandas query engine
      try {
        const result: NLQueryResult = await runNLQuery(dashboard.dataset_id, query);
        
        // Add assistant message with query result
        const assistantMessage = {
          id: `assistant-${Date.now()}`,
          type: 'assistant' as const,
          content: result.summary,
          queryResult: result,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, assistantMessage]);
        
        toast.success(`Query executed: ${result.displayed_rows} rows returned`);
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Query failed');
        
        // Add error message
        const errorMessage = {
          id: `assistant-${Date.now()}`,
          type: 'assistant' as const,
          content: `Sorry, I couldn't process that query: ${error.response?.data?.detail || error.message}`,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      } finally {
        setQueryLoading(false);
      }
    } else {
      // Route to conversational agent (existing logic)
      setShowAgentStatus(true);

      // Simulate agent execution
      const agents: AgentStatus[] = [
        { name: 'Orchestrator Agent', status: 'running' },
        { name: 'Cleaning Agent', status: 'waiting' },
        { name: 'Analyst Agent', status: 'waiting' },
        { name: 'Critic Agent', status: 'waiting' },
        { name: 'Chart Agent', status: 'waiting' },
        { name: 'Insight Agent', status: 'waiting' },
        { name: 'Strategist Agent', status: 'waiting' },
      ];

      setAgentStatus(agents);

      try {
        // Simulate progressive agent execution
        for (let i = 0; i < agents.length; i++) {
          await new Promise(resolve => setTimeout(resolve, 500));
          
          setAgentStatus(prev => prev.map((agent, idx) => {
            if (idx === i) return { ...agent, status: 'completed', duration: Math.random() * 2 + 0.5 };
            if (idx === i + 1) return { ...agent, status: 'running' };
            return agent;
          }));
        }

        // Submit actual query
        const result = await submitQuery({
          dataset_id: dashboard.dataset_id,
          query,
          role: dashboard.role || 'default'
        });

        console.log('Query result:', result);

        // Extract results from agent_outputs
        if (result.result?.agent_outputs) {
          const outputs = result.result.agent_outputs;
          
          console.log('Agent outputs:', outputs);
          
          // Extract insights
          if (outputs.insights) {
            console.log('Setting insights:', outputs.insights);
            setInsights(outputs.insights);
          }
          
          // Extract recommendations
          if (outputs.recommendations) {
            console.log('Setting recommendations:', outputs.recommendations);
            setRecommendations(outputs.recommendations);
          }
          
          // Extract KPIs
          if (outputs.analyst?.kpis) {
            console.log('Setting KPIs:', outputs.analyst.kpis);
            // setKpis(outputs.analyst.kpis); // Removed - kpis state variable was removed
          }
          
          // Add assistant message to chat
          const assistantMessage = {
            id: `assistant-${Date.now()}`,
            type: 'assistant' as const,
            content: `I've analyzed your data for: "${query}"`,
            insights: outputs.insights,
            recommendations: outputs.recommendations,
            summary: result.result.summary,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, assistantMessage]);
          
          // Show summary
          if (result.result.summary) {
            const summary = result.result.summary;
            toast.success(
              `Analysis complete! Found ${summary.insights_found || 0} insights, ` +
              `${summary.recommendations_count || 0} recommendations, ` +
              `${summary.charts_generated || 0} charts`
            );
          } else {
            toast.success('Analysis complete!');
          }
        } else {
          toast.error('No analysis results returned');
        }
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Query failed');
        
        setAgentStatus(prev => prev.map(agent => 
          agent.status === 'running' ? { ...agent, status: 'error' } : agent
        ));
      } finally {
        setQueryLoading(false);
      }
    }
  };

  const prepareTileData = (tiles: any[]) => {
    const tileData: Record<string, any[]> = {};
    
    console.log('=== PREPARE TILE DATA ===');
    console.log('Total tiles:', tiles.length);
    
    tiles.forEach((tile, index) => {
      console.log(`\nTile ${index}:`, {
        id: tile.id,
        type: tile.type,
        title: tile.title,
        hasConfig: !!tile.config,
        configType: tile.config?.type,
        hasData: !!(tile.config?.data),
        dataLength: tile.config?.data?.length || 0
      });
      
      if (tile.config && tile.config.data) {
        tileData[tile.id] = tile.config.data;
        console.log(`  ✓ Added ${tile.config.data.length} data points for tile ${tile.id}`);
        if (tile.config.data.length > 0) {
          console.log(`  Sample data:`, tile.config.data[0]);
        }
      } else {
        console.log(`  ✗ No data for tile ${tile.id}`);
      }
    });
    
    console.log('\nTotal tiles with data:', Object.keys(tileData).length);
    console.log('=========================\n');
    return tileData;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="font-heading text-2xl font-bold mb-2">Dashboard not found</h2>
          <p className="text-text-secondary">The dashboard you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Compact Header */}
        <div className="px-6 py-4 border-b border-border bg-surface">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="font-heading text-2xl font-bold">{dashboard.name}</h1>
              <p className="text-sm text-text-secondary mt-1">
                {dashboard.tiles?.length || 0} visualizations
              </p>
            </div>
            
            {/* Compact Toolbar */}
            <div className="flex items-center gap-2">
              {/* Preset Dropdown */}
              <select
                value={selectedPreset}
                onChange={(e) => handlePresetChange(e.target.value)}
                className="px-3 py-2 bg-surface-2 border border-border rounded-lg text-sm font-medium hover:bg-surface-3 transition-colors"
              >
                <option value="executive">Executive</option>
                <option value="operational">Operational</option>
                <option value="trend">Trend Analysis</option>
                <option value="comparison">Comparison</option>
              </select>
              
              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`
                  px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
                  ${showFilters 
                    ? 'bg-accent text-bg' 
                    : 'bg-surface-2 text-text hover:bg-surface-3'
                  }
                `}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                {filtersHook.filters.length > 0 && (
                  <span className="px-1.5 py-0.5 bg-accent text-bg rounded-full text-xs font-bold">
                    {filtersHook.filters.length}
                  </span>
                )}
              </button>
              
              {/* Chat Toggle */}
              <button
                onClick={() => setShowChat(!showChat)}
                className={`
                  px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
                  ${showChat 
                    ? 'bg-accent text-bg' 
                    : 'bg-surface-2 text-text hover:bg-surface-3'
                  }
                `}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                {chatMessages.length > 0 && !showChat && (
                  <span className="px-1.5 py-0.5 bg-accent text-bg rounded-full text-xs font-bold">
                    {chatMessages.length}
                  </span>
                )}
              </button>

              {/* What-If Simulator */}
              <button
                onClick={() => setShowWhatIf(!showWhatIf)}
                className={`
                  px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
                  ${showWhatIf 
                    ? 'bg-accent text-bg' 
                    : 'bg-surface-2 text-text hover:bg-surface-3'
                  }
                `}
                title="What-If Simulator"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </button>
              
              <ExportMenu 
                dashboardId={dashboard.id}
                datasetId={dashboard.dataset_id}
                onExportComplete={(result) => {
                  console.log('Export complete:', result);
                  toast.success('Export completed successfully!');
                }}
              />
            </div>
          </div>
        </div>

        {/* Filter Bar - Compact */}
        {showFilters && dashboard.tiles && (
          <div className="px-6 py-3 border-b border-border bg-surface-2">
            <FilterBar
              columns={[
                ...new Set(
                  dashboard.tiles
                    .filter((t: any) => t.config?.data)
                    .flatMap((t: any) => 
                      t.config.data.length > 0 ? Object.keys(t.config.data[0]) : []
                    )
                )
              ].map(col => ({
                name: col as string,
                type: 'string'
              }))}
              filters={filtersHook.filters}
              onFiltersChange={(newFilters) => {
                filtersHook.filters.forEach((_f, idx) => filtersHook.removeFilter(String(idx)));
                newFilters.forEach(f => filtersHook.addFilter(f));
              }}
            />
          </div>
        )}

        {/* Drill-Down Breadcrumbs - Compact */}
        {drillDownHook.levels.length > 0 && (
          <div className="px-6 py-2 border-b border-border bg-surface-2">
            <DrillDown
              levels={drillDownHook.levels}
              onNavigate={drillDownHook.navigateToLevel}
              onReset={drillDownHook.reset}
            />
          </div>
        )}

        {/* Main Content Area - Toggle between Dashboard and Chat */}
        {showChat ? (
          /* Chat View */
          <ChatHistory messages={chatMessages} />
        ) : (
          /* Dashboard View */
          <>
            {/* KPI Cards - Compact */}
            {(() => {
              const kpiTiles = dashboard.tiles?.filter((t: any) => t.type === 'kpi') || [];
              if (kpiTiles.length > 0) {
                return (
                  <div className="px-6 py-4 border-b border-border bg-surface">
                    <div className="grid grid-cols-4 gap-3">
                      {kpiTiles.map((tile: any) => (
                        <KPICard
                          key={tile.id}
                          label={tile.title}
                          value={tile.config?.value || 0}
                          change={tile.config?.change}
                          trend={tile.config?.trend}
                          format="number"
                        />
                      ))}
                    </div>
                  </div>
                );
              }
              return null;
            })()}

            {/* Dashboard Canvas - Full Height */}
            <div className="flex-1 overflow-auto">
              <DashboardCanvas
                tiles={dashboard.tiles?.filter((t: any) => t.type !== 'kpi') || []}
                data={prepareTileData(dashboard.tiles || [])}
                layout={dashboard.layout?.filter((l: any) => {
                  const tile = dashboard.tiles?.find((t: any) => t.id === l.i);
                  return tile && tile.type !== 'kpi';
                }) || []}
                onLayoutChange={(layout) => console.log('Layout changed:', layout)}
                onTileEdit={(tileId) => console.log('Edit tile:', tileId)}
                onTileDelete={(tileId) => console.log('Delete tile:', tileId)}
                onTileDuplicate={(tileId) => console.log('Duplicate tile:', tileId)}
              />
            </div>
          </>
        )}

        {/* Compact Conversation Bar */}
        <div className="border-t border-border bg-surface">
          {/* Query Suggestions - Show before first query */}
          {showQuerySuggestions && (
            <div className="px-6 pt-4">
              <QuerySuggestions
                visible={showQuerySuggestions}
                onSelect={(query) => {
                  setShowQuerySuggestions(false);
                  handleQuery(query);
                }}
              />
            </div>
          )}
          
          <ConversationBar
            onSubmit={handleQuery}
            loading={queryLoading}
          />
        </div>
      </div>

      {/* Compact Insight Panel */}
      <div className="w-80 border-l border-border bg-surface overflow-auto">
        <InsightPanel
          insights={insights}
          recommendations={recommendations}
        />
      </div>

      {/* Agent Status Bar */}
      <AgentStatusBar
        agents={agentStatus}
        isOpen={showAgentStatus}
        onClose={() => setShowAgentStatus(false)}
      />

      {/* Global Voice Trigger */}
      <GlobalVoiceTrigger />

      {/* What-If Panel */}
      {dashboard?.dataset_id && (
        <WhatIfPanel
          datasetId={dashboard.dataset_id}
          isOpen={showWhatIf}
          onClose={() => setShowWhatIf(false)}
        />
      )}
    </div>
  );
}
