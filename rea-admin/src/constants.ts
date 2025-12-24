/**
 * 定数定義
 * マジックナンバーは全てここで一元管理（DRY原則）
 */

// === 販売ステータス ===
export const SALES_STATUS = {
  SELLING: '販売中',
  SOLD: '成約済み',
  WITHDRAWN: '取下げ',
  ENDED: '販売終了',
  NEGOTIATING: '商談中',
  PREPARING: '販売準備',
} as const;

// 販売中とみなすステータス
export const ACTIVE_SALES_STATUSES = [SALES_STATUS.SELLING] as const;
// 非公開にすべきステータス
export const INACTIVE_SALES_STATUSES = [
  SALES_STATUS.SOLD,
  SALES_STATUS.WITHDRAWN,
  SALES_STATUS.ENDED,
] as const;

// === 公開ステータス ===
export const PUBLICATION_STATUS = {
  PUBLIC: '公開',
  PRIVATE: '非公開',
} as const;

// === ページ設定 ===
export const PAGE_CONFIG = {
  ITEMS_PER_PAGE: 20,
  DEBOUNCE_MS: 300,
} as const;

// === 日本円単位 ===
export const YEN_MAN = 10000;          // 万
export const YEN_OKU = 100000000;      // 億

// === 自動保存 ===
export const AUTO_SAVE_DELAY_MS = 2000;

// === 地理情報 ===
export const DEFAULT_SEARCH_RADIUS_M = 2000;  // デフォルト検索半径（メートル）
export const WALK_SPEED_M_PER_MIN = 80;       // 徒歩速度（メートル/分）

// === 価格フォーマット ===
export const formatPrice = (price: number): string => {
  if (price >= YEN_OKU) return (price / YEN_OKU).toFixed(1) + '億円';
  if (price >= YEN_MAN) return Math.round(price / YEN_MAN) + '万円';
  return price.toLocaleString() + '円';
};

// === 価格パース（文字列→数値） ===
export const parseJapanesePrice = (text: string): number | null => {
  const match = text.match(/(\d+(?:\.\d+)?)\s*(万|億)?/);
  if (!match) return null;

  let value = parseFloat(match[1]);
  if (match[2] === '万') value *= YEN_MAN;
  if (match[2] === '億') value *= YEN_OKU;
  return value;
};

// === タブグループ定義 ===
// DynamicFormで使用するタブとグループ名のマッピング
// 変更はここのみで全体に反映される

/**
 * タブグループ定義
 *
 * 各タブに含めるグループ名の配列
 * group_name は column_labels テーブルの値と一致させること
 */
export const TAB_GROUPS: {
  location: readonly string[];
  basicInfo: readonly string[];
  priceDeal: readonly string[];
  management: readonly string[];
  excluded: readonly string[];
  regulationFromLandInfo: readonly string[];
} = {
  /** 所在地・周辺情報タブ */
  location: ['所在地', '学区', '電車・鉄道', 'バス', '周辺施設'],

  /** 基本情報タブ */
  basicInfo: ['物件種別', '基本情報', 'キャッチコピー'],

  /** 価格・取引タブ */
  priceDeal: ['価格情報', '契約条件', '元請会社', '引渡・掲載'],

  /** 管理・費用タブ */
  management: ['月額費用', '費用情報', '管理情報', '備考', 'ZOHO連携'],

  /** 除外グループ（ヘッダーや専用タブで表示） */
  excluded: ['ステータス', 'システム'],

  /** 法令制限タブで表示（land_infoから除外） */
  regulationFromLandInfo: ['法規制（自動取得）', 'ハザード情報（自動取得）'],
};

/**
 * タブ情報定義
 */
export const TAB_INFO = {
  location: {
    tableName: 'properties_location',
    label: '所在地・周辺情報',
    icon: '📍',
  },
  basicInfo: {
    tableName: 'properties_basic',
    label: '基本情報',
    icon: '🏠',
  },
  priceDeal: {
    tableName: 'properties_price',
    label: '価格・取引',
    icon: '💰',
  },
  management: {
    tableName: 'properties_management',
    label: '管理・費用',
    icon: '📋',
  },
  landInfo: {
    tableName: 'land_info',
    label: '土地情報',
    icon: '🗺️',
  },
  buildingInfo: {
    tableName: 'building_info',
    label: '建物情報',
    icon: '🏗️',
  },
  regulation: {
    tableName: 'properties_regulation',
    label: '法令制限',
    icon: '📜',
  },
  registry: {
    tableName: 'properties_registry',
    label: '登記情報',
    icon: '📑',
  },
} as const;
