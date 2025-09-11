import { useEffect, useRef, useCallback, useState } from 'react';
import debounce from 'lodash.debounce';

interface UseAutoSaveOptions {
  delay?: number;
  onSave: (data: any) => Promise<void>;
  enabled?: boolean;
}

interface AutoSaveState {
  isSaving: boolean;
  lastSaved: Date | null;
  saveError: Error | null;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
}

export const useAutoSave = (data: any, options: UseAutoSaveOptions) => {
  const { delay = 1000, onSave, enabled = true } = options;
  
  const [state, setState] = useState<AutoSaveState>({
    isSaving: false,
    lastSaved: null,
    saveError: null,
    saveStatus: 'idle'
  });

  const saveDataRef = useRef(data);
  const isFirstRender = useRef(true);

  // データを保存する関数
  const performSave = useCallback(async (dataToSave: any) => {
    setState(prev => ({ ...prev, isSaving: true, saveStatus: 'saving', saveError: null }));
    
    try {
      await onSave(dataToSave);
      setState(prev => ({
        ...prev,
        isSaving: false,
        lastSaved: new Date(),
        saveStatus: 'saved',
        saveError: null
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isSaving: false,
        saveStatus: 'error',
        saveError: error as Error
      }));
      console.error('自動保存エラー:', error);
    }
  }, [onSave]);

  // デバウンスされた保存関数
  const debouncedSave = useRef(
    debounce((dataToSave: any) => {
      performSave(dataToSave);
    }, delay)
  ).current;

  // 即座に保存する関数（画像アップロードなど）
  const saveImmediately = useCallback(async () => {
    debouncedSave.cancel();
    await performSave(saveDataRef.current);
  }, [performSave, debouncedSave]);

  // データが変更されたときの処理
  useEffect(() => {
    saveDataRef.current = data;

    // 初回レンダリング時は保存しない
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    // 自動保存が有効な場合のみ実行
    if (enabled && data) {
      debouncedSave(data);
    }

    // クリーンアップ
    return () => {
      debouncedSave.cancel();
    };
  }, [data, enabled, debouncedSave]);

  // コンポーネントのアンマウント時に保存
  useEffect(() => {
    return () => {
      if (enabled && saveDataRef.current && state.saveStatus !== 'saved') {
        debouncedSave.flush();
      }
    };
  }, [enabled, state.saveStatus, debouncedSave]);

  return {
    ...state,
    saveImmediately,
    cancelPendingSave: debouncedSave.cancel
  };
};