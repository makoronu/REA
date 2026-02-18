/**
 * 定数定義
 * マジックナンバーは全てここで一元管理（DRY原則）
 */

// === 販売ステータス ===
export const SALES_STATUS = {
  ASSESSMENT: '査定中',
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
  MEMBER: '会員公開',
  PRE_CHECK: '公開前確認',
} as const;

// === ページ設定 ===
export const PAGE_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  DEBOUNCE_MS: 300,
} as const;

// 表示件数オプション
export const PAGE_SIZE_OPTIONS = [20, 50, 100] as const;

// === 日本円単位 ===
export const YEN_MAN = 10000;          // 万
export const YEN_OKU = 100000000;      // 億

// === メッセージ表示 ===
export const MESSAGE_TIMEOUT_MS = 3000;       // 通常メッセージ自動消去（ms）
export const LONG_MESSAGE_TIMEOUT_MS = 5000;  // エラー・重要メッセージ自動消去（ms）

// === 自動保存 ===
export const AUTO_SAVE_DELAY_MS = 2000;

// === 地図タイル ===
export const MAP_TILES = {
  /** 国土地理院 淡色地図 */
  GSI_PALE: {
    URL: 'https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png',
    ATTRIBUTION: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>',
    MAX_ZOOM: 18,
  },
  /** OpenStreetMap */
  OSM: {
    URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  },
} as const;

// === Leafletアイコン ===
export const LEAFLET_ICON_URLS = {
  MARKER_RETINA: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  MARKER: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  SHADOW: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
} as const;

// === 外部API ===
export const EXTERNAL_API = {
  /** 郵便番号検索（zipcloud） */
  ZIPCLOUD: 'https://zipcloud.ibsnet.co.jp/api/search',
} as const;

// === 用途地域カラーマッピング ===
export const ZONE_COLORS: Record<number, string> = {
  1: '#00FF00',   // 第一種低層住居専用
  2: '#80FF00',   // 第二種低層住居専用
  3: '#FFFF00',   // 第一種中高層住居専用
  4: '#FFCC00',   // 第二種中高層住居専用
  5: '#FF9900',   // 第一種住居
  6: '#FF6600',   // 第二種住居
  7: '#FF3300',   // 準住居
  8: '#FF00FF',   // 近隣商業
  9: '#FF0000',   // 商業
  10: '#00FFFF',  // 準工業
  11: '#0080FF',  // 工業
  12: '#0000FF',  // 工業専用
  21: '#90EE90',  // 田園住居
  99: '#CCCCCC',  // 無指定
} as const;

// === 地理情報 ===
export const DEFAULT_SEARCH_RADIUS_M = 2000;  // デフォルト検索半径（メートル）
export const WALK_SPEED_M_PER_MIN = 80;       // 徒歩速度（メートル/分）

// === 検索パラメータ設定 ===
export const GEO_SEARCH_CONFIG = {
  // 最寄駅検索
  STATION: {
    RADIUS_M: 5000,      // 検索半径（メートル）
    LIMIT: 15,           // 最大取得件数
  },
  // バス停検索
  BUS_STOP: {
    LIMIT: 15,           // 最大取得件数
  },
  // 周辺施設検索
  FACILITY: {
    LIMIT_PER_CATEGORY: 5,  // カテゴリあたりの最大件数
  },
  // 最寄駅設定（物件保存用）
  PROPERTY_STATIONS: {
    LIMIT: 3,            // 物件に保存する最寄駅数
  },
  // geoService用デフォルト
  API_DEFAULT: {
    LIMIT: 10,           // API呼び出しのデフォルトlimit
  },
} as const;

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
