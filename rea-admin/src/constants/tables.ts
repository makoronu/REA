// テーブル名定数
// バックエンドのshared/config/tables.pyと同期すること

// 物件関連テーブル（フォーム表示対象）
export const PROPERTY_FORM_TABLES = [
  'properties',
  'building_info',
  'land_info',
  'amenities',
  'property_images',
] as const;

// 物件関連全テーブル（CRUD対象）
export const PROPERTY_TABLES = [
  ...PROPERTY_FORM_TABLES,
  'property_locations',
  'property_registries',
] as const;

// 型定義
export type PropertyFormTable = typeof PROPERTY_FORM_TABLES[number];
export type PropertyTable = typeof PROPERTY_TABLES[number];
