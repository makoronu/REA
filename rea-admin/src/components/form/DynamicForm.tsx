import React, { useState } from 'react';
import { FormProvider } from 'react-hook-form';
import { FieldGroup, SmartFieldGroup } from './FieldFactory';
import { useMetadataForm } from '../../hooks/useMetadataForm';
import { ColumnWithLabel } from '../../services/metadataService';

interface DynamicFormProps {
  tableName?: string;
  tableNames?: string[];
  onSubmit: (data: any) => void | Promise<void>;
  defaultValues?: any;
  submitButtonText?: string;
  isLoading?: boolean;
  showDebug?: boolean;
  layoutMode?: 'compact' | 'spacious' | 'auto'; // レイアウトモード追加
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  tableName,
  tableNames,
  onSubmit,
  defaultValues,
  submitButtonText = '保存',
  isLoading: externalLoading = false,
  showDebug = false,
  layoutMode = 'auto'
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    form,
    columns,
    groupedColumns,
    tables,
    allColumns,
    isLoading: metadataLoading,
    error
  } = useMetadataForm({
    tableName,
    tableNames,
    onSubmit: async (data) => {
      setIsSubmitting(true);
      try {
        await onSubmit(data);
      } finally {
        setIsSubmitting(false);
      }
    },
    defaultValues
  });

  const isLoading = metadataLoading || externalLoading;

  // フィールドグループの優先度とレイアウト設定
  const getGroupSettings = (tableName: string, groupName: string) => {
    const settings: Record<string, Record<string, { priority: 'high' | 'medium' | 'low'; layout: 'single' | 'double' | 'auto' }>> = {
      'properties': {
        '基本情報': { priority: 'high', layout: 'double' },
        '基本・取引情報': { priority: 'high', layout: 'double' },
        '価格情報': { priority: 'high', layout: 'double' },
        '契約条件': { priority: 'medium', layout: 'double' },
        '元請会社': { priority: 'medium', layout: 'double' },
        '管理情報': { priority: 'low', layout: 'single' },
        'システム': { priority: 'low', layout: 'single' }
      },
      'land_info': {
        '基本情報': { priority: 'high', layout: 'double' },
        '権利関係': { priority: 'high', layout: 'double' },
        '詳細情報': { priority: 'medium', layout: 'auto' }
      },
      'building_info': {
        '基本情報': { priority: 'high', layout: 'double' },
        '構造・設備': { priority: 'high', layout: 'double' },
        '詳細情報': { priority: 'medium', layout: 'auto' }
      },
      'amenities': {
        '設備': { priority: 'medium', layout: 'auto' },
        '周辺環境': { priority: 'medium', layout: 'auto' }
      },
      'property_images': {
        '画像管理': { priority: 'medium', layout: 'single' }
      }
    };

    return settings[tableName]?.[groupName] || { priority: 'medium', layout: 'auto' };
  };

  // エラー表示
  if (error) {
    return (
      <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong className="font-bold">エラー:</strong>
        <span className="block sm:inline"> メタデータの取得に失敗しました。</span>
        <pre className="mt-2 text-sm">{error.message}</pre>
      </div>
    );
  }

  // ローディング表示
  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">フォームを生成中...</span>
      </div>
    );
  }

  // デバッグ情報
  const renderDebugInfo = () => {
    if (!showDebug) return null;

    return (
      <div className="mt-8 p-4 bg-gray-100 rounded">
        <h4 className="font-bold mb-2">デバッグ情報</h4>
        <details>
          <summary className="cursor-pointer text-sm text-blue-600">フォームデータ</summary>
          <pre className="mt-2 text-xs overflow-auto">
            {JSON.stringify(form.watch(), null, 2)}
          </pre>
        </details>
        <details className="mt-2">
          <summary className="cursor-pointer text-sm text-blue-600">エラー</summary>
          <pre className="mt-2 text-xs overflow-auto">
            {JSON.stringify(form.formState.errors, null, 2)}
          </pre>
        </details>
        <details className="mt-2">
          <summary className="cursor-pointer text-sm text-blue-600">カラム情報</summary>
          <pre className="mt-2 text-xs overflow-auto">
            {JSON.stringify(columns.map(c => ({
              name: c.column_name,
              type: c.input_type,
              required: c.is_required
            })), null, 2)}
          </pre>
        </details>
      </div>
    );
  };

  // 進行状況インジケーター（複数テーブル時）
  const renderProgressIndicator = (tabGroups: any[]) => {
    if (tabGroups.length <= 1) return null;

    return (
      <div className="mb-6 bg-gray-50 p-4 rounded-lg">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">
            進行状況: {activeTab + 1} / {tabGroups.length}
          </span>
          <div className="flex space-x-1">
            {tabGroups.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index <= activeTab ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>
        <div className="mt-2 bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((activeTab + 1) / tabGroups.length) * 100}%` }}
          />
        </div>
      </div>
    );
  };

  // 単一テーブルモード
  if (tableName && !tableNames) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit} className="space-y-6">
            {Object.entries(groupedColumns).map(([groupName, groupColumns]) => {
              const { priority, layout } = getGroupSettings(tableName, groupName);
              return (
                <FieldGroup
                  key={groupName}
                  groupName={groupName}
                  columns={groupColumns}
                  disabled={isSubmitting}
                  priority={priority}
                  layout={layout}
                />
              );
            })}

            <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3 pt-6 border-t">
              <button
                type="button"
                onClick={() => form.reset()}
                className="w-full sm:w-auto px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                disabled={isSubmitting}
              >
                リセット
              </button>
              <button
                type="submit"
                className="w-full sm:w-auto px-6 py-3 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                disabled={isSubmitting}
              >
                {isSubmitting ? '送信中...' : submitButtonText}
              </button>
            </div>

            {renderDebugInfo()}
          </form>
        </FormProvider>
      </div>
    );
  }

  // 複数テーブルモード（タブ形式）
  if (tableNames && tableNames.length > 0 && tables) {
    // tableNamesの順序に従ってtablesを並び替え
    const orderedTables = tableNames.map(tableName => 
      tables.find(table => table.table_name === tableName)
    ).filter(table => table !== undefined);

    const tabGroups = orderedTables.map(table => {
      const tableColumns = allColumns?.[table.table_name] || [];
      const grouped = tableColumns.reduce((acc, column) => {
        const groupName = column.group_name || '基本情報';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>);

      // 日本語のテーブル名マッピング - 新テーブル構造に対応
      const tableLabels: Record<string, { label: string; icon: string }> = {
        'properties': { label: '基本・取引情報', icon: '🏠' },
        'land_info': { label: '土地情報', icon: '🗺️' },
        'building_info': { label: '建物情報', icon: '🏗️' },
        'amenities': { label: '設備・周辺環境', icon: '🔧' },
        'property_images': { label: '画像情報', icon: '📸' },
        // 旧テーブル名も残しておく（互換性のため）
        'properties_location': { label: '所在地', icon: '📍' },
        'properties_pricing': { label: '価格', icon: '💰' },
        'properties_building': { label: '建物', icon: '🏗️' },
        'properties_contract': { label: '契約', icon: '📋' },
        'properties_facilities': { label: '周辺施設', icon: '🏪' },
        'properties_floor_plans': { label: '間取り', icon: '📐' },
        'properties_images': { label: '画像', icon: '📸' },
        'properties_roads': { label: '接道', icon: '🛣️' },
        'properties_transportation': { label: '交通', icon: '🚃' },
        'properties_other': { label: 'その他', icon: '📄' }
      };

      const tableInfo = tableLabels[table.table_name] || { 
        label: table.table_comment || table.table_name, 
        icon: '📄' 
      };

      return {
        tableName: table.table_name,
        tableLabel: tableInfo.label,
        tableIcon: tableInfo.icon,
        groups: grouped
      };
    });

    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit} className="w-full">
            {/* 進行状況インジケーター */}
            <div className="mb-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-blue-800">
                  進行状況: {activeTab + 1} / {tabGroups.length}
                </span>
                <div className="flex space-x-1">
                  {tabGroups.map((_, index) => (
                    <div
                      key={index}
                      className={`w-3 h-3 rounded-full ${
                        index <= activeTab ? 'bg-blue-600' : 'bg-blue-200'
                      }`}
                    />
                  ))}
                </div>
              </div>
              <div className="mt-2 bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((activeTab + 1) / tabGroups.length) * 100}%` }}
                />
              </div>
            </div>

            {/* シンプルなタブヘッダー */}
            <div className="mb-6 overflow-x-auto">
              <div className="flex gap-3 min-w-max pb-2">
                {tabGroups.map((tabGroup, index) => (
                  <button
                    key={tabGroup.tableName}
                    type="button"
                    onClick={() => setActiveTab(index)}
                    style={{
                      backgroundColor: activeTab === index ? '#2563eb' : '#ffffff',
                      color: activeTab === index ? '#ffffff' : '#374151',
                      border: '2px solid',
                      borderColor: activeTab === index ? '#2563eb' : '#d1d5db',
                      padding: '12px 20px',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      whiteSpace: 'nowrap',
                      minWidth: 'fit-content'
                    }}
                    onMouseEnter={(e) => {
                      if (activeTab !== index) {
                        e.currentTarget.style.backgroundColor = '#f3f4f6';
                        e.currentTarget.style.borderColor = '#9ca3af';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (activeTab !== index) {
                        e.currentTarget.style.backgroundColor = '#ffffff';
                        e.currentTarget.style.borderColor = '#d1d5db';
                      }
                    }}
                  >
                    <span style={{ marginRight: '8px' }}>{tabGroup.tableIcon}</span>
                    {tabGroup.tableLabel}
                  </button>
                ))}
              </div>
            </div>

            {/* タブコンテンツ */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6 min-h-96 w-full overflow-hidden">
              {tabGroups.map((tabGroup, index) => (
                <div
                  key={tabGroup.tableName}
                  style={{
                    display: activeTab === index ? 'block' : 'none'
                  }}
                >
                  {/* 現在のタブ情報 */}
                  <div className="mb-6 pb-4 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                      <span style={{ fontSize: '32px' }}>{tabGroup.tableIcon}</span>
                      <div>
                        <h2 className="text-xl sm:text-2xl font-bold text-gray-900">{tabGroup.tableLabel}</h2>
                        <p className="text-sm text-gray-500">
                          {Object.keys(tabGroup.groups).length}つのセクション
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* フィールドグループ */}
                  <div className="space-y-6 w-full">
                    {Object.entries(tabGroup.groups).map(([groupName, groupColumns]) => (
                      <div key={`${tabGroup.tableName}-${groupName}`} className="w-full">
                        <FieldGroup
                          groupName={groupName}
                          columns={groupColumns}
                          disabled={isSubmitting}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* ナビゲーションボタン */}
            <div className="mt-6 bg-gray-50 p-4 rounded-lg w-full">
              <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                <button
                  type="button"
                  onClick={() => setActiveTab(Math.max(0, activeTab - 1))}
                  disabled={activeTab === 0}
                  style={{
                    backgroundColor: activeTab === 0 ? '#f3f4f6' : '#ffffff',
                    color: activeTab === 0 ? '#9ca3af' : '#374151',
                    border: '1px solid #d1d5db',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    cursor: activeTab === 0 ? 'not-allowed' : 'pointer',
                    minWidth: '80px'
                  }}
                >
                  ← 前へ
                </button>

                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
                  <button
                    type="button"
                    onClick={() => form.reset()}
                    disabled={isSubmitting}
                    style={{
                      backgroundColor: '#ffffff',
                      color: '#374151',
                      border: '1px solid #d1d5db',
                      padding: '10px 20px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      minWidth: '100px'
                    }}
                  >
                    🔄 リセット
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    style={{
                      backgroundColor: '#2563eb',
                      color: '#ffffff',
                      border: 'none',
                      padding: '10px 24px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: '600',
                      minWidth: '100px'
                    }}
                  >
                    {isSubmitting ? '💾 保存中...' : '💾 保存'}
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => setActiveTab(Math.min(tabGroups.length - 1, activeTab + 1))}
                  disabled={activeTab === tabGroups.length - 1}
                  style={{
                    backgroundColor: activeTab === tabGroups.length - 1 ? '#f3f4f6' : '#ffffff',
                    color: activeTab === tabGroups.length - 1 ? '#9ca3af' : '#374151',
                    border: '1px solid #d1d5db',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    cursor: activeTab === tabGroups.length - 1 ? 'not-allowed' : 'pointer',
                    minWidth: '80px'
                  }}
                >
                  次へ →
                </button>
              </div>
            </div>

            {renderDebugInfo()}
          </form>
        </FormProvider>
      </div>
    );
  }

  // テーブルが指定されていない場合
  return (
    <div className="text-center text-gray-500 p-8">
      テーブルが指定されていません。
    </div>
  );
};

// 使いやすいプリセット版

// 単一のpropertiesテーブル用
export const PropertyForm: React.FC<Omit<DynamicFormProps, 'tableName'>> = (props) => {
  return <DynamicForm {...props} tableName="properties" />;
};

// 全property系テーブル統合フォーム - 新テーブル構造に対応
export const PropertyFullForm: React.FC<Omit<DynamicFormProps, 'tableNames'>> = (props) => {
  const propertyTables = [
    'properties',
    'land_info', 
    'building_info',
    'amenities',
    'property_images'
  ];

  return <DynamicForm {...props} tableNames={propertyTables} layoutMode="spacious" />;
};