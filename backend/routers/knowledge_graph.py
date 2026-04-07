"""
Knowledge Graph Router - API endpoints for knowledge graph operations
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from services import knowledge_graph_service

router = APIRouter()


class BuildGraphRequest(BaseModel):
    dataset_id: str
    include_correlations: bool = True
    include_causality: bool = True
    correlation_threshold: float = 0.5


class ExportGraphRequest(BaseModel):
    format: str = "json"  # json, gexf, graphml, cytoscape


class ShortestPathRequest(BaseModel):
    source: str
    target: str


class NeighborsRequest(BaseModel):
    node_id: str
    depth: int = 1


@router.post("/build")
async def build_graph(request: BuildGraphRequest, db: AsyncSession = Depends(get_db)):
    """
    Build a knowledge graph from dataset relationships.
    
    Request body:
    - dataset_id: Dataset ID
    - include_correlations: Include correlation edges
    - include_causality: Include causal edges
    - correlation_threshold: Minimum correlation to include
    
    Returns:
    - nodes: List of graph nodes
    - edges: List of graph edges
    - metrics: Graph metrics
    """
    try:
        result = await knowledge_graph_service.build_knowledge_graph(
            db=db,
            dataset_id=request.dataset_id,
            include_correlations=request.include_correlations,
            include_causality=request.include_causality,
            correlation_threshold=request.correlation_threshold
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph building failed: {str(e)}")


@router.post("/export")
async def export_graph(
    graph_data: dict,
    request: ExportGraphRequest
):
    """
    Export knowledge graph in various formats.
    
    Request body:
    - graph_data: Graph data from build endpoint
    - format: Export format (json, gexf, graphml, cytoscape)
    
    Returns:
    - Exported graph data in requested format
    """
    try:
        result = await knowledge_graph_service.export_graph_formats(
            graph_data=graph_data,
            format=request.format
        )
        
        # Set appropriate content type
        if request.format == "json":
            return result
        elif request.format in ["gexf", "graphml"]:
            return Response(content=result, media_type="application/xml")
        else:
            return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph export failed: {str(e)}")


@router.post("/shortest-path")
async def find_shortest_path(
    graph_data: dict,
    request: ShortestPathRequest
):
    """
    Find shortest path between two nodes in the knowledge graph.
    
    Request body:
    - graph_data: Graph data from build endpoint
    - source: Source node ID
    - target: Target node ID
    
    Returns:
    - path: List of nodes in shortest path
    - path_length: Length of path
    - edges: Edges along the path
    """
    try:
        result = await knowledge_graph_service.find_shortest_path(
            graph_data=graph_data,
            source=request.source,
            target=request.target
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path finding failed: {str(e)}")


@router.post("/neighbors")
async def get_neighbors(
    graph_data: dict,
    request: NeighborsRequest
):
    """
    Get neighbors of a node up to specified depth.
    
    Request body:
    - graph_data: Graph data from build endpoint
    - node_id: Node ID
    - depth: Depth of neighborhood
    
    Returns:
    - neighbors_by_depth: Neighbors at each depth level
    - total_neighbors: Total number of neighbors
    """
    try:
        result = await knowledge_graph_service.get_node_neighbors(
            graph_data=graph_data,
            node_id=request.node_id,
            depth=request.depth
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neighbor search failed: {str(e)}")

