// 物件の型定義（バックエンドモデルに合わせて修正）
export interface Property {
  // 基本情報
  id: number;
  title: string;
  price: number;
  price_unit?: string;

  // 元請会社情報
  contractor_company_name?: string;
  contractor_contact_person?: string;
  contractor_phone?: string;
  contractor_email?: string;
  contractor_address?: string;
  contractor_license_number?: string;

  // 物件詳細
  property_type?: string;
  building_structure?: string;
  floors_total?: number;
  floor_current?: number;

  // 面積・間取り
  area_building?: number;
  area_land?: number;
  layout?: string;
  rooms?: number;

  // 築年・駅情報
  built_year?: number;
  station_name?: string;
  station_walk_time?: number;
  station_line?: string;

  // 住所
  prefecture?: string;
  city?: string;
  address?: string;

  // JSON型フィールド
  equipments?: string[];
  images?: string[];
  transportation?: { station_name: string; line_name: string; walk_minutes: number }[];

  // 緯度経度
  latitude?: number;
  longitude?: number;

  // ホームズ連携
  homes_id?: string;
  homes_url?: string;

  // 管理情報
  description?: string;
  is_active?: boolean;
  source?: string;
  created_at?: string;
  updated_at?: string;
}

// フォーム用の型定義
export interface PropertyFormData extends Omit<Property, 'id' | 'created_at' | 'updated_at'> {
  // フォーム用の追加フィールドがあれば追加
}

// 検索パラメータの型定義
export interface PropertySearchParams {
  price_min?: number;
  price_max?: number;
  area_min?: number;
  area_max?: number;
  property_type?: string;
  prefecture?: string;
  city?: string;
  station_name?: string;
  layout?: string;
  contractor_company_name?: string;
  contractor_contact_person?: string;
  contractor_license_number?: string;
  skip?: number;
  limit?: number;
}