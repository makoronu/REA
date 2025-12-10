import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// 保存状態の型
export type SaveStatus = 'idle' | 'unsaved' | 'saving' | 'saved' | 'error';

interface AutoSaveContextType {
  status: SaveStatus;
  lastSavedAt: Date | null;
  errorMessage: string | null;
  setStatus: (status: SaveStatus) => void;
  setLastSavedAt: (date: Date | null) => void;
  setErrorMessage: (message: string | null) => void;
  markAsUnsaved: () => void;
  markAsSaving: () => void;
  markAsSaved: () => void;
  markAsError: (message: string) => void;
}

const AutoSaveContext = createContext<AutoSaveContextType | undefined>(undefined);

export const AutoSaveProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<SaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const markAsUnsaved = useCallback(() => {
    setStatus('unsaved');
    setErrorMessage(null);
  }, []);

  const markAsSaving = useCallback(() => {
    setStatus('saving');
    setErrorMessage(null);
  }, []);

  const markAsSaved = useCallback(() => {
    setStatus('saved');
    setLastSavedAt(new Date());
    setErrorMessage(null);
  }, []);

  const markAsError = useCallback((message: string) => {
    setStatus('error');
    setErrorMessage(message);
  }, []);

  return (
    <AutoSaveContext.Provider
      value={{
        status,
        lastSavedAt,
        errorMessage,
        setStatus,
        setLastSavedAt,
        setErrorMessage,
        markAsUnsaved,
        markAsSaving,
        markAsSaved,
        markAsError,
      }}
    >
      {children}
    </AutoSaveContext.Provider>
  );
};

export const useAutoSaveContext = (): AutoSaveContextType => {
  const context = useContext(AutoSaveContext);
  if (context === undefined) {
    throw new Error('useAutoSaveContext must be used within an AutoSaveProvider');
  }
  return context;
};
