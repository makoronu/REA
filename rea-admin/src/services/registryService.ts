/**
 * 登記情報API
 * 表題部 + 甲区（所有権）+ 乙区（抵当権等）
 */
import { api } from './api';

// 表題部
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
  floor_area_b1?: number;
  floor_area_total?: number;
  built_date?: string;
  title_cause?: string;
  title_cause_date?: string;
  registry_office?: string;
  certified_date?: string;
  raw_pdf_path?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  // 旧カラム（後方互換）
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
}

// 甲区（所有権）
export interface KouEntry {
  id: number;
  registry_id: number;
  rank_number: string;
  purpose: string;
  reception_date?: string;
  reception_number?: string;
  owner_name: string;
  owner_address?: string;
  ownership_ratio?: string;
  cause?: string;
  cause_date?: string;
  cause_detail?: string;
  is_active: boolean;
  deletion_date?: string;
  deletion_reception_number?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// 乙区（抵当権等）
export interface OtsuEntry {
  id: number;
  registry_id: number;
  rank_number: string;
  purpose: string;
  reception_date?: string;
  reception_number?: string;
  debt_amount?: number;
  interest_rate?: string;
  damage_rate?: string;
  debtor_name?: string;
  debtor_address?: string;
  mortgagee_name?: string;
  mortgagee_address?: string;
  maximum_amount?: number;
  debt_scope?: string;
  right_holder_name?: string;
  right_holder_address?: string;
  right_purpose?: string;
  right_scope?: string;
  right_duration?: string;
  rent_amount?: string;
  cause?: string;
  cause_date?: string;
  joint_collateral_number?: string;
  is_active: boolean;
  deletion_date?: string;
  deletion_reception_number?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// 登記目的マスター
export interface RegistryPurpose {
  id: number;
  code: string;
  name: string;
  description?: string;
}

// 全情報（表題部 + 甲区 + 乙区）
export interface RegistryFull {
  registry: Registry;
  kou_entries: KouEntry[];
  otsu_entries: OtsuEntry[];
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
  // ============
  // 表題部
  // ============
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
  },

  // 全情報取得（表題部 + 甲区 + 乙区）
  async getRegistryFull(registryId: number): Promise<RegistryFull> {
    const response = await api.get(`/registries/${registryId}/full`);
    return response.data;
  },

  // ============
  // 登記目的マスター
  // ============
  async getPurposes(): Promise<{ 甲区: RegistryPurpose[]; 乙区: RegistryPurpose[] }> {
    const response = await api.get('/registries/purposes');
    return response.data;
  },

  // ============
  // 甲区（所有権）
  // ============
  async getKouEntries(registryId: number): Promise<KouEntry[]> {
    const response = await api.get(`/registries/${registryId}/kou`);
    return response.data;
  },

  async createKouEntry(registryId: number, data: Partial<KouEntry>): Promise<KouEntry> {
    const response = await api.post(`/registries/${registryId}/kou`, data);
    return response.data;
  },

  async updateKouEntry(entryId: number, data: Partial<KouEntry>): Promise<KouEntry> {
    const response = await api.put(`/registries/kou/${entryId}`, data);
    return response.data;
  },

  async deleteKouEntry(entryId: number): Promise<void> {
    await api.delete(`/registries/kou/${entryId}`);
  },

  // ============
  // 乙区（抵当権等）
  // ============
  async getOtsuEntries(registryId: number): Promise<OtsuEntry[]> {
    const response = await api.get(`/registries/${registryId}/otsu`);
    return response.data;
  },

  async createOtsuEntry(registryId: number, data: Partial<OtsuEntry>): Promise<OtsuEntry> {
    const response = await api.post(`/registries/${registryId}/otsu`, data);
    return response.data;
  },

  async updateOtsuEntry(entryId: number, data: Partial<OtsuEntry>): Promise<OtsuEntry> {
    const response = await api.put(`/registries/otsu/${entryId}`, data);
    return response.data;
  },

  async deleteOtsuEntry(entryId: number): Promise<void> {
    await api.delete(`/registries/otsu/${entryId}`);
  },
};
