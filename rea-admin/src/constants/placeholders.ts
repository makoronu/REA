/**
 * placeholder定数
 *
 * ADR-0001に基づき、固定フィールドのplaceholderを定数ファイルで一元管理。
 * 動的フィールド（column_labels対象）はDBから取得。
 *
 * メタデータ駆動ではなく定数化の理由:
 * - 開発者のみが変更
 * - 変更頻度が年1回以下
 * - 変更時にテストが必要
 */

// 認証関連
export const AUTH_PLACEHOLDERS = {
  EMAIL: 'mail@example.com',
  PASSWORD: '********',
  PASSWORD_MIN_LENGTH: '8文字以上',
  PASSWORD_CONFIRM: 'もう一度入力',
} as const;

// ユーザー管理
export const USER_PLACEHOLDERS = {
  NAME: '山田 太郎',
  EMAIL: 'user@example.com',
} as const;

// 検索
export const SEARCH_PLACEHOLDERS = {
  PROPERTY: '物件を検索... (例: 北見 1000万以下 戸建)',
  GENERIC: '検索...',
  VIEW_NAME: 'ビュー名',
} as const;

// 交通・位置
export const LOCATION_PLACEHOLDERS = {
  STATION_NAME: '駅名',
  LINE_NAME: '路線名',
  WALK_MINUTES: '徒歩(分)',
  BUS_STOP_NAME: 'バス停名',
  LINE_NAME_OPTIONAL: '路線名（任意）',
  LATITUDE: '35.681236',
  LONGITUDE: '139.767125',
} as const;

// 周辺施設
export const FACILITY_PLACEHOLDERS = {
  NAME: '施設名',
  DISTANCE_M: '距離(m)',
  WALK_MINUTES: '徒歩(分)',
} as const;

// 法規制
export const REGULATION_PLACEHOLDERS = {
  SELECT: '選択してください',
  SELECT_MULTIPLE: '選択してください（複数可）',
  COVERAGE_RATIO: '例: 60',
  FLOOR_AREA_RATIO: '例: 200',
  HEIGHT_DISTRICT: '例: 第1種高度地区',
  DISTRICT_PLAN: '地区計画名を入力',
} as const;

// その他
export const MISC_PLACEHOLDERS = {
  CAPTION: 'キャプション（任意）',
  REFORM_DETAIL: 'リフォーム内容の詳細',
  IMPORT_ID: '例: 2480',
  FLOOR_AREA: '4.0',
  FLOOR_AREA_2: '5.0',
  LINE_EXAMPLE: 'JR山手線',
  STATION_EXAMPLE: '渋谷',
  POSTAL_CODE: '123-4567',
  EMAIL_EXAMPLE: 'example@example.com',
  PHONE_EXAMPLE: '090-1234-5678',
} as const;
