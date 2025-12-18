/**
 * メタデータ関連の型定義
 *
 * このファイルは column_labels, master_options からの
 * データ型を一元管理する。
 *
 * 重要: any型は禁止。全てのデータに明確な型を定義する。
 */

// ============================================
// 選択肢（Options）の型定義
// ============================================

/**
 * 選択肢の標準形式
 *
 * API、フロントエンド全てでこの形式を使用する。
 * 文字列形式（"1:ラベル,2:ラベル"）は禁止。
 */
export interface OptionType {
  value: string;
  label: string;
  group?: string;      // グループ化が必要な場合
  color?: string;      // バッジ表示用
  bg?: string;         // 背景色
  disabled?: boolean;  // 選択不可の場合
}

/**
 * マスターオプション（DB: master_options）
 */
export interface MasterOption {
  id: number;
  category_id: number;
  option_code: string;
  option_value: string;
  display_order: number;
  is_active: boolean;
  metadata?: Record<string, string | number | boolean>;
}

/**
 * マスターカテゴリ（DB: master_categories）
 */
export interface MasterCategory {
  id: number;
  category_code: string;
  category_name: string;
  description?: string;
}

// ============================================
// カラムメタデータの型定義
// ============================================

/**
 * 入力タイプの列挙
 */
export type InputType =
  | 'text'
  | 'number'
  | 'textarea'
  | 'select'
  | 'multi_select'
  | 'checkbox'
  | 'radio'
  | 'date'
  | 'datetime'
  | 'email'
  | 'tel'
  | 'url'
  | 'password'
  | 'file'
  | 'image'
  | 'hidden'
  | 'readonly';

/**
 * バリデーションルール
 */
export interface ValidationRule {
  type: 'required' | 'min' | 'max' | 'minLength' | 'maxLength' | 'pattern' | 'email' | 'url' | 'custom';
  value?: string | number;
  message?: string;
}

/**
 * カラム情報（DB情報）
 */
export interface ColumnInfo {
  column_name: string;
  data_type: string;
  character_maximum_length?: number;
  numeric_precision?: number;
  numeric_scale?: number;
  is_nullable: boolean;
  column_default?: string;
  ordinal_position: number;
  column_comment?: string;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  foreign_table_name?: string;
  foreign_column_name?: string;
}

/**
 * カラムメタデータ（ラベル付き）
 *
 * 重要: optionsはOptionType[]またはnull
 * 文字列形式は使用しない
 */
export interface ColumnMetadata extends ColumnInfo {
  // ラベル情報
  label_ja: string;
  label_en: string;
  description?: string;

  // 入力設定
  input_type: InputType;
  validation_rules?: ValidationRule[];

  // 表示設定
  display_order: number;
  is_required: boolean;
  is_searchable: boolean;
  is_display_list: boolean;
  group_name: string;

  // UI補助
  placeholder?: string;
  help_text?: string;
  default_value?: string | number | boolean | null;

  // 選択肢（統一形式）
  options: OptionType[] | null;

  // 物件種別による表示制御
  visible_for?: string[] | null;
}

// ============================================
// API レスポンス型
// ============================================

/**
 * テーブル情報
 */
export interface TableInfo {
  table_name: string;
  table_type: string;
  table_comment?: string;
  column_count: number;
  has_primary_key: boolean;
}

/**
 * テーブル詳細
 */
export interface TableDetails {
  table_name: string;
  record_count: number;
  columns: ColumnInfo[];
  column_count: number;
}

/**
 * フィルターオプション（一覧画面用）
 */
export interface FilterOptions {
  sales_status: OptionType[];
  publication_status: OptionType[];
  property_type: OptionType[];
  property_type_simple: OptionType[];
}

/**
 * バリデーションルール一覧
 */
export interface ValidationRulesConfig {
  available_rules: Record<string, string>;
  input_types: Record<string, string>;
}

// ============================================
// フォーム関連の型定義
// ============================================

/**
 * グループ化されたカラム
 */
export type GroupedColumns = Record<string, ColumnMetadata[]>;

/**
 * テーブル別グループ化カラム
 */
export type TableGroupedColumns = Record<string, GroupedColumns>;

/**
 * フォームデータ
 */
export interface PropertyFormData {
  tables: TableInfo[];
  columnsMap: Record<string, ColumnMetadata[]>;
  groupedColumns: TableGroupedColumns;
}

// ============================================
// 型ガード関数
// ============================================

/**
 * OptionType配列かどうかを判定
 */
export function isOptionTypeArray(value: unknown): value is OptionType[] {
  if (!Array.isArray(value)) return false;
  if (value.length === 0) return true;
  return value.every(item =>
    typeof item === 'object' &&
    item !== null &&
    'value' in item &&
    'label' in item &&
    typeof item.value === 'string' &&
    typeof item.label === 'string'
  );
}

/**
 * ColumnMetadataかどうかを判定
 */
export function isColumnMetadata(value: unknown): value is ColumnMetadata {
  if (typeof value !== 'object' || value === null) return false;
  const col = value as Record<string, unknown>;
  return (
    typeof col.column_name === 'string' &&
    typeof col.label_ja === 'string' &&
    typeof col.input_type === 'string'
  );
}
