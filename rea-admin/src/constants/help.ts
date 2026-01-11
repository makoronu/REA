/**
 * ヘルプページ関連の定数
 * ハードコーディング防止のため、カテゴリ情報を一元管理
 */

import { HelpCategory } from '../types/help';

/** MDファイルの配置パス */
export const HELP_BASE_PATH = '/manuals';

/** ヘルプカテゴリ一覧 */
export const HELP_CATEGORIES: HelpCategory[] = [
  {
    id: 'index',
    title: '基本操作',
    description: '物件一覧・新規登録・保存の基本操作',
    icon: '📖',
    file: '00_index.md',
  },
  {
    id: 'property',
    title: '物件情報',
    description: '基本情報・所在地・価格・ステータス',
    icon: '🏠',
    file: '01_property.md',
  },
  {
    id: 'land',
    title: '土地情報',
    description: '法規制・接道・土地詳細',
    icon: '🌍',
    file: '02_land.md',
  },
  {
    id: 'building',
    title: '建物情報',
    description: '建物・居住・駐車場・管理',
    icon: '🏢',
    file: '03_building.md',
  },
  {
    id: 'glossary',
    title: '用語集',
    description: '不動産用語を検索',
    icon: '📚',
    file: '99_glossary.md',
  },
];

/** カテゴリIDからカテゴリを取得 */
export const getHelpCategoryById = (id: string): HelpCategory | undefined => {
  return HELP_CATEGORIES.find((cat) => cat.id === id);
};

/** ファイル名からカテゴリを取得 */
export const getHelpCategoryByFile = (file: string): HelpCategory | undefined => {
  return HELP_CATEGORIES.find((cat) => cat.file === file);
};
