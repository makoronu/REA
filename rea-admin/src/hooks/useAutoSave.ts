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
  const prevDataJsonRef = useRef<string>('');
  const isFirstRender = useRef(true);
  const hasUnsavedChanges = useRef(false);
  const onSaveRef = useRef(onSave);

  // onSaveの参照を常に最新に保つ
  useEffect(() => {
    onSaveRef.current = onSave;
  }, [onSave]);

  // 保存実行（関数をrefで保持してクロージャ問題を回避）
  const performSaveRef = useRef(async (dataToSave: any) => {
    setState(prev => ({ ...prev, isSaving: true, saveStatus: 'saving', saveError: null }));
    setGlobalStatus('saving');

    try {
      await onSaveRef.current(dataToSave);
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
  });

  // デバウンス保存
  const debouncedSave = useRef(
    debounce((dataToSave: any) => {
      performSaveRef.current(dataToSave);
    }, delay)
  ).current;

  // 即時保存
  const saveImmediately = useCallback(async () => {
    debouncedSave.cancel();
    if (saveDataRef.current) {
      await performSaveRef.current(saveDataRef.current);
    }
  }, [debouncedSave]);

  // データ変更時（JSON比較で本当に変わった場合のみ）
  useEffect(() => {
    if (!enabled || !data) return;

    const currentJson = JSON.stringify(data);

    // 初回は保存せず、前回値を記録
    if (isFirstRender.current) {
      isFirstRender.current = false;
      prevDataJsonRef.current = currentJson;
      saveDataRef.current = data;
      return;
    }

    // 本当にデータが変わった場合のみ処理
    if (currentJson === prevDataJsonRef.current) {
      return;
    }

    prevDataJsonRef.current = currentJson;
    saveDataRef.current = data;

    // 変更ありマーク
    if (!hasUnsavedChanges.current) {
      hasUnsavedChanges.current = true;
      setState(prev => ({ ...prev, saveStatus: 'unsaved' }));
      setGlobalStatus('unsaved');
    }
    debouncedSave(data);
    // クリーンアップでキャンセルしない（データ変更のたびにキャンセルされてしまうため）
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
        performSaveRef.current(saveDataRef.current);
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
  }, [enabled, debouncedSave]);

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
