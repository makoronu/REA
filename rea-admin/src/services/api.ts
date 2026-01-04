// API通信の基本設定
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { STORAGE_KEYS } from '../constants/storage';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター: JWTトークンを自動付与
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター: エラーハンドリング
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401エラーの場合、トークンを削除してログインページへ
    if (error.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.AUTH_USER);
      // 現在のページがログインでなければリダイレクト
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    // 詳細エラーログ
    console.error('=== API Error ===');
    console.error('URL:', error.config?.url);
    console.error('Method:', error.config?.method);
    console.error('Status:', error.response?.status);
    console.error('Detail:', error.response?.data?.detail || error.message);
    console.error('Full response:', error.response?.data);
    return Promise.reject(error);
  }
);