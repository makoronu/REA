import React, { useState } from 'react';
import { FormProvider } from 'react-hook-form';
import { FieldGroup } from './FieldFactory';
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
  layoutMode?: 'compact' | 'spacious' | 'auto';
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  tableName,
  tableNames,
  onSubmit,
  defaultValues,
  submitButtonText = '保存',
  isLoading: externalLoading = false,
  showDebug = false,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    form,
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

  // エラー表示 - 枠線なし
  if (error) {
    return (
      <div style={{
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        color: '#DC2626',
        padding: '16px 20px',
        borderRadius: '8px',
      }}>
        <strong style={{ fontWeight: 600 }}>エラー:</strong>
        <span> メタデータの取得に失敗しました。</span>
        <pre style={{ marginTop: '8px', fontSize: '13px', opacity: 0.8 }}>{error.message}</pre>
      </div>
    );
  }

  // ローディング - スケルトン（スピナー禁止）
  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '24px' }}>
        <div className="skeleton" style={{ width: '200px', height: '32px' }} />
        <div style={{ display: 'flex', gap: '12px' }}>
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton" style={{ width: '120px', height: '44px', borderRadius: '8px' }} />
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginTop: '16px' }}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="skeleton" style={{ height: '56px', borderRadius: '6px' }} />
          ))}
        </div>
      </div>
    );
  }

  // デバッグ情報
  const renderDebugInfo = () => {
    if (!showDebug) return null;

    return (
      <div style={{ marginTop: '32px', padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
        <h4 style={{ fontWeight: 600, marginBottom: '8px' }}>デバッグ情報</h4>
        <details>
          <summary style={{ cursor: 'pointer', fontSize: '14px', color: '#3B82F6' }}>フォームデータ</summary>
          <pre style={{ marginTop: '8px', fontSize: '12px', overflow: 'auto' }}>
            {JSON.stringify(form.watch(), null, 2)}
          </pre>
        </details>
      </div>
    );
  };

  // 単一テーブルモード
  if (tableName && !tableNames) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit as any} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {Object.entries(groupedColumns).map(([groupName, groupColumns]) => (
              <FieldGroup
                key={groupName}
                groupName={groupName}
                columns={groupColumns}
                disabled={isSubmitting}
              />
            ))}

            {/* ボタン - 枠線なし */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px',
              paddingTop: '24px',
            }}>
              <button
                type="button"
                onClick={() => form.reset()}
                disabled={isSubmitting}
                style={{
                  padding: '12px 24px',
                  fontSize: '14px',
                  fontWeight: 500,
                  color: '#6B7280',
                  backgroundColor: '#F3F4F6',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'background-color 150ms',
                }}
              >
                リセット
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                style={{
                  padding: '12px 32px',
                  fontSize: '14px',
                  fontWeight: 600,
                  color: '#fff',
                  backgroundColor: '#3B82F6',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 150ms',
                }}
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

      const tableLabels: Record<string, { label: string; icon: string }> = {
        'properties': { label: '基本・取引情報', icon: '🏠' },
        'land_info': { label: '土地情報', icon: '🗺️' },
        'building_info': { label: '建物情報', icon: '🏗️' },
        'amenities': { label: '設備・周辺環境', icon: '🔧' },
        'property_images': { label: '画像情報', icon: '📸' },
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
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit as any} style={{ width: '100%' }}>

            {/* 進行状況 - シンプルなバー、枠線なし */}
            <div style={{
              marginBottom: '24px',
              padding: '16px',
              backgroundColor: 'rgba(59, 130, 246, 0.06)',
              borderRadius: '12px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 500, color: '#1D4ED8' }}>
                  {activeTab + 1} / {tabGroups.length}
                </span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  {tabGroups.map((_, index) => (
                    <div
                      key={index}
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: index <= activeTab ? '#3B82F6' : 'rgba(59, 130, 246, 0.2)',
                        transition: 'background-color 200ms',
                      }}
                    />
                  ))}
                </div>
              </div>
              <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', borderRadius: '4px', height: '4px' }}>
                <div
                  style={{
                    backgroundColor: '#3B82F6',
                    height: '4px',
                    borderRadius: '4px',
                    transition: 'width 300ms ease-out',
                    width: `${((activeTab + 1) / tabGroups.length) * 100}%`
                  }}
                />
              </div>
            </div>

            {/* タブヘッダー - 枠線なし、背景色のみ */}
            <div style={{ marginBottom: '24px', overflowX: 'auto' }}>
              <div style={{ display: 'flex', gap: '8px', minWidth: 'max-content', paddingBottom: '8px' }}>
                {tabGroups.map((tabGroup, index) => (
                  <button
                    key={tabGroup.tableName}
                    type="button"
                    onClick={() => setActiveTab(index)}
                    style={{
                      backgroundColor: activeTab === index ? '#3B82F6' : 'transparent',
                      color: activeTab === index ? '#ffffff' : '#6B7280',
                      border: 'none',
                      padding: '12px 20px',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 150ms',
                      whiteSpace: 'nowrap',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                    onMouseEnter={(e) => {
                      if (activeTab !== index) {
                        e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.04)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (activeTab !== index) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    <span>{tabGroup.tableIcon}</span>
                    {tabGroup.tableLabel}
                  </button>
                ))}
              </div>
            </div>

            {/* タブコンテンツ - 枠線なし */}
            <div style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              padding: '24px',
              minHeight: '400px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
            }}>
              {tabGroups.map((tabGroup, index) => (
                <div
                  key={tabGroup.tableName}
                  style={{ display: activeTab === index ? 'block' : 'none' }}
                >
                  {/* タブタイトル - 下線なし */}
                  <div style={{ marginBottom: '24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '32px' }}>{tabGroup.tableIcon}</span>
                      <div>
                        <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
                          {tabGroup.tableLabel}
                        </h2>
                        <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '4px 0 0' }}>
                          {Object.keys(tabGroup.groups).length}つのセクション
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* フィールドグループ */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {Object.entries(tabGroup.groups).map(([groupName, groupColumns]) => (
                      <div key={`${tabGroup.tableName}-${groupName}`}>
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

            {/* ナビゲーションボタン - 枠線なし */}
            <div style={{
              marginTop: '24px',
              padding: '16px',
              backgroundColor: '#F9FAFB',
              borderRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px',
            }}>
              <button
                type="button"
                onClick={() => setActiveTab(Math.max(0, activeTab - 1))}
                disabled={activeTab === 0}
                style={{
                  backgroundColor: activeTab === 0 ? '#E5E7EB' : '#fff',
                  color: activeTab === 0 ? '#9CA3AF' : '#374151',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: activeTab === 0 ? 'not-allowed' : 'pointer',
                  fontWeight: 500,
                  boxShadow: activeTab === 0 ? 'none' : '0 1px 2px rgba(0,0,0,0.05)',
                }}
              >
                ← 前へ
              </button>

              <div style={{ display: 'flex', gap: '12px' }}>
                <button
                  type="button"
                  onClick={() => form.reset()}
                  disabled={isSubmitting}
                  style={{
                    backgroundColor: '#fff',
                    color: '#6B7280',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 500,
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  }}
                >
                  リセット
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  style={{
                    backgroundColor: '#3B82F6',
                    color: '#fff',
                    border: 'none',
                    padding: '10px 28px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 600,
                    boxShadow: '0 1px 2px rgba(59, 130, 246, 0.3)',
                  }}
                >
                  {isSubmitting ? '保存中...' : '保存'}
                </button>
              </div>

              <button
                type="button"
                onClick={() => setActiveTab(Math.min(tabGroups.length - 1, activeTab + 1))}
                disabled={activeTab === tabGroups.length - 1}
                style={{
                  backgroundColor: activeTab === tabGroups.length - 1 ? '#E5E7EB' : '#fff',
                  color: activeTab === tabGroups.length - 1 ? '#9CA3AF' : '#374151',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: activeTab === tabGroups.length - 1 ? 'not-allowed' : 'pointer',
                  fontWeight: 500,
                  boxShadow: activeTab === tabGroups.length - 1 ? 'none' : '0 1px 2px rgba(0,0,0,0.05)',
                }}
              >
                次へ →
              </button>
            </div>

            {renderDebugInfo()}
          </form>
        </FormProvider>
      </div>
    );
  }

  // テーブルが指定されていない場合
  return (
    <div style={{ textAlign: 'center', color: '#9CA3AF', padding: '32px' }}>
      テーブルが指定されていません。
    </div>
  );
};

// プリセット版
export const PropertyForm: React.FC<Omit<DynamicFormProps, 'tableName'>> = (props) => {
  return <DynamicForm {...props} tableName="properties" />;
};

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
