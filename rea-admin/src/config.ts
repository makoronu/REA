/**
 * アプリケーション設定
 * 全ての設定値はここで一元管理する（DRY原則）
 */

// API設定
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';
export const API_BASE_URL = `${API_URL}/api/v1`;

// 画像URL
export const getImageUrl = (path: string) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${API_URL}${path.startsWith('/') ? '' : '/'}${path}`;
};
