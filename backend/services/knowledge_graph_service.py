"""
Knowledge Graph Service - Build and export knowledge graphs
Creates NetworkX graphs from correlations and causal relationships
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from database.models import Dataset


async def build_knowledge_graph(
    db: AsyncSession,
    dataset_id: str,
    include_correlations: bool = True,
    include_causality: bool = True,
    correlation_threshold: float = 0.5
) -> Dict:
    """
    Build a knowledge graph from dataset relationships.
    
    Args:
        db: Database session
        dataset_id: Dataset ID
        include_correlations: Include correlation edges
        include_causality: Include causal edges
        correlation_threshold: Minimum correlation to include
    
    Returns:
        Knowledge graph data for frontend visualization
    """
    # Get dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")
    
    # Load data
    from sqlalchemy import text
    query_sql = f'SELECT * FROM "{dataset.sqlite_table_name}"'
    result = await db.execute(text(query_sql))
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)
    
    if df.empty:
        raise ValueError("Dataset is empty")
    
    # Create NetworkX graph
    G = nx.DiGraph()
    
    # Get numeric columns for correlation analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Add nodes for each column
    for col in df.columns:
        node_type = "numeric" if col in numeric_cols else "categorical"
        G.add_node(
            col,
            type=node_type,
            label=col,
            size=10
        )
    
    # Add correlation edges
    if include_correlations and len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        
        for i, col_a in enumerate(numeric_cols):
            for j, col_b in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.loc[col_a, col_b]
                    
                    if abs(corr_value) >= correlation_threshold:
                        G.add_edge(
                            col_a,
                            col_b,
                            weight=abs(corr_value),
                            correlation=float(corr_value),
                            type="correlation",
                            label=f"r={corr_value:.2f}"
                        )
    
    # Add causal edges (simple heuristic: strong correlations with time lag)
    if include_causality:
        # Find date column
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                break
        
        if date_col and len(numeric_cols) >= 2:
            # Sort by date
            df_sorted = df.sort_values(date_col)
            
            # Check lagged correlations
            for col_a in numeric_cols[:5]:  # Limit to top 5
                for col_b in numeric_cols[:5]:
                    if col_a != col_b:
                        # Check if col_a predicts col_b with 1-period lag
                        try:
                            lagged_corr = df_sorted[col_a].shift(1).corr(df_sorted[col_b])
                            
                            if abs(lagged_corr) >= correlation_threshold:
                                # Add causal edge
                                if not G.has_edge(col_a, col_b):
                                    G.add_edge(
                                        col_a,
                                        col_b,
                                        weight=abs(lagged_corr),
                                        correlation=float(lagged_corr),
                                        type="causal",
                                        label=f"causes (r={lagged_corr:.2f})",
                                        lag=1
                                    )
                        except Exception as e:
                            print(f"Error computing lagged correlation: {e}")
                            continue
    
    # Convert to frontend-friendly format
    nodes = []
    for node_id, node_data in G.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": node_data.get('label', node_id),
            "type": node_data.get('type', 'unknown'),
            "size": node_data.get('size', 10)
        })
    
    edges = []
    for source, target, edge_data in G.edges(data=True):
        edges.append({
            "source": source,
            "target": target,
            "weight": edge_data.get('weight', 1.0),
            "correlation": edge_data.get('correlation', 0.0),
            "type": edge_data.get('type', 'unknown'),
            "label": edge_data.get('label', ''),
            "lag": edge_data.get('lag', 0)
        })
    
    # Calculate graph metrics
    metrics = {
        "node_count": G.number_of_nodes(),
        "edge_count": G.number_of_edges(),
        "density": nx.density(G),
        "is_connected": nx.is_weakly_connected(G) if G.is_directed() else nx.is_connected(G)
    }
    
    # Find central nodes (most connected)
    if G.number_of_nodes() > 0:
        degree_centrality = nx.degree_centrality(G)
        central_nodes = sorted(
            degree_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        metrics["central_nodes"] = [
            {"node": node, "centrality": centrality}
            for node, centrality in central_nodes
        ]
    
    return {
        "dataset_id": dataset_id,
        "nodes": nodes,
        "edges": edges,
        "metrics": metrics,
        "graph_type": "directed" if G.is_directed() else "undirected"
    }


async def export_graph_formats(
    graph_data: Dict,
    format: str = "json"
) -> Any:
    """
    Export knowledge graph in various formats.
    
    Args:
        graph_data: Graph data from build_knowledge_graph
        format: Export format ("json", "gexf", "graphml", "cytoscape")
    
    Returns:
        Exported graph data in requested format
    """
    # Reconstruct NetworkX graph
    G = nx.DiGraph() if graph_data.get('graph_type') == 'directed' else nx.Graph()
    
    # Add nodes
    for node in graph_data.get('nodes', []):
        G.add_node(node['id'], **{k: v for k, v in node.items() if k != 'id'})
    
    # Add edges
    for edge in graph_data.get('edges', []):
        G.add_edge(
            edge['source'],
            edge['target'],
            **{k: v for k, v in edge.items() if k not in ['source', 'target']}
        )
    
    if format == "json":
        # Return as JSON (already in this format)
        return graph_data
    
    elif format == "gexf":
        # Export as GEXF (Gephi format)
        import io
        buffer = io.StringIO()
        nx.write_gexf(G, buffer)
        return buffer.getvalue()
    
    elif format == "graphml":
        # Export as GraphML
        import io
        buffer = io.StringIO()
        nx.write_graphml(G, buffer)
        return buffer.getvalue()
    
    elif format == "cytoscape":
        # Export as Cytoscape.js format
        cytoscape_data = {
            "elements": {
                "nodes": [
                    {"data": node}
                    for node in graph_data.get('nodes', [])
                ],
                "edges": [
                    {
                        "data": {
                            "id": f"{edge['source']}-{edge['target']}",
                            **edge
                        }
                    }
                    for edge in graph_data.get('edges', [])
                ]
            }
        }
        return cytoscape_data
    
    else:
        raise ValueError(f"Unsupported format: {format}")


async def find_shortest_path(
    graph_data: Dict,
    source: str,
    target: str
) -> Dict:
    """
    Find shortest path between two nodes in the knowledge graph.
    
    Args:
        graph_data: Graph data from build_knowledge_graph
        source: Source node ID
        target: Target node ID
    
    Returns:
        Shortest path information
    """
    # Reconstruct NetworkX graph
    G = nx.DiGraph() if graph_data.get('graph_type') == 'directed' else nx.Graph()
    
    for node in graph_data.get('nodes', []):
        G.add_node(node['id'])
    
    for edge in graph_data.get('edges', []):
        G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1.0))
    
    try:
        if nx.has_path(G, source, target):
            path = nx.shortest_path(G, source, target, weight='weight')
            path_length = nx.shortest_path_length(G, source, target, weight='weight')
            
            # Get edges along the path
            path_edges = []
            for i in range(len(path) - 1):
                edge_data = G.get_edge_data(path[i], path[i+1])
                path_edges.append({
                    "source": path[i],
                    "target": path[i+1],
                    "weight": edge_data.get('weight', 1.0)
                })
            
            return {
                "source": source,
                "target": target,
                "path": path,
                "path_length": path_length,
                "edges": path_edges,
                "found": True
            }
        else:
            return {
                "source": source,
                "target": target,
                "path": [],
                "path_length": float('inf'),
                "edges": [],
                "found": False,
                "message": "No path exists between these nodes"
            }
    
    except nx.NodeNotFound as e:
        return {
            "source": source,
            "target": target,
            "path": [],
            "path_length": float('inf'),
            "edges": [],
            "found": False,
            "message": f"Node not found: {str(e)}"
        }


async def get_node_neighbors(
    graph_data: Dict,
    node_id: str,
    depth: int = 1
) -> Dict:
    """
    Get neighbors of a node up to specified depth.
    
    Args:
        graph_data: Graph data from build_knowledge_graph
        node_id: Node ID
        depth: Depth of neighborhood (1 = direct neighbors)
    
    Returns:
        Neighbor information
    """
    # Reconstruct NetworkX graph
    G = nx.DiGraph() if graph_data.get('graph_type') == 'directed' else nx.Graph()
    
    for node in graph_data.get('nodes', []):
        G.add_node(node['id'], **{k: v for k, v in node.items() if k != 'id'})
    
    for edge in graph_data.get('edges', []):
        G.add_edge(edge['source'], edge['target'])
    
    if node_id not in G:
        return {
            "node_id": node_id,
            "neighbors": [],
            "message": "Node not found"
        }
    
    # Get neighbors at each depth level
    neighbors_by_depth = {}
    visited = {node_id}
    current_level = {node_id}
    
    for d in range(1, depth + 1):
        next_level = set()
        for node in current_level:
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    next_level.add(neighbor)
                    visited.add(neighbor)
        
        neighbors_by_depth[d] = list(next_level)
        current_level = next_level
    
    return {
        "node_id": node_id,
        "depth": depth,
        "neighbors_by_depth": neighbors_by_depth,
        "total_neighbors": len(visited) - 1  # Exclude the node itself
    }



