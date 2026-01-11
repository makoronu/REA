/**
 * ヘルプページ関連の型定義
 */

/** カテゴリ定義（トップページのカード表示用） */
export interface HelpCategory {
  id: string;
  title: string;
  description: string;
  icon: string;
  file: string;
}

/** セクション（MDの##に対応） */
export interface HelpSection {
  id: string;
  title: string;
  items: HelpItem[];
}

/** 項目（MDの###に対応） */
export interface HelpItem {
  id: string;
  title: string;
  content: string;
}

/** MDパース結果 */
export interface ParsedHelp {
  title: string;
  description: string;
  sections: HelpSection[];
}
