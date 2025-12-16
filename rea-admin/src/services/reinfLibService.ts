/**
 * 不動産情報ライブラリAPI サービス
 *
 * 国土交通省の不動産情報ライブラリAPIと連携
 */
import { api } from './api';

// 規制情報の型
export interface RegulationData {
  [key: string]: string | undefined;
}

export interface AllRegulations {
  use_area: RegulationData | null;
  fire_prevention: RegulationData | null;
  flood: RegulationData | null;
  landslide: RegulationData | null;
  tsunami: RegulationData | null;
  storm_surge: RegulationData | null;
  location_optimization: RegulationData | null;
  district_plan: RegulationData | null;
  planned_road: RegulationData | null;
}

export interface RegulationsResponse {
  status: string;
  coordinates: { lat: number; lng: number };
  regulations: AllRegulations;
}

export interface HazardResponse {
  status: string;
  has_risk: boolean;
  data: {
    flood: RegulationData | null;
    landslide: RegulationData | null;
    tsunami: RegulationData | null;
    storm_surge: RegulationData | null;
  };
}

export interface UseAreaResponse {
  status: string;
  data: RegulationData | null;
  message?: string;
}

// GeoJSON型
export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: number[][][] | number[][][][];
  };
  properties: Record<string, unknown>;
}

export interface GeoJSON {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export const reinfLibService = {
  /**
   * 全規制情報を取得
   */
  async getRegulations(lat: number, lng: number): Promise<RegulationsResponse> {
    const response = await api.get('/reinfolib/regulations', { params: { lat, lng } });
    return response.data;
  },

  /**
   * 用途地域を取得
   */
  async getUseArea(lat: number, lng: number): Promise<UseAreaResponse> {
    const response = await api.get('/reinfolib/use-area', { params: { lat, lng } });
    return response.data;
  },

  /**
   * ハザード情報を取得
   */
  async getHazard(lat: number, lng: number): Promise<HazardResponse> {
    const response = await api.get('/reinfolib/hazard', { params: { lat, lng } });
    return response.data;
  },

  /**
   * MAP表示用のGeoJSONを取得
   */
  async getTileGeoJSON(apiCode: string, lat: number, lng: number): Promise<GeoJSON> {
    const response = await api.get(`/reinfolib/tile/${apiCode}`, { params: { lat, lng } });
    return response.data;
  },

  /**
   * 利用可能なAPI一覧を取得
   */
  async getAvailableApis(): Promise<Record<string, { name: string; type: string }>> {
    const response = await api.get('/reinfolib/apis');
    return response.data;
  }
};
