// 地理情報API
import { api } from './api';

export interface NearestStation {
  station_id: number;
  station_name: string;
  line_name: string | null;
  company_name: string | null;
  distance_meters: number;
  walk_minutes: number;
}

export interface NearestStationsResponse {
  stations: NearestStation[];
  latitude: number;
  longitude: number;
}

export interface GeocodeResponse {
  address: string;
  latitude: number;
  longitude: number;
  source: string;
}

// 物件に保存する最寄駅情報の型
export interface PropertyStation {
  station_name: string;
  line_name: string;
  walk_minutes: number;
}

export const geoService = {
  // 座標から最寄駅を検索
  async getNearestStations(
    lat: number,
    lng: number,
    radius: number = 2000,
    limit: number = 10
  ): Promise<NearestStationsResponse> {
    const response = await api.get('/geo/nearest-stations', {
      params: { lat, lng, radius, limit }
    });
    return response.data;
  },

  // 住所から座標を取得
  async geocode(address: string): Promise<GeocodeResponse> {
    const response = await api.get('/geo/geocode', {
      params: { address }
    });
    return response.data;
  },

  // 物件の最寄駅を自動設定（バックエンドで処理）
  async setPropertyNearestStations(
    propertyId: number,
    limit: number = 3
  ): Promise<{ property_id: number; stations_set: number; transportation: PropertyStation[] }> {
    const response = await api.post(`/geo/properties/${propertyId}/set-nearest-stations`, null, {
      params: { limit }
    });
    return response.data;
  }
};
