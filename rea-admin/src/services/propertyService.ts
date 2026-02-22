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

  // 画像アップロード（単一）
  async uploadImage(
    propertyId: number,
    file: File,
    metadata?: {
      image_type?: string;
      display_order?: number;
      caption?: string;
      is_public?: boolean;
    }
  ): Promise<PropertyImage> {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata?.image_type) formData.append('image_type', metadata.image_type);
    if (metadata?.display_order !== undefined) formData.append('display_order', metadata.display_order.toString());
    if (metadata?.caption) formData.append('caption', metadata.caption);
    if (metadata?.is_public !== undefined) formData.append('is_public', metadata.is_public.toString());

    const response = await api.post(`/properties/${propertyId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // 画像アップロード（複数対応）
  async uploadImages(
    propertyId: number,
    images: Array<{ file: File; image_type?: string; display_order?: number; caption?: string; is_public?: boolean }>
  ): Promise<PropertyImage[]> {
    const uploadPromises = images.map((img) =>
      this.uploadImage(propertyId, img.file, {
        image_type: img.image_type,
        display_order: img.display_order,
        caption: img.caption,
        is_public: img.is_public,
      })
    );

    return Promise.all(uploadPromises);
  },

  // 画像メタデータ更新
  async updateImageMetadata(
    propertyId: number,
    imageId: number,
    data: { image_type?: string; display_order?: number; caption?: string; is_public?: boolean }
  ): Promise<PropertyImage> {
    const response = await api.put(`/properties/${propertyId}/images/${imageId}`, data);
    return response.data;
  },

  // 画像メタデータ一括更新
  async bulkUpdateImages(
    propertyId: number,
    images: Array<{ id: number; image_type?: string; display_order?: number; caption?: string; is_public?: boolean }>
  ): Promise<{ updated: number; results: Array<{ id: number; status: string }> }> {
    const response = await api.post(`/properties/${propertyId}/images/bulk`, images);
    return response.data;
  },

  // 画像削除
  async deleteImage(propertyId: number, imageId: number): Promise<void> {
    await api.delete(`/properties/${propertyId}/images/${imageId}`);
  },

  // 画像一覧取得
  async getImages(propertyId: number): Promise<PropertyImage[]> {
    const response = await api.get(`/properties/${propertyId}/images`);
    return response.data;
  },
};

// 画像型定義
export interface PropertyImage {
  id?: number;
  property_id?: number;
  image_type: string;
  file_path?: string;
  file_url?: string;
  display_order: number;
  caption: string;
  is_public: boolean;
  file?: File;
  preview?: string;
}
