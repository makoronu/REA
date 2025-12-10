import { useEffect, useRef, useCallback, useState } from 'react';

// 保存状態
export type SaveStatus = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error';

interface UseAutoSaveOptions {
  delay?: number;
  onSave: (data: any) => Promise<void>;
  enabled?: boolean;
}

interface AutoSaveState {
  isSaving: boolean;
  lastSaved: Date | null;
  saveError: Error | null;
  saveStatus: SaveStatus;
}

// グローバル状態（Layout表示用）
let globalSaveStatus: SaveStatus = 'idle';
let globalLastSaved: Date | null = null;
let globalListeners: Array<() => void> = [];

export const subscribeToSaveStatus = (listener: () => void) => {
  globalListeners.push(listener);
  return () => {
    globalListeners = globalListeners.filter(l => l !== listener);
  };
};

export const getSaveStatus = () => ({ status: globalSaveStatus, lastSaved: globalLastSaved });

const notifyListeners = () => {
  globalListeners.forEach(listener => listener());
};

const setGlobalStatus = (status: SaveStatus, lastSaved?: Date | null) => {
  globalSaveStatus = status;
  if (lastSaved !== undefined) {
    globalLastSaved = lastSaved;
  }
  notifyListeners();
};

// デバウンス関数（lodash不要に）
const debounce = <T extends (...args: any[]) => any>(fn: T, delay: number) => {
  let timeoutId: NodeJS.Timeout | null = null;

  const debouncedFn = (...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };

  debouncedFn.cancel = () => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = null;
  };

  debouncedFn.flush = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debouncedFn;
};

export const useAutoSave = (data: any, options: UseAutoSaveOptions) => {
  const { delay = 2000, onSave, enabled = true } = options;

  const [state, setState] = useState<AutoSaveState>({
    isSaving: false,
    lastSaved: null,
    saveError: null,
    saveStatus: 'idle'
  });

  const saveDataRef = useRef(data);
  const isFirstRender = useRef(true);
  const hasUnsavedChanges = useRef(false);

  // 保存実行
  const performSave = useCallback(async (dataToSave: any) => {
    setState(prev => ({ ...prev, isSaving: true, saveStatus: 'saving', saveError: null }));
    setGlobalStatus('saving');

    try {
      await onSave(dataToSave);
      const now = new Date();
      setState(prev => ({
        ...prev,
        isSaving: false,
        lastSaved: now,
        saveStatus: 'saved',
        saveError: null
      }));
      setGlobalStatus('saved', now);
      hasUnsavedChanges.current = false;
    } catch (error) {
      setState(prev => ({
        ...prev,
        isSaving: false,
        saveStatus: 'error',
        saveError: error as Error
      }));
      setGlobalStatus('error');
      console.error('自動保存エラー:', error);
    }
  }, [onSave]);

  // デバウンス保存
  const debouncedSave = useRef(
    debounce((dataToSave: any) => {
      performSave(dataToSave);
    }, delay)
  ).current;

  // 即時保存
  const saveImmediately = useCallback(async () => {
    debouncedSave.cancel();
    if (saveDataRef.current) {
      await performSave(saveDataRef.current);
    }
  }, [performSave, debouncedSave]);

  // データ変更時
  useEffect(() => {
    saveDataRef.current = data;

    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (enabled && data) {
      // 変更ありマーク
      if (!hasUnsavedChanges.current) {
        hasUnsavedChanges.current = true;
        setState(prev => ({ ...prev, saveStatus: 'unsaved' }));
        setGlobalStatus('unsaved');
      }
      debouncedSave(data);
    }

    return () => {
      debouncedSave.cancel();
    };
  }, [data, enabled, debouncedSave]);

  // ページ離脱/タブ切替時に保存
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges.current) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && hasUnsavedChanges.current && saveDataRef.current) {
        debouncedSave.cancel();
        performSave(saveDataRef.current);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (enabled && hasUnsavedChanges.current) {
        debouncedSave.flush();
      }
    };
  }, [enabled, performSave, debouncedSave]);

  return {
    ...state,
    saveImmediately,
    cancelPendingSave: debouncedSave.cancel,
    hasUnsavedChanges: hasUnsavedChanges.current
  };
};

// Layout用フック
export const useSaveStatusDisplay = () => {
  const [, forceUpdate] = useState({});

  useEffect(() => {
    return subscribeToSaveStatus(() => forceUpdate({}));
  }, []);

  return getSaveStatus();
};
