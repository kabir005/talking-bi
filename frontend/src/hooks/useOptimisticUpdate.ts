import { useState, useCallback } from 'react';

interface OptimisticUpdateOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: any) => void;
  rollbackDelay?: number;
}

export const useOptimisticUpdate = <T,>(initialData: T) => {
  const [data, setData] = useState<T>(initialData);
  const [isOptimistic, setIsOptimistic] = useState(false);
  const [error, setError] = useState<any>(null);

  const update = useCallback(async (
    optimisticData: T,
    asyncUpdate: () => Promise<T>,
    options: OptimisticUpdateOptions<T> = {}
  ) => {
    const previousData = data;
    
    // Apply optimistic update immediately
    setData(optimisticData);
    setIsOptimistic(true);
    setError(null);

    try {
      // Perform actual update
      const result = await asyncUpdate();
      
      // Update with real data
      setData(result);
      setIsOptimistic(false);
      
      options.onSuccess?.(result);
      
      return result;
    } catch (err) {
      // Rollback on error
      const rollbackDelay = options.rollbackDelay || 0;
      
      if (rollbackDelay > 0) {
        setTimeout(() => {
          setData(previousData);
          setIsOptimistic(false);
        }, rollbackDelay);
      } else {
        setData(previousData);
        setIsOptimistic(false);
      }
      
      setError(err);
      options.onError?.(err);
      
      throw err;
    }
  }, [data]);

  const reset = useCallback(() => {
    setIsOptimistic(false);
    setError(null);
  }, []);

  return {
    data,
    isOptimistic,
    error,
    update,
    reset,
    setData
  };
};

// Hook for optimistic list operations
export const useOptimisticList = <T extends { id: string }>(initialList: T[]) => {
  const [list, setList] = useState<T[]>(initialList);
  const [optimisticIds, setOptimisticIds] = useState<Set<string>>(new Set());

  const addOptimistic = useCallback(async (
    item: T,
    asyncAdd: () => Promise<T>
  ) => {
    // Add optimistically
    setList(prev => [...prev, item]);
    setOptimisticIds(prev => new Set(prev).add(item.id));

    try {
      const result = await asyncAdd();
      
      // Replace optimistic item with real one
      setList(prev => prev.map(i => i.id === item.id ? result : i));
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(item.id);
        return next;
      });
      
      return result;
    } catch (err) {
      // Remove on error
      setList(prev => prev.filter(i => i.id !== item.id));
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(item.id);
        return next;
      });
      
      throw err;
    }
  }, []);

  const updateOptimistic = useCallback(async (
    id: string,
    updates: Partial<T>,
    asyncUpdate: () => Promise<T>
  ) => {
    const previousList = list;
    
    // Update optimistically
    setList(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ));
    setOptimisticIds(prev => new Set(prev).add(id));

    try {
      const result = await asyncUpdate();
      
      // Replace with real data
      setList(prev => prev.map(item => item.id === id ? result : item));
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      
      return result;
    } catch (err) {
      // Rollback
      setList(previousList);
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      
      throw err;
    }
  }, [list]);

  const removeOptimistic = useCallback(async (
    id: string,
    asyncRemove: () => Promise<void>
  ) => {
    const previousList = list;
    
    // Remove optimistically
    setList(prev => prev.filter(item => item.id !== id));
    setOptimisticIds(prev => new Set(prev).add(id));

    try {
      await asyncRemove();
      
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } catch (err) {
      // Restore on error
      setList(previousList);
      setOptimisticIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      
      throw err;
    }
  }, [list]);

  const isOptimistic = useCallback((id: string) => {
    return optimisticIds.has(id);
  }, [optimisticIds]);

  return {
    list,
    addOptimistic,
    updateOptimistic,
    removeOptimistic,
    isOptimistic,
    setList
  };
};
