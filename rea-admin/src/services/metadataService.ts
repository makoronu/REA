import axios from 'axios';
import { API_BASE_URL } from '../config';
import { API_PATHS } from '../constants/apiPaths';
import { PROPERTY_FORM_TABLES } from '../constants/tables';

// 型定義
export interface TableInfo {
  table_name: string;
  table_type: string;
  table_comment?: string;
  column_count: number;
  has_primary_key: boolean;
}

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

export interface ColumnWithLabel extends ColumnInfo {
  label_ja: string;
  label_en: string;
  description?: string;
  input_type: string;
  validation_rules?: string;
  display_order: number;
  is_required: boolean;
  is_searchable: boolean;
  is_display_list: boolean;
  group_name: string;
  placeholder?: string;
  help_text?: string;
  default_value?: any;
  options?: string;
  visible_for?: string[] | null; // 物件種別による表示制御
}

export interface TableDetails {
  table_name: string;
  record_count: number;
  columns: ColumnInfo[];
  column_count: number;
}

export interface ValidationRules {
  available_rules: Record<string, string>;
  input_types: Record<string, string>;
}

class MetadataService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}${API_PATHS.METADATA.BASE}`;
  }

  /**
   * 全テーブル一覧を取得
   */
  async getAllTables(): Promise<TableInfo[]> {
    try {
      const response = await axios.get<TableInfo[]>(`${this.baseURL}/tables`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tables:', error);
      throw error;
    }
  }

  /**
   * property系のテーブルのみ取得 - 新テーブル構造に対応
   * テーブル名はconstants/tables.tsで一元管理
   */
  async getPropertyTables(): Promise<TableInfo[]> {
    const allTables = await this.getAllTables();

    return allTables.filter(table =>
      (PROPERTY_FORM_TABLES as readonly string[]).includes(table.table_name)
    );
  }

  /**
   * テーブルの詳細情報を取得
   */
  async getTableDetails(tableName: string): Promise<TableDetails> {
    try {
      const response = await axios.get<TableDetails>(
        `${this.baseURL}/tables/${tableName}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching table details for ${tableName}:`, error);
      throw error;
    }
  }

  /**
   * テーブルのカラム情報をラベル付きで取得
   */
  async getTableColumnsWithLabels(tableName: string): Promise<ColumnWithLabel[]> {
    try {
      const response = await axios.get<ColumnWithLabel[]>(
        `${this.baseURL}/columns/${tableName}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching columns for ${tableName}:`, error);
      throw error;
    }
  }

  /**
   * 複数テーブルのカラム情報を一括取得
   */
  async getMultipleTablesColumns(
    tableNames: string[]
  ): Promise<Record<string, ColumnWithLabel[]>> {
    try {
      const promises = tableNames.map(tableName =>
        this.getTableColumnsWithLabels(tableName)
      );
      const results = await Promise.all(promises);
      
      const columnsMap: Record<string, ColumnWithLabel[]> = {};
      tableNames.forEach((tableName, index) => {
        columnsMap[tableName] = results[index];
      });
      
      return columnsMap;
    } catch (error) {
      console.error('Error fetching multiple tables columns:', error);
      throw error;
    }
  }

  /**
   * ENUM型の値一覧を取得
   */
  async getEnumValues(enumName: string): Promise<string[]> {
    try {
      const response = await axios.get<string[]>(
        `${this.baseURL}/enums/${enumName}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching enum values for ${enumName}:`, error);
      throw error;
    }
  }

  /**
   * バリデーションルールの一覧を取得
   */
  async getValidationRules(): Promise<ValidationRules> {
    try {
      const response = await axios.get<ValidationRules>(
        `${this.baseURL}/validation/rules`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching validation rules:', error);
      throw error;
    }
  }

  /**
   * フォーム用のグループ化されたカラム情報を取得
   */
  async getFormColumns(tableName: string): Promise<Record<string, ColumnWithLabel[]>> {
    const columns = await this.getTableColumnsWithLabels(tableName);
    
    // グループ名でカラムをグループ化
    const grouped = columns.reduce((acc, column) => {
      const groupName = column.group_name || '基本情報';
      if (!acc[groupName]) {
        acc[groupName] = [];
      }
      acc[groupName].push(column);
      return acc;
    }, {} as Record<string, ColumnWithLabel[]>);

    // 各グループ内でdisplay_orderでソート
    Object.keys(grouped).forEach(groupName => {
      grouped[groupName].sort((a, b) => a.display_order - b.display_order);
    });

    return grouped;
  }

  /**
   * 全property系テーブルの統合フォームデータを取得 - 新テーブル構造対応
   */
  async getPropertyFormData(): Promise<{
    tables: TableInfo[];
    columnsMap: Record<string, ColumnWithLabel[]>;
    groupedColumns: Record<string, Record<string, ColumnWithLabel[]>>;
  }> {
    // property系テーブルを取得（新しい5テーブル）
    const tables = await this.getPropertyTables();
    const tableNames = tables.map(t => t.table_name);
    
    // 全テーブルのカラム情報を取得
    const columnsMap = await this.getMultipleTablesColumns(tableNames);
    
    // 各テーブルのカラムをグループ化
    const groupedColumns: Record<string, Record<string, ColumnWithLabel[]>> = {};
    for (const tableName of tableNames) {
      const columns = columnsMap[tableName];
      const grouped = columns.reduce((acc, column) => {
        const groupName = column.group_name || '基本情報';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>);
      
      groupedColumns[tableName] = grouped;
    }
    
    return {
      tables,
      columnsMap,
      groupedColumns
    };
  }

  /**
   * フィルター用のオプション一覧を取得（メタデータ駆動）
   * color/bgはmaster_options.metadataから取得される
   */
  async getFilterOptions(): Promise<{
    sales_status?: { value: string; label: string; color?: string; bg?: string }[];
    publication_status?: { value: string; label: string; color?: string; bg?: string }[];
    property_type?: { value: string; label: string }[];
    property_type_simple?: { value: string; label: string; group?: string }[];
  }> {
    try {
      const response = await axios.get(`${this.baseURL}/filter-options`);
      return response.data;
    } catch (error) {
      console.error('Error fetching filter options:', error);
      throw error;
    }
  }

  /**
   * カテゴリコード別にマスタオプションを取得（メタデータ駆動）
   *
   * @param categoryCode - カテゴリコード（road_direction, room_type等）
   * @returns オプション配列（拡張フィールド含む）
   */
  async getOptionsByCategory(categoryCode: string): Promise<MasterOption[]> {
    try {
      const response = await axios.get<MasterOption[]>(
        `${this.baseURL}/options/${categoryCode}`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching options for ${categoryCode}:`, error);
      throw error;
    }
  }

  /**
   * ステータス連動設定を取得（メタデータ駆動）
   * 販売ステータス→公開ステータスの連動ロジックに使用
   */
  async getStatusSettings(): Promise<StatusSettings> {
    try {
      const response = await axios.get<StatusSettings>(
        `${this.baseURL}/status-settings`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching status settings:', error);
      throw error;
    }
  }

  /**
   * 全マスタカテゴリ一覧を取得
   */
  async getAllCategories(): Promise<MasterCategory[]> {
    try {
      const response = await axios.get<MasterCategory[]>(
        `${this.baseURL}/categories`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }
}

// マスタオプション型（拡張フィールド対応）
export interface MasterOption {
  value: string;
  label: string;
  display_order?: number;
  is_default?: boolean;
  allows_publication?: boolean;
  linked_status?: string;
  ui_color?: string;
  shows_contractor?: boolean;
  category_icon?: string;
  metadata?: Record<string, any>;
}

// ステータス連動設定型
export interface StatusSettings {
  sales_status: {
    default: string | null;
    options: {
      value: string;
      label: string;
      ui_color?: string;
      allows_publication?: boolean;
    }[];
    publication_link: Record<string, string>;
  };
  publication_status: {
    default: string | null;
    options: {
      value: string;
      label: string;
      ui_color?: string;
    }[];
  };
  transaction_type: {
    contractor_required: string[];
  };
}

// マスタカテゴリ型
export interface MasterCategory {
  code: string;
  name: string;
  description?: string;
  icon?: string;
  display_order?: number;
}

// シングルトンインスタンスをエクスポート
export const metadataService = new MetadataService();