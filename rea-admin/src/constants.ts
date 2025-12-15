/**
 * 定数定義
 * マジックナンバーは全てここで一元管理（DRY原則）
 */

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
