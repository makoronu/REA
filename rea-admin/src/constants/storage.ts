// ローカルストレージキー定数
// 全てのストレージキーはここで一元管理する

export const STORAGE_KEYS = {
  // 認証関連
  AUTH_TOKEN: 'rea_auth_token',
  AUTH_USER: 'rea_auth_user',

  // UI状態
  PROPERTY_VIEWS: 'rea_property_views',
  PAGE_SIZE: 'rea_page_size',
  VISIBLE_COLUMNS: 'rea_visible_columns',
  SCROLL_POSITION: 'rea_scroll_position',
  SEARCH_HISTORY: 'rea_search_history',
} as const;

// 型定義
export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];
