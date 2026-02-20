import { useState, useEffect, useCallback } from 'react';
import { useForm, UseFormReturn, FieldValues, DefaultValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { metadataService, ColumnWithLabel, TableInfo } from '../services/metadataService';

// テキスト型かどうか判定
const isTextType = (dataType: string): boolean => {
  return ['character varying', 'text', 'character', 'varchar'].includes(dataType.toLowerCase());
};

// バリデーションルールからZodスキーマを生成
// メタデータ駆動: is_requiredフラグに基づき必須テキストフィールドのみ事前検証
// それ以外のバリデーションはバックエンドで実施
const createZodSchema = (columns: ColumnWithLabel[]): z.ZodObject<any> => {
  const schemaFields: Record<string, z.ZodTypeAny> = {};

  columns.forEach(column => {
    if (column.is_required && isTextType(column.data_type)) {
      // 必須テキストフィールド: null/undefined→空文字変換後、空文字を禁止
      schemaFields[column.column_name] = z.preprocess(
        (val) => (val === null || val === undefined ? '' : val),
        z.string().min(1, `${column.label_ja || column.column_name}は必須です`)
      );
    } else {
      schemaFields[column.column_name] = z.any().optional();
    }
  });

  return z.object(schemaFields).passthrough();
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
  onValidationError?: (message: string) => void;
}

interface UseMetadataFormReturn {
  form: UseFormReturn<FieldValues>;
  // handleSubmitは引数なしで呼び出せる形式（コールバックはhook内で設定済み）
  submitForm: () => Promise<void>;
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
  defaultValues: userDefaultValues,
  onValidationError,
}: UseMetadataFormOptions): UseMetadataFormReturn => {
  const [columns, setColumns] = useState<ColumnWithLabel[]>([]);
  const [groupedColumns, setGroupedColumns] = useState<Record<string, ColumnWithLabel[]>>({});
  const [allColumns, setAllColumns] = useState<Record<string, ColumnWithLabel[]>>({});
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [schema, setSchema] = useState<z.ZodObject<any>>(z.object({}));
  const [isInitialized, setIsInitialized] = useState(false);
  
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

        // メタデータからのデフォルト値とユーザー指定のデフォルト値をマージ
        // 注意: form.resetは初回のみ実行（setValueで設定した値を上書きしないため）
        if (!isInitialized) {
          const metadataDefaults = createDefaultValues(columnsData);
          const defaultValues = { ...metadataDefaults, ...userDefaultValues };
          form.reset(defaultValues);
          setIsInitialized(true);
        }
        
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

        // メタデータからのデフォルト値とユーザー指定のデフォルト値をマージ
        // 注意: form.resetは初回のみ実行（setValueで設定した値を上書きしないため）
        if (!isInitialized) {
          const metadataDefaults = createDefaultValues(allColumnsFlat);
          const defaultValues = { ...metadataDefaults, ...userDefaultValues };
          form.reset(defaultValues);
          setIsInitialized(true);
        }
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
  const handleSubmit = form.handleSubmit(
    async (data) => {
      try {
        await onSubmit(data);
      } catch (error) {
        console.error('Form submission error:', error);
        throw error;
      }
    },
    (errors) => {
      console.error('Form validation errors:', JSON.stringify(errors, null, 2));
      const errorFields = Object.keys(errors);
      errorFields.forEach(key => {
        console.error(`  - ${key}:`, errors[key]?.message || errors[key]);
      });
      if (onValidationError) {
        onValidationError(`入力エラーがあります（${errorFields.length}件）: ${errorFields.join(', ')}`);
      }
    }
  );
  
  return {
    form,
    submitForm: handleSubmit,
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