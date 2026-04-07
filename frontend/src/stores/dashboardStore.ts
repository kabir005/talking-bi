import { create } from 'zustand';
import { Dashboard, ChartTile } from '../types';

interface DashboardStore {
  dashboards: Dashboard[];
  currentDashboard: Dashboard | null;
  setDashboards: (dashboards: Dashboard[]) => void;
  setCurrentDashboard: (dashboard: Dashboard | null) => void;
  addDashboard: (dashboard: Dashboard) => void;
  updateDashboard: (id: string, updates: Partial<Dashboard>) => void;
  removeDashboard: (id: string) => void;
  updateTile: (tileId: string, updates: Partial<ChartTile>) => void;
  addTile: (tile: ChartTile) => void;
  removeTile: (tileId: string) => void;
  addVoiceTile: (tile: { title: string; source: string; chart_config: any | null }) => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  dashboards: [],
  currentDashboard: null,
  setDashboards: (dashboards) => set({ dashboards }),
  setCurrentDashboard: (dashboard) => set({ currentDashboard: dashboard }),
  addDashboard: (dashboard) => set((state) => ({ dashboards: [...state.dashboards, dashboard] })),
  updateDashboard: (id, updates) => set((state) => ({
    dashboards: state.dashboards.map((d) => (d.id === id ? { ...d, ...updates } : d)),
    currentDashboard: state.currentDashboard?.id === id 
      ? { ...state.currentDashboard, ...updates } 
      : state.currentDashboard,
  })),
  removeDashboard: (id) => set((state) => ({
    dashboards: state.dashboards.filter((d) => d.id !== id),
    currentDashboard: state.currentDashboard?.id === id ? null : state.currentDashboard,
  })),
  updateTile: (tileId, updates) => set((state) => {
    if (!state.currentDashboard) return state;
    
    const updatedTiles = state.currentDashboard.tiles.map((tile) =>
      tile.id === tileId ? { ...tile, ...updates } : tile
    );
    
    return {
      currentDashboard: { ...state.currentDashboard, tiles: updatedTiles },
    };
  }),
  addTile: (tile) => set((state) => {
    if (!state.currentDashboard) return state;
    
    return {
      currentDashboard: {
        ...state.currentDashboard,
        tiles: [...state.currentDashboard.tiles, tile],
      },
    };
  }),
  removeTile: (tileId) => set((state) => {
    if (!state.currentDashboard) return state;
    
    return {
      currentDashboard: {
        ...state.currentDashboard,
        tiles: state.currentDashboard.tiles.filter((tile) => tile.id !== tileId),
      },
    };
  }),
  addVoiceTile: (tile: { title: string; source: string; chart_config: any | null }) => set((state) => {
    if (!state.currentDashboard) return state;
    
    // Generate a new tile ID
    const tileId = `voice_${Date.now()}`;
    
    // Create new tile
    const newTile: ChartTile = {
      id: tileId,
      type: (tile.chart_config?.type as any) || 'bar',
      x_column: tile.chart_config?.xKey || '',
      y_column: tile.chart_config?.yKey || '',
      title: tile.title,
      options: {
        config: tile.chart_config,
        source: 'voice'
      }
    };
    
    return {
      currentDashboard: {
        ...state.currentDashboard,
        tiles: [...state.currentDashboard.tiles, newTile],
      },
    };
  }),
}));
