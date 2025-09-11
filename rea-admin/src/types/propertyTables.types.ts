// 分割テーブルの型定義

// メインテーブル
export interface PropertyMain {
  id: number;
  homes_record_id?: string;
  company_property_number?: string;
  status?: string;
  property_type?: string;
  investment_property?: string;
  building_property_name?: string;
  building_name_kana?: string;
  property_name_public?: string;
  total_units?: number;
  vacant_units?: number;
  vacant_units_detail?: string;
  created_at?: string;
  updated_at?: string;
}

// 契約情報（元請会社情報含む）
export interface PropertyContract {
  id?: number;
  property_id: number;
  contract_period_years?: number;
  contract_period_months?: number;
  contract_period_type?: string;
  current_status?: string;
  move_in_timing?: string;
  move_in_date?: string;
  move_in_period?: string;
  property_manager_name?: string;
  transaction_type?: string;
  listing_confirmation_date?: string;
  tenant_placement?: string;
  brokerage_contract_date?: string;
  brokerage_fee?: number;
  commission_split_ratio?: number;
  contract_type?: string;
  // 元請会社情報
  contractor_company_name?: string;
  contractor_contact_person?: string;
  contractor_phone?: string;
  contractor_email?: string;
  contractor_address?: string;
  contractor_license_number?: string;
}

// 統合型
export interface PropertyFullData {
  main: PropertyMain;
  contract?: PropertyContract;
  // 他のテーブルも追加予定
}
