import { useState, useEffect, useCallback } from 'react';
import { useForm, UseFormReturn, FieldValues, DefaultValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { metadataService, ColumnWithLabel, TableInfo } from '../services/metadataService';

// バリデーションルールからZodスキーマを生成
const createZodSchema = (columns: ColumnWithLabel[]): z.ZodObject<any> => {
  const schemaFields: Record<string, z.ZodTypeAny> = {};
  
  columns.forEach(column => {
    let fieldSchema: z.ZodTypeAny;
    
    // データ型に基づいて基本スキーマを作成
    switch (column.data_type) {
      case 'integer':
      case 'bigint':
      case 'smallint':
        fieldSchema = z.number().int();
        break;
      case 'numeric':
      case 'decimal':
      case 'real':
      case 'double precision':
        fieldSchema = z.number();
        break;
      case 'boolean':
        fieldSchema = z.boolean();
        break;
      case 'date':
      case 'timestamp':
      case 'timestamp without time zone':
      case 'timestamp with time zone':
        fieldSchema = z.string(); // 日付は文字列として扱い、別途変換
        break;
      default:
        fieldSchema = z.string();
    }
    
    // NULL許可の場合
    if (column.is_nullable && !column.is_required) {
      fieldSchema = fieldSchema.optional().nullable();
    }
    
    // 文字数制限
    if (column.character_maximum_length && fieldSchema instanceof z.ZodString) {
      fieldSchema = fieldSchema.max(column.character_maximum_length);
    }
    
    // カスタムバリデーションルール（JSON形式で格納されている場合）
    if (column.validation_rules) {
      try {
        const rules = JSON.parse(column.validation_rules);
        
        if (rules.min_length && fieldSchema instanceof z.ZodString) {
          fieldSchema = fieldSchema.min(rules.min_length);
        }
        if (rules.pattern && fieldSchema instanceof z.ZodString) {
          fieldSchema = fieldSchema.regex(new RegExp(rules.pattern));
        }
        if (rules.min_value && fieldSchema instanceof z.ZodNumber) {
          fieldSchema = fieldSchema.min(rules.min_value);
        }
        if (rules.max_value && fieldSchema instanceof z.ZodNumber) {
          fieldSchema = fieldSchema.max(rules.max_value);
        }
      } catch (e) {
        // バリデーションルールのパースに失敗した場合は無視
      }
    }
    
    schemaFields[column.column_name] = fieldSchema;
  });
  
  return z.object(schemaFields);
};

// フォームの初期値を生成
const createDefaultValues = (columns: ColumnWithLabel[]): DefaultValues<FieldValues> => {
  const defaultValues: DefaultValues<FieldValues> = {};
  
  columns.forEach(column => {
    if (column.default_value !== null && column.default_value !== undefined) {
      defaultValues[column.column_name] = column.default_value;
    } else {
      // データ型に基づいてデフォルト値を設定
      switch (column.data_type) {
        case 'integer':
        case 'bigint':
        case 'smallint':
        case 'numeric':
        case 'decimal':
        case 'real':
        case 'double precision':
          defaultValues[column.column_name] = column.is_nullable ? null : 0;
          break;
        case 'boolean':
          defaultValues[column.column_name] = false;
          break;
        default:
          defaultValues[column.column_name] = column.is_nullable ? null : '';
      }
    }
  });
  
  return defaultValues;
};

interface UseMetadataFormOptions {
  tableName?: string;
  tableNames?: string[]; // 複数テーブル対応
  onSubmit: (data: any) => void | Promise<void>;
  defaultValues?: DefaultValues<FieldValues>;
}

interface UseMetadataFormReturn {
  form: UseFormReturn<FieldValues>;
  columns: ColumnWithLabel[];
  groupedColumns: Record<string, ColumnWithLabel[]>;
  tables?: TableInfo[];
  allColumns?: Record<string, ColumnWithLabel[]>;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export const useMetadataForm = ({
  tableName,
  tableNames,
  onSubmit,
  defaultValues: userDefaultValues
}: UseMetadataFormOptions): UseMetadataFormReturn => {
  const [columns, setColumns] = useState<ColumnWithLabel[]>([]);
  const [groupedColumns, setGroupedColumns] = useState<Record<string, ColumnWithLabel[]>>({});
  const [allColumns, setAllColumns] = useState<Record<string, ColumnWithLabel[]>>({});
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [schema, setSchema] = useState<z.ZodObject<any>>(z.object({}));
  
  // React Hook Form
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: userDefaultValues || {}
  });
  
  // メタデータを取得
  const fetchMetadata = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      if (tableName) {
        // 単一テーブルモード
        const columnsData = await metadataService.getTableColumnsWithLabels(tableName);
        const grouped = await metadataService.getFormColumns(tableName);
        
        setColumns(columnsData);
        setGroupedColumns(grouped);
        
        // スキーマとデフォルト値を設定
        const newSchema = createZodSchema(columnsData);
        setSchema(newSchema);
        
        const defaultValues = userDefaultValues || createDefaultValues(columnsData);
        form.reset(defaultValues);
        
      } else if (tableNames && tableNames.length > 0) {
        // 複数テーブルモード
        const tablesData = await metadataService.getPropertyTables();
        const relevantTables = tablesData.filter(t => tableNames.includes(t.table_name));
        setTables(relevantTables);
        
        const columnsMap = await metadataService.getMultipleTablesColumns(tableNames);
        setAllColumns(columnsMap);
        
        // 全カラムを統合
        const allColumnsFlat = Object.values(columnsMap).flat();
        setColumns(allColumnsFlat);
        
        // グループ化
        const grouped = allColumnsFlat.reduce((acc, column) => {
          const groupName = column.group_name || '基本情報';
          if (!acc[groupName]) {
            acc[groupName] = [];
          }
          acc[groupName].push(column);
          return acc;
        }, {} as Record<string, ColumnWithLabel[]>);
        
        setGroupedColumns(grouped);
        
        // スキーマとデフォルト値を設定
        const newSchema = createZodSchema(allColumnsFlat);
        setSchema(newSchema);
        
        const defaultValues = userDefaultValues || createDefaultValues(allColumnsFlat);
        form.reset(defaultValues);
      }
    } catch (err) {
      setError(err as Error);
      console.error('Failed to fetch metadata:', err);
    } finally {
      setIsLoading(false);
    }
  }, [tableName, tableNames, userDefaultValues]);
  
  useEffect(() => {
    fetchMetadata();
  }, [fetchMetadata]);
  
  // フォーム送信ハンドラー
  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Form submission error:', error);
      throw error;
    }
  });
  
  return {
    form: {
      ...form,
      handleSubmit: handleSubmit as unknown as UseFormReturn<FieldValues>['handleSubmit']
    },
    columns,
    groupedColumns,
    tables,
    allColumns,
    isLoading,
    error,
    refetch: fetchMetadata
  };
};

// 特定のテーブル用のカスタムフック
export const usePropertyForm = (
  onSubmit: (data: any) => void | Promise<void>,
  defaultValues?: DefaultValues<FieldValues>
) => {
  return useMetadataForm({
    tableName: 'properties',
    onSubmit,
    defaultValues
  });
};

// 全property系テーブル用のカスタムフック
export const usePropertyFullForm = (
  onSubmit: (data: any) => void | Promise<void>,
  defaultValues?: DefaultValues<FieldValues>
) => {
  const [propertyTables, setPropertyTables] = useState<string[]>([]);
  
  useEffect(() => {
    // property系テーブル名を取得
    metadataService.getPropertyTables().then(tables => {
      setPropertyTables(tables.map(t => t.table_name));
    });
  }, []);
  
  return useMetadataForm({
    tableNames: propertyTables,
    onSubmit,
    defaultValues
  });
};