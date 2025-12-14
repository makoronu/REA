// 物件の型定義（APIレスポンスに合わせて修正）
export interface Property {
  // 基本情報
  id: number;
  company_property_number?: string;
  external_property_id?: string;
  property_name?: string;
  property_name_kana?: string;
  property_name_public?: string;
  property_type?: string;
  investment_property?: boolean;

  // 販売情報
  sales_status?: string;
  publication_status?: string;
  affiliated_group?: string;
  priority_score?: number;
  property_url?: string;

  // 価格情報
  sale_price?: number;
  price_per_tsubo?: number;
  price_status?: string;
  tax_type?: string;
  yield_rate?: number;
  current_yield?: number;

  // 取引情報
  transaction_type?: string;
  brokerage_fee?: number;
  commission_split_ratio?: number;
  brokerage_contract_date?: string;
  listing_start_date?: string;
  listing_confirmation_date?: string;

  // 引渡し情報
  delivery_date?: string;
  delivery_timing?: string;
  current_status?: string;
  move_in_consultation?: string;

  // 管理費用
  management_fee?: number;
  repair_reserve_fund?: number;
  repair_reserve_fund_base?: number;
  parking_fee?: number;
  housing_insurance?: number;

  // 元請会社情報
  contractor_company_name?: string;
  contractor_contact_person?: string;
  contractor_phone?: string;
  contractor_email?: string;
  contractor_address?: string;
  contractor_license_number?: string;

  // 担当者・メモ
  property_manager_name?: string;
  internal_memo?: string;

  // 管理情報
  created_at?: string;
  updated_at?: string;

  // 互換性のための追加フィールド
  latitude?: number;
  longitude?: number;
  images?: string[];
  transportation?: { station_name: string; line_name: string; walk_minutes: number }[];
}

// フォーム用の型定義（互換性のため）
export interface PropertyFormData extends Omit<Property, 'id' | 'created_at' | 'updated_at'> {}

// 検索パラメータの型定義
export interface PropertySearchParams {
  search?: string;
  property_type?: string;
  sales_status?: string;
  publication_status?: string;
  price_min?: number;
  price_max?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}

// ページネーション付きレスポンス
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
