// 認証コンテキスト
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService, User, LoginRequest, getStoredUser, getToken } from '../services/authService';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (request: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 初期化: ストレージからユーザー情報を復元
  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      if (token) {
        // トークンがあればストレージからユーザー情報を復元
        const storedUser = getStoredUser();
        if (storedUser) {
          setUser(storedUser);
        }
        // バックグラウンドで最新のユーザー情報を取得
        try {
          const freshUser = await authService.getCurrentUser();
          setUser(freshUser);
        } catch {
          // トークンが無効ならクリア
          await authService.logout();
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // ログイン
  const login = useCallback(async (request: LoginRequest) => {
    const response = await authService.login(request);
    setUser(response.user);
  }, []);

  // ログアウト
  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, []);

  // ユーザー情報を再取得
  const refreshUser = useCallback(async () => {
    try {
      const freshUser = await authService.getCurrentUser();
      setUser(freshUser);
    } catch {
      // エラー時は何もしない
    }
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
