import { useState, useRef, useEffect } from 'react';
import GridLayout, { Layout } from 'react-grid-layout';
import { ChartTile as ChartTileType } from '../../types';
import ChartTile from './ChartTile';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

interface DashboardCanvasProps {
  tiles: ChartTileType[];
  data: Record<string, any[]>;
  layout?: Layout[];
  onLayoutChange?: (layout: Layout[]) => void;
  onTileEdit?: (tileId: string) => void;
  onTileDelete?: (tileId: string) => void;
  onTileDuplicate?: (tileId: string) => void;
}

export default function DashboardCanvas({
  tiles,
  data,
  layout: providedLayout,
  onLayoutChange,
  onTileEdit,
  onTileDelete,
  onTileDuplicate
}: DashboardCanvasProps) {
  const [fullscreenTile, setFullscreenTile] = useState<string | null>(null);
  const [containerWidth, setContainerWidth] = useState(1200);
  const containerRef = useRef<HTMLDivElement>(null);

  // Measure container width for responsive layout
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth - 32); // Subtract padding
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  // Use provided layout or generate default layout from tiles
  const layout: Layout[] = providedLayout || tiles.map((tile, index) => ({
    i: tile.id,
    x: (index % 3) * 4,
    y: Math.floor(index / 3) * 4,
    w: 4,
    h: 4,
    minW: 2,
    minH: 2
  }));

  const handleLayoutChange = (newLayout: Layout[]) => {
    if (onLayoutChange) {
      onLayoutChange(newLayout);
    }
  };

  if (fullscreenTile) {
    const tile = tiles.find(t => t.id === fullscreenTile);
    if (tile) {
      return (
        <div className="fixed inset-0 z-50 bg-slate-950 p-8">
          <button
            onClick={() => setFullscreenTile(null)}
            className="absolute top-4 right-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors text-white border border-slate-700"
          >
            Close
          </button>
          <div className="h-full">
            <ChartTile
              tile={tile}
              data={data[tile.id] || []}
              onEdit={() => onTileEdit?.(tile.id)}
              onDelete={() => {
                setFullscreenTile(null);
                onTileDelete?.(tile.id);
              }}
            />
          </div>
        </div>
      );
    }
  }

  if (tiles.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-center p-8 bg-slate-950">
        <div>
          <h3 className="font-heading text-xl font-semibold mb-2 text-white">No charts yet</h3>
          <p className="text-slate-400">
            Ask a question or generate a dashboard to see visualizations
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="h-full overflow-auto p-4 bg-slate-950">
      <GridLayout
        className="layout"
        layout={layout}
        cols={12}
        rowHeight={60}
        width={containerWidth}
        onLayoutChange={handleLayoutChange}
        draggableHandle=".drag-handle"
        isDraggable={true}
        isResizable={true}
        compactType="vertical"
        preventCollision={false}
        margin={[16, 16]}
        containerPadding={[0, 0]}
      >
        {tiles.map((tile) => (
          <div key={tile.id} className="overflow-hidden">
            <ChartTile
              tile={tile}
              data={data[tile.id] || []}
              onEdit={() => onTileEdit?.(tile.id)}
              onDuplicate={() => onTileDuplicate?.(tile.id)}
              onDelete={() => onTileDelete?.(tile.id)}
              onFullscreen={() => setFullscreenTile(tile.id)}
            />
          </div>
        ))}
      </GridLayout>
    </div>
  );
}
