// 認証サービス
import { api } from './api';
import { STORAGE_KEYS } from '../constants/storage';

// 型定義
export interface User {
  id: number;
  email: string;
  name: string;
  organization_id: number;
  organization_name: string;
  role_code: string;
  role_name: string;
  role_level: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

// トークン管理（キーはconstants/storage.tsで一元管理）
export const getToken = (): string | null => {
  return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
};

export const setToken = (token: string): void => {
  localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
};

export const removeToken = (): void => {
  localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
};

// ユーザー情報管理
export const getStoredUser = (): User | null => {
  const userStr = localStorage.getItem(STORAGE_KEYS.AUTH_USER);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

export const setStoredUser = (user: User): void => {
  localStorage.setItem(STORAGE_KEYS.AUTH_USER, JSON.stringify(user));
};

export const removeStoredUser = (): void => {
  localStorage.removeItem(STORAGE_KEYS.AUTH_USER);
};

// API呼び出し
export const authService = {
  // ログイン
  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', request);
    const { token, user } = response.data;

    // トークンとユーザー情報を保存
    setToken(token);
    setStoredUser(user);

    return response.data;
  },

  // ログアウト
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch {
      // エラーでも続行（トークン無効の場合など）
    } finally {
      removeToken();
      removeStoredUser();
    }
  },

  // 現在のユーザー情報を取得
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    setStoredUser(response.data);
    return response.data;
  },

  // 認証済みかどうか
  isAuthenticated(): boolean {
    return !!getToken();
  },

  // パスワードリセットリクエスト
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/password-reset/request', { email });
    return response.data;
  },

  // パスワードリセットトークン検証
  async verifyResetToken(token: string): Promise<{ valid: boolean; message: string }> {
    const response = await api.get<{ valid: boolean; message: string }>(`/auth/password-reset/verify/${token}`);
    return response.data;
  },

  // パスワードリセット実行
  async confirmPasswordReset(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default authService;
