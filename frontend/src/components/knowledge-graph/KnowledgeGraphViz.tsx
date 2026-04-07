import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ForceGraph2D from 'react-force-graph-2d';
import { Network, Download, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  size: number;
}

interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  correlation: number;
  type: string;
  label: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metrics: {
    node_count: number;
    edge_count: number;
    density: number;
    central_nodes?: Array<{ node: string; centrality: number }>;
  };
}

interface KnowledgeGraphVizProps {
  datasetId: string;
  correlationThreshold?: number;
  width?: number;
  height?: number;
}

export const KnowledgeGraphViz: React.FC<KnowledgeGraphVizProps> = ({ 
  datasetId,
  correlationThreshold = 0.5,
  width = 800,
  height = 600
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const graphRef = useRef<any>();

  useEffect(() => {
    loadGraph();
  }, [datasetId, correlationThreshold]);

  const loadGraph = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.post('/api/knowledge-graph/build', {
        dataset_id: datasetId,
        include_correlations: true,
        include_causality: true,
        correlation_threshold: correlationThreshold
      });

      setGraphData(response.data);
    } catch (err: any) {
      console.error('Error loading graph:', err);
      setError(err.response?.data?.detail || 'Failed to load knowledge graph');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
  };

  const handleZoomIn = () => {
    if (graphRef.current) {
      graphRef.current.zoom(zoom * 1.2, 400);
      setZoom(zoom * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      graphRef.current.zoom(zoom * 0.8, 400);
      setZoom(zoom * 0.8);
    }
  };

  const handleFitView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400);
      setZoom(1);
    }
  };

  const exportGraph = async () => {
    if (!graphData) return;

    try {
      const response = await axios.post('/api/knowledge-graph/export', {
        graph_data: graphData,
        format: 'json'
      });

      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge_graph_${datasetId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting graph:', err);
      alert('Failed to export graph');
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'numeric':
        return '#3B82F6'; // Blue
      case 'categorical':
        return '#22C55E'; // Green
      default:
        return '#6B7280'; // Gray
    }
  };

  const getEdgeColor = (type: string) => {
    switch (type) {
      case 'correlation':
        return '#8B5CF6'; // Purple
      case 'causal':
        return '#EF4444'; // Red
      default:
        return '#9CA3AF'; // Gray
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">Building knowledge graph...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-red-500">{error}</div>
        </div>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-gray-500">No graph data available</div>
        </div>
      </div>
    );
  }

  // Transform data for react-force-graph
  const forceGraphData = {
    nodes: graphData.nodes.map(node => ({
      id: node.id,
      name: node.label,
      type: node.type,
      val: node.size,
      color: getNodeColor(node.type)
    })),
    links: graphData.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      value: edge.weight,
      label: edge.label,
      type: edge.type,
      color: getEdgeColor(edge.type)
    }))
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Network className="w-6 h-6 text-blue-600" />
          Knowledge Graph
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={handleFitView}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Fit View"
          >
            <Maximize2 className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={exportGraph}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Export Graph"
          >
            <Download className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Graph Metrics */}
      <div className="mb-4 grid grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-sm text-gray-600">Nodes</div>
          <div className="text-xl font-bold text-gray-800">{graphData.metrics.node_count}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">Edges</div>
          <div className="text-xl font-bold text-gray-800">{graphData.metrics.edge_count}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">Density</div>
          <div className="text-xl font-bold text-gray-800">
            {(graphData.metrics.density * 100).toFixed(1)}%
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600">Threshold</div>
          <div className="text-xl font-bold text-gray-800">{correlationThreshold}</div>
        </div>
      </div>

      {/* Graph Visualization */}
      <div className="border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
        <ForceGraph2D
          ref={graphRef}
          graphData={forceGraphData}
          width={width}
          height={height}
          nodeLabel="name"
          nodeColor="color"
          nodeVal="val"
          linkLabel="label"
          linkColor="color"
          linkWidth={(link: any) => link.value * 2}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={1}
          onNodeClick={handleNodeClick}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const label = node.name;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

            // Draw node circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.val || 5, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color;
            ctx.fill();

            // Draw label background
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillRect(
              node.x - bckgDimensions[0] / 2,
              node.y + (node.val || 5) + 2,
              bckgDimensions[0],
              bckgDimensions[1]
            );

            // Draw label text
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#1F2937';
            ctx.fillText(label, node.x, node.y + (node.val || 5) + 2 + bckgDimensions[1] / 2);
          }}
        />
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
          <span className="text-gray-600">Numeric</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">Categorical</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-purple-500 rounded"></div>
          <span className="text-gray-600">Correlation</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-gray-600">Causal</span>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNode && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-gray-800 mb-2">Selected Node</h4>
          <div className="space-y-1 text-sm">
            <div><strong>Name:</strong> {selectedNode.label}</div>
            <div><strong>Type:</strong> {selectedNode.type}</div>
            <div><strong>ID:</strong> {selectedNode.id}</div>
          </div>
        </div>
      )}

      {/* Central Nodes */}
      {graphData.metrics.central_nodes && graphData.metrics.central_nodes.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-3">Most Central Nodes</h4>
          <div className="space-y-2">
            {graphData.metrics.central_nodes.slice(0, 5).map((item, index) => (
              <div key={item.node} className="flex items-center justify-between text-sm">
                <span className="text-gray-700">
                  {index + 1}. {item.node}
                </span>
                <span className="font-semibold text-gray-800">
                  {(item.centrality * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
