import { create } from 'zustand';
import { Dataset } from '../types';

interface DatasetStore {
  datasets: Dataset[];
  currentDataset: Dataset | null;
  setDatasets: (datasets: Dataset[]) => void;
  setCurrentDataset: (dataset: Dataset | null) => void;
  addDataset: (dataset: Dataset) => void;
  removeDataset: (id: string) => void;
}

export const useDatasetStore = create<DatasetStore>((set) => ({
  datasets: [],
  currentDataset: null,
  setDatasets: (datasets) => set({ datasets }),
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
  addDataset: (dataset) => set((state) => ({ datasets: [...state.datasets, dataset] })),
  removeDataset: (id) => set((state) => ({
    datasets: state.datasets.filter((d) => d.id !== id),
    currentDataset: state.currentDataset?.id === id ? null : state.currentDataset,
  })),
}));
