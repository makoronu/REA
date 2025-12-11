import React, { useState } from 'react';
import { FormProvider, useFormContext } from 'react-hook-form';
import { FieldGroup } from './FieldFactory';
import { useMetadataForm } from '../../hooks/useMetadataForm';
import { useAutoSave } from '../../hooks/useAutoSave';
import { ColumnWithLabel } from '../../services/metadataService';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

// 学校候補の型
interface SchoolCandidate {
  school_name: string;
  address: string | null;
  admin_type: string | null;
  distance_meters: number;
  walk_minutes: number;
  is_in_district: boolean;
}

// 学区自動取得・選択コンポーネント
const SchoolDistrictAutoFetchButton: React.FC = () => {
  const { getValues, setValue } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [elementaryCandidates, setElementaryCandidates] = useState<SchoolCandidate[]>([]);
  const [juniorHighCandidates, setJuniorHighCandidates] = useState<SchoolCandidate[]>([]);
  const [showCandidates, setShowCandidates] = useState(false);

  const handleFetch = async () => {
    const lat = getValues('latitude');
    const lng = getValues('longitude');

    if (!lat || !lng) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geo/school-districts?lat=${lat}&lng=${lng}`
      );

      if (!response.ok) {
        throw new Error('学校情報の取得に失敗しました');
      }

      const data = await response.json();
      setElementaryCandidates(data.elementary || []);
      setJuniorHighCandidates(data.junior_high || []);
      setShowCandidates(true);

      setMessage({ type: 'success', text: '学校候補を取得しました。選択してください。' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || '学校情報の取得に失敗しました' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const selectSchool = (type: 'elementary' | 'junior_high', school: SchoolCandidate) => {
    if (type === 'elementary') {
      setValue('elementary_school', school.school_name, { shouldDirty: true });
      setValue('elementary_school_minutes', school.walk_minutes, { shouldDirty: true });
    } else {
      setValue('junior_high_school', school.school_name, { shouldDirty: true });
      setValue('junior_high_school_minutes', school.walk_minutes, { shouldDirty: true });
    }
  };

  const renderCandidateList = (
    title: string,
    candidates: SchoolCandidate[],
    type: 'elementary' | 'junior_high'
  ) => {
    const currentValue = getValues(type === 'elementary' ? 'elementary_school' : 'junior_high_school');

    return (
      <div style={{ marginBottom: '16px' }}>
        <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: '#374151' }}>
          {title}
        </h4>
        {candidates.length === 0 ? (
          <p style={{ fontSize: '13px', color: '#6B7280' }}>候補が見つかりませんでした</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {candidates.map((school, index) => {
              const isSelected = currentValue === school.school_name;
              return (
                <button
                  key={index}
                  type="button"
                  onClick={() => selectSchool(type, school)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 12px',
                    backgroundColor: isSelected ? '#EFF6FF' : school.is_in_district ? '#FEF2F2' : '#F9FAFB',
                    border: isSelected ? '2px solid #3B82F6' : school.is_in_district ? '2px solid #EF4444' : '1px solid #E5E7EB',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: school.is_in_district ? 600 : 500,
                      color: school.is_in_district ? '#DC2626' : '#1F2937',
                    }}>
                      {school.is_in_district && '● '}
                      {school.school_name}
                      {school.is_in_district && (
                        <span style={{
                          marginLeft: '8px',
                          fontSize: '11px',
                          backgroundColor: '#DC2626',
                          color: '#fff',
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}>
                          学区内
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                      {school.address || '住所不明'}
                    </div>
                  </div>
                  <div style={{
                    fontSize: '13px',
                    color: '#374151',
                    whiteSpace: 'nowrap',
                    marginLeft: '12px',
                  }}>
                    徒歩{school.walk_minutes}分（{school.distance_meters.toLocaleString()}m）
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      <button
        type="button"
        onClick={handleFetch}
        disabled={isLoading}
        style={{
          backgroundColor: isLoading ? '#9CA3AF' : '#059669',
          color: '#fff',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '8px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          fontWeight: 500,
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        {isLoading ? (
          <>
            <span style={{
              display: 'inline-block',
              width: '16px',
              height: '16px',
              border: '2px solid #fff',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }} />
            取得中...
          </>
        ) : (
          <>🏫 座標から学校候補を取得</>
        )}
      </button>

      {message && (
        <div style={{
          marginTop: '12px',
          padding: '10px 14px',
          borderRadius: '8px',
          fontSize: '13px',
          backgroundColor: message.type === 'success' ? '#D1FAE5' : '#FEE2E2',
          color: message.type === 'success' ? '#065F46' : '#991B1B',
        }}>
          {message.text}
        </div>
      )}

      {showCandidates && (
        <div style={{
          marginTop: '16px',
          padding: '16px',
          backgroundColor: '#fff',
          border: '1px solid #E5E7EB',
          borderRadius: '12px',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
          }}>
            <p style={{ fontSize: '13px', color: '#6B7280' }}>
              <span style={{ color: '#DC2626', fontWeight: 600 }}>● 赤字</span> = 学区データあり
            </p>
            <button
              type="button"
              onClick={() => setShowCandidates(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '20px',
                cursor: 'pointer',
                color: '#9CA3AF',
              }}
            >
              ×
            </button>
          </div>

          {renderCandidateList('【小学校】', elementaryCandidates, 'elementary')}
          {renderCandidateList('【中学校】', juniorHighCandidates, 'junior_high')}
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

interface DynamicFormProps {
  tableName?: string;
  tableNames?: string[];
  onSubmit: (data: any) => void | Promise<void>;
  defaultValues?: any;
  isLoading?: boolean;
  showDebug?: boolean;
  autoSave?: boolean; // 自動保存有効/無効
  autoSaveDelay?: number; // デバウンス時間（ms）
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  tableName,
  tableNames,
  onSubmit,
  defaultValues,
  isLoading: externalLoading = false,
  showDebug = false,
  autoSave = false,
  autoSaveDelay = 2000,
}) => {
  const [activeTab, setActiveTab] = useState(0);

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
    onSubmit,
    defaultValues
  });

  // フォームデータを監視
  const formData = form.watch();

  // 自動保存フック
  useAutoSave(formData, {
    onSave: async (data) => {
      await Promise.resolve(onSubmit(data));
    },
    delay: autoSaveDelay,
    enabled: autoSave && !metadataLoading && !externalLoading,
  });

  const isLoading = metadataLoading || externalLoading;

  // エラー表示
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

  // ローディング - スケルトン
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
            {JSON.stringify(formData, null, 2)}
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {Object.entries(groupedColumns).map(([groupName, groupColumns]) => (
              <FieldGroup
                key={groupName}
                groupName={groupName}
                columns={groupColumns}
                disabled={false}
              />
            ))}
            {renderDebugInfo()}
          </div>
        </FormProvider>
      </div>
    );
  }

  // 複数テーブルモード（タブ形式）
  if (tableNames && tableNames.length > 0 && tables) {
    const orderedTables = tableNames.map(tableName =>
      tables.find(table => table.table_name === tableName)
    ).filter(table => table !== undefined);

    // 所在地・周辺情報グループ名
    const locationGroups = ['所在地', '学区', '交通', '周辺施設'];

    // propertiesから所在地・周辺情報を分離してタブを構築
    const tabGroups: Array<{
      tableName: string;
      tableLabel: string;
      tableIcon: string;
      groups: Record<string, ColumnWithLabel[]>;
    }> = [];

    // 1. 所在地・周辺情報タブを最初に追加
    const propertiesColumns = allColumns?.['properties'] || [];
    const locationColumns = propertiesColumns.filter(col =>
      locationGroups.includes(col.group_name || '')
    );
    if (locationColumns.length > 0) {
      const locationGrouped = locationColumns.reduce((acc, column) => {
        const groupName = column.group_name || '所在地';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>);

      tabGroups.push({
        tableName: 'properties_location',
        tableLabel: '所在地・周辺情報',
        tableIcon: '📍',
        groups: locationGrouped
      });
    }

    // 2. 残りのタブを追加（propertiesは所在地・周辺情報を除外）
    orderedTables.forEach(table => {
      const tableColumns = allColumns?.[table.table_name] || [];

      // propertiesの場合は所在地・周辺情報グループを除外
      const filteredColumns = table.table_name === 'properties'
        ? tableColumns.filter(col => !locationGroups.includes(col.group_name || ''))
        : tableColumns;

      const grouped = filteredColumns.reduce((acc, column) => {
        const groupName = column.group_name || '基本情報';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>);

      // 空のグループがある場合はスキップしない（フィールドがある場合のみ追加）
      if (Object.keys(grouped).length > 0) {
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

        tabGroups.push({
          tableName: table.table_name,
          tableLabel: tableInfo.label,
          tableIcon: tableInfo.icon,
          groups: grouped
        });
      }
    });

    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
          <div style={{ width: '100%' }}>

            {/* 進行状況バー */}
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

            {/* タブヘッダー */}
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

            {/* タブコンテンツ */}
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
                  {/* タブタイトル */}
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
                        {/* 学区グループの場合、自動取得ボタンを表示 */}
                        {groupName === '学区' && <SchoolDistrictAutoFetchButton />}
                        <FieldGroup
                          groupName={groupName}
                          columns={groupColumns}
                          disabled={false}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* ナビゲーションボタン（保存ボタンなし） */}
            <div style={{
              marginTop: '24px',
              padding: '16px',
              backgroundColor: '#F9FAFB',
              borderRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
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

              {/* 中央: 自動保存のヒント */}
              <span style={{ fontSize: '12px', color: '#9CA3AF' }}>
                変更は自動的に保存されます
              </span>

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
          </div>
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

  return <DynamicForm {...props} tableNames={propertyTables} />;
};
