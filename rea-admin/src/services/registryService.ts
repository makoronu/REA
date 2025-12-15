/**
 * 登記情報API
 */
import { api } from './api';

export interface Registry {
  id: number;
  property_id: number;
  registry_type: string;
  location?: string;
  chiban?: string;
  land_category?: string;
  land_area?: number;
  building_number?: string;
  building_type?: string;
  building_structure?: string;
  floor_area_1f?: number;
  floor_area_2f?: number;
  floor_area_3f?: number;
  floor_area_total?: number;
  built_date?: string;
  owner_name?: string;
  owner_address?: string;
  ownership_ratio?: string;
  ownership_cause?: string;
  ownership_date?: string;
  mortgage_holder?: string;
  mortgage_amount?: number;
  mortgage_date?: string;
  other_rights?: Record<string, unknown>;
  registration_number?: string;
  registry_office?: string;
  certified_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface RegistryMetadataColumn {
  name: string;
  label: string;
  type: string;
  group: string;
  required: boolean;
  description?: string;
  master_category_code?: string;
}

export interface RegistryMetadata {
  columns: RegistryMetadataColumn[];
  groups: Record<string, RegistryMetadataColumn[]>;
}

export const registryService = {
  // 物件の登記一覧取得
  async getPropertyRegistries(propertyId: number): Promise<Registry[]> {
    const response = await api.get(`/properties/${propertyId}/registries`);
    return response.data.items;
  },

  // 登記詳細取得
  async getRegistry(registryId: number): Promise<Registry> {
    const response = await api.get(`/registries/${registryId}`);
    return response.data;
  },

  // 登記追加
  async createRegistry(propertyId: number, data: Partial<Registry>): Promise<Registry> {
    const response = await api.post(`/properties/${propertyId}/registries`, data);
    return response.data;
  },

  // 登記更新
  async updateRegistry(registryId: number, data: Partial<Registry>): Promise<Registry> {
    const response = await api.put(`/registries/${registryId}`, data);
    return response.data;
  },

  // 登記削除
  async deleteRegistry(registryId: number): Promise<void> {
    await api.delete(`/registries/${registryId}`);
  },

  // メタデータ取得
  async getMetadata(): Promise<RegistryMetadata> {
    const response = await api.get('/registries/metadata');
    return response.data;
  }
};
