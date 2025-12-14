/**
 * ZOHO CRM連携サービス
 */
import { api } from './api';

// 型定義
export interface ZohoStatus {
  configured: boolean;
  has_refresh_token: boolean;
  connected: boolean;
  module_name: string;
  module_exists?: boolean;
  error?: string;
}

export interface ZohoProperty {
  id: string;
  [key: string]: any;
}

export interface ZohoPropertiesResponse {
  data: ZohoProperty[];
  info: {
    count?: number;
    more_records?: boolean;
    page?: number;
    per_page?: number;
  };
  page: number;
  per_page: number;
}

export interface ZohoImportRequest {
  zoho_ids: string[];
  update_existing: boolean;
  auto_geocode: boolean;
}

export interface ZohoImportResult {
  success: number;
  failed: number;
  skipped: number;
  errors: { message: string }[];
}

// API関数
export const zohoService = {
  /**
   * 接続状態を取得
   */
  async getStatus(): Promise<ZohoStatus> {
    const response = await api.get('/zoho/status');
    return response.data;
  },

  /**
   * OAuth認証URLを取得
   */
  async getAuthUrl(): Promise<string> {
    const response = await api.get('/zoho/auth');
    return response.data.auth_url;
  },

  /**
   * モジュール一覧を取得
   */
  async getModules(): Promise<any[]> {
    const response = await api.get('/zoho/modules');
    return response.data.modules;
  },

  /**
   * フィールド一覧を取得
   */
  async getFields(module?: string): Promise<any[]> {
    const response = await api.get('/zoho/fields', {
      params: module ? { module } : undefined
    });
    return response.data.fields;
  },

  /**
   * 物件一覧を取得
   */
  async getProperties(page = 1, perPage = 50): Promise<ZohoPropertiesResponse> {
    const response = await api.get('/zoho/properties', {
      params: { page, per_page: perPage }
    });
    return response.data;
  },

  /**
   * 物件詳細を取得
   */
  async getProperty(zohoId: string): Promise<ZohoProperty> {
    const response = await api.get(`/zoho/properties/${zohoId}`);
    return response.data.data;
  },

  /**
   * 物件をインポート
   */
  async importProperties(request: ZohoImportRequest): Promise<ZohoImportResult> {
    const response = await api.post('/zoho/import', request);
    return response.data;
  }
};
