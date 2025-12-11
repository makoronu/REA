import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

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
    this.baseURL = `${API_BASE_URL}/api/v1/metadata`;
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
   */
  async getPropertyTables(): Promise<TableInfo[]> {
    const allTables = await this.getAllTables();
    
    // 新しい5テーブル構造に対応
    const propertyTableNames = [
      'properties',
      'land_info', 
      'building_info',
      'amenities',
      'property_images'
    ];
    
    return allTables.filter(table => 
      propertyTableNames.includes(table.table_name)
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
}

// シングルトンインスタンスをエクスポート
export const metadataService = new MetadataService();