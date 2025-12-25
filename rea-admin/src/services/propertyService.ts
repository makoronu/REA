// 物件関連のAPI呼び出し
import { api } from './api';
import { Property, PropertySearchParams } from '../types/property';

export interface PropertiesResponse {
  items: Property[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export const propertyService = {
  // 物件一覧取得（ページネーション対応）
  async getProperties(params?: PropertySearchParams): Promise<Property[]> {
    const response = await api.get('/properties/', { params });
    // APIが配列を返す場合はそのまま返す
    if (Array.isArray(response.data)) {
      return response.data;
    }
    // ページネーション付きレスポンスの場合
    return response.data.items || response.data;
  },

  // 物件一覧取得（総件数付き）
  async getPropertiesWithCount(params?: PropertySearchParams): Promise<{ items: Property[]; total: number }> {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.property_type) queryParams.append('property_type', params.property_type);
    if (params?.sales_status) queryParams.append('sales_status', params.sales_status);
    if (params?.publication_status) queryParams.append('publication_status', params.publication_status);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.sale_price_min !== undefined) queryParams.append('sale_price_min', params.sale_price_min.toString());
    if (params?.sale_price_max !== undefined) queryParams.append('sale_price_max', params.sale_price_max.toString());

    const response = await api.get(`/properties/?${queryParams.toString()}`);

    // APIが配列を返す場合
    if (Array.isArray(response.data)) {
      return { items: response.data, total: response.data.length };
    }
    // ページネーション付きレスポンスの場合
    return { items: response.data.items || response.data, total: response.data.total || response.data.length };
  },

  // 物件詳細取得
  async getProperty(id: number): Promise<Property> {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },

  // 物件詳細取得（関連テーブル含む）- 編集画面用
  async getPropertyFull(id: number): Promise<Property> {
    const response = await api.get(`/properties/${id}/full`);
    return response.data;
  },

  // 物件更新
  async updateProperty(id: number, data: Partial<Property>): Promise<Property> {
    const response = await api.put(`/properties/${id}`, data);
    return response.data;
  },

  // 物件作成
  async createProperty(data: Partial<Property>): Promise<Property> {
    const response = await api.post('/properties/', data);
    return response.data;
  },

  // 物件削除
  async deleteProperty(id: number): Promise<void> {
    await api.delete(`/properties/${id}`);
  },

  // 画像アップロード（複数対応）
  async uploadImages(propertyId: number, files: File[]): Promise<string[]> {
    const uploadPromises = files.map(async (file) => {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('property_id', propertyId.toString());

      const response = await api.post(`/properties/${propertyId}/images`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data.url;
    });

    return Promise.all(uploadPromises);
  },

  // 画像削除
  async deleteImage(propertyId: number, imageUrl: string): Promise<void> {
    const fileName = imageUrl.split('/').pop();
    await api.delete(`/properties/${propertyId}/images/${fileName}`);
  },

  // 画像一覧を含む物件情報を更新
  async updatePropertyWithImages(id: number, data: Partial<Property>, imageUrls: string[]): Promise<Property> {
    const updateData = {
      ...data,
      images: imageUrls
    };
    return this.updateProperty(id, updateData);
  },
};
