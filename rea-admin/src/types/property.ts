// 物件の型定義 - メタデータ駆動版
//
// 注意: 以前はここに全フィールドをハードコードしていたが、
// メタデータ駆動に移行したため、最小限の定義のみ残す。
// フィールド情報は /api/v1/metadata/columns/{table_name} から動的に取得する。

/**
 * 物件データ（動的型）
 *
 * APIから返されるデータは全て Record<string, any> として扱う。
 * フィールドの存在確認は実行時に行う。
 */
export type Property = Record<string, any> & {
  // 必須フィールドのみ定義（型安全性のため）
  id: number;
};

/**
 * 物件作成時のデータ
 */
export type PropertyCreate = Omit<Property, 'id'> & {
  property_name: string; // 必須
};

/**
 * 物件更新時のデータ
 */
export type PropertyUpdate = Partial<Property>;

/**
 * 検索パラメータの型定義
 */
export interface PropertySearchParams {
  search?: string;
  property_type?: string;
  sales_status?: string;
  publication_status?: string;
  price_min?: number;
  price_max?: number;
  sale_price_min?: number;
  sale_price_max?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}

/**
 * ページネーション付きレスポンス
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// NOTE: 以前はここに全フィールドをハードコードしていた。
// メタデータ駆動では column_labels テーブルからフィールド情報を取得する。
//
// 型安全性が必要な場合は、メタデータからTypeScriptの型を自動生成する
// スクリプトを作成することを検討する。
