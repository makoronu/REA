// 地理情報API
import { api } from './api';
import { DEFAULT_SEARCH_RADIUS_M } from '../constants';

// 郵便番号検索結果
export interface PostalCodeResult {
  zipcode: string;
  prefcode: string;
  address1: string;  // 都道府県
  address2: string;  // 市区町村
  address3: string;  // 町域
}

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
  // 郵便番号から住所を検索（zipcloud API - 無料）
  async searchByPostalCode(postalCode: string): Promise<PostalCodeResult | null> {
    // ハイフンを除去して7桁にする
    const cleanCode = postalCode.replace(/[^0-9]/g, '');
    if (cleanCode.length !== 7) {
      return null;
    }

    try {
      const response = await fetch(
        `https://zipcloud.ibsnet.co.jp/api/search?zipcode=${cleanCode}`
      );
      const data = await response.json();

      if (data.status === 200 && data.results && data.results.length > 0) {
        const result = data.results[0];
        return {
          zipcode: result.zipcode,
          prefcode: result.prefcode,
          address1: result.address1,
          address2: result.address2,
          address3: result.address3
        };
      }
      return null;
    } catch (error) {
      console.error('郵便番号検索エラー:', error);
      return null;
    }
  },

  // 座標から最寄駅を検索
  async getNearestStations(
    lat: number,
    lng: number,
    radius: number = DEFAULT_SEARCH_RADIUS_M,
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
