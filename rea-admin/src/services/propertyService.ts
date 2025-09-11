// 物件関連のAPI呼び出し
import { api } from './api';
import { Property } from '../types/property';

export const propertyService = {
  // 物件一覧取得
  async getProperties(params?: any): Promise<Property[]> {
    const response = await api.get('/properties', { params });
    return response.data;
  },

  // 物件詳細取得
  async getProperty(id: number): Promise<Property> {
    const response = await api.get(`/properties/${id}`);
    return response.data;
  },

  // 物件更新
  async updateProperty(id: number, data: Partial<Property>): Promise<Property> {
    const response = await api.put(`/properties/${id}`, data);
    return response.data;
  },

  // 物件作成
  async createProperty(data: Partial<Property>): Promise<Property> {
    const response = await api.post('/properties', data);
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
      
      return response.data.url; // アップロードされた画像のURL
    });

    return Promise.all(uploadPromises);
  },

  // 画像削除
  async deleteImage(propertyId: number, imageUrl: string): Promise<void> {
    // URLからファイル名を抽出
    const fileName = imageUrl.split('/').pop();
    await api.delete(`/properties/${propertyId}/images/${fileName}`);
  },

  // 画像一覧を含む物件情報を更新
  async updatePropertyWithImages(id: number, data: Partial<Property>, imageUrls: string[]): Promise<Property> {
    const updateData = {
      ...data,
      images: imageUrls // 画像URLの配列を含める
    };
    return this.updateProperty(id, updateData);
  },
};