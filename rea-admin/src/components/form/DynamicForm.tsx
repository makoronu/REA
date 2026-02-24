/**
 * DynamicForm: メタデータ駆動の動的フォーム
 *
 * 単一テーブル/複数テーブル（タブ形式）に対応。
 * ステータス管理はuseStatusSync、タブ構築はbuildTabGroups、
 * ヘッダーはFormHeader、バリデーションモーダルはValidationErrorModalに委譲。
 */
import React, { useState } from 'react';
import { FormProvider } from 'react-hook-form';
import { FieldGroup } from './FieldGroup';
import { useMetadataForm } from '../../hooks/useMetadataForm';
import { useAutoSave } from '../../hooks/useAutoSave';
import { AUTO_SAVE_DELAY_MS } from '../../constants';
import { RegulationPanel } from './RegulationPanel';
import { RegistryTab } from '../registry/RegistryTab';
import ErrorBanner from '../ErrorBanner';
import { GeoPanel } from './GeoPanel';
import { useStatusSync } from './useStatusSync';
import { buildTabGroups, getTabIndexForGroup } from './buildTabGroups';
import { ValidationErrorModal } from './ValidationErrorModal';
import { FormHeader } from './FormHeader';

interface DynamicFormProps {
  tableName?: string;
  tableNames?: string[];
  onSubmit: (data: any) => void | Promise<void>;
  defaultValues?: any;
  isLoading?: boolean;
  showDebug?: boolean;
  autoSave?: boolean;
  autoSaveDelay?: number;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  tableName,
  tableNames,
  onSubmit,
  defaultValues,
  isLoading: externalLoading = false,
  showDebug = false,
  autoSave = false,
  autoSaveDelay = AUTO_SAVE_DELAY_MS,
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isGeoPanelOpen, setIsGeoPanelOpen] = useState(false);
  const [isRegulationPanelOpen, setIsRegulationPanelOpen] = useState(false);

  const {
    form,
    submitForm,
    groupedColumns,
    tables,
    allColumns,
    isLoading: metadataLoading,
    error
  } = useMetadataForm({
    tableName,
    tableNames,
    onSubmit,
    defaultValues,
    onValidationError: (msg: string) => setValidationError(msg),
  });

  const formData = form.watch();

  // ステータス管理（色設定・変更ハンドラー・公開バリデーション）
  const statusSync = useStatusSync({ form, formData });

  // 自動保存
  const autoSaveEnabled = autoSave && !metadataLoading && !externalLoading;
  const { saveStatus } = useAutoSave(formData, {
    onSave: async (data) => { await Promise.resolve(onSubmit(data)); },
    delay: autoSaveDelay,
    enabled: autoSaveEnabled,
  });

  const getSaveStatusDisplay = () => {
    if (!autoSave) return null;
    switch (saveStatus) {
      case 'unsaved': return { text: '下書き', color: '#F59E0B', bg: '#FEF3C7' };
      case 'saving': return { text: '保存中...', color: '#3B82F6', bg: '#DBEAFE' };
      case 'saved': return { text: '保存済み', color: '#10B981', bg: '#D1FAE5' };
      case 'error': return { text: '保存エラー', color: '#EF4444', bg: '#FEE2E2' };
      default: return { text: '保存済み', color: '#10B981', bg: '#D1FAE5' };
    }
  };

  const isLoading = metadataLoading || externalLoading;

  if (error) {
    return (
      <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.08)', color: '#DC2626', padding: '16px 20px', borderRadius: '8px' }}>
        <strong style={{ fontWeight: 600 }}>エラー:</strong>
        <span> メタデータの取得に失敗しました。</span>
        <pre style={{ marginTop: '8px', fontSize: '13px', opacity: 0.8 }}>{error.message}</pre>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px' }}>
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {Object.entries(groupedColumns).map(([groupName, groupColumns]) => (
              <FieldGroup key={groupName} groupName={groupName} columns={groupColumns} disabled={false} />
            ))}
            {renderDebugInfo()}
          </div>
        </FormProvider>
      </div>
    );
  }

  // 複数テーブルモード（タブ形式）
  if (tableNames && tableNames.length > 0 && tables) {
    const orderedTables = tableNames
      .map(tn => tables.find(t => t.table_name === tn))
      .filter(t => t !== undefined);
    const currentPropertyType = formData.property_type;
    const propertiesColumns = allColumns?.['properties'] || [];

    // 物件種別未選択時
    if (!currentPropertyType) {
      const propertyTypeFields = propertiesColumns.filter(col =>
        col.column_name === 'property_type' || col.column_name === 'is_new_construction'
      );
      return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
          <FormProvider {...form}>
            <div style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              padding: '32px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
            }}>
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏠</div>
                <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#1A1A1A', margin: '0 0 8px' }}>
                  物件種別を選択してください
                </h2>
                <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
                  種別を選ぶと、その物件に必要な入力項目が表示されます
                </p>
              </div>
              <div style={{ maxWidth: '400px', margin: '0 auto' }}>
                <FieldGroup groupName="" columns={propertyTypeFields} disabled={false} />
              </div>
            </div>
          </FormProvider>
        </div>
      );
    }

    // タブグループ構築
    const tabGroups = buildTabGroups(orderedTables, allColumns, propertiesColumns, currentPropertyType);

    // グループ名からタブへナビゲート
    const navigateToField = (groupName: string) => {
      const tabIndex = getTabIndexForGroup(tabGroups, groupName);
      if (tabIndex !== null) {
        setActiveTab(tabIndex);
        statusSync.setShowValidationErrorModal(false);
        setTimeout(() => { window.scrollTo({ top: 0, behavior: 'smooth' }); }, 100);
      } else {
        statusSync.setShowValidationErrorModal(false);
      }
    };

    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
          {validationError && (
            <ErrorBanner type="error" message={validationError} onClose={() => setValidationError(null)} />
          )}
          <div style={{ width: '100%' }}>
            <FormHeader
              formData={formData}
              statusSync={statusSync}
              submitForm={submitForm}
              autoSave={autoSave}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              tabGroups={tabGroups}
            />

            {/* タブコンテンツ */}
            <div style={{
              backgroundColor: '#ffffff',
              borderRadius: '8px',
              padding: '12px',
              marginTop: '8px',
              minHeight: '400px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
            }}>
              {tabGroups.map((tabGroup, index) => (
                <div
                  key={tabGroup.tableName}
                  style={{ display: activeTab === index ? 'block' : 'none' }}
                >
                  {tabGroup.tableName === 'registries' ? (
                    <>
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontSize: '20px' }}>{tabGroup.tableIcon}</span>
                          <div>
                            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
                              {tabGroup.tableLabel}
                            </h2>
                            <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '4px 0 0' }}>
                              土地・建物の登記情報
                            </p>
                          </div>
                        </div>
                      </div>
                      {formData.id ? (
                        <RegistryTab propertyId={formData.id} />
                      ) : (
                        <div style={{
                          padding: '40px 20px',
                          backgroundColor: '#F9FAFB',
                          borderRadius: '8px',
                          border: '2px dashed #D1D5DB',
                          textAlign: 'center',
                        }}>
                          <div style={{ fontSize: '32px', marginBottom: '12px' }}>📜</div>
                          <div style={{ fontSize: '14px', color: '#6B7280' }}>
                            物件を保存すると登記情報を追加できます
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* タブタイトル */}
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontSize: '20px' }}>{tabGroup.tableIcon}</span>
                          <div>
                            <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
                              {tabGroup.tableLabel}
                            </h2>
                            <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '4px 0 0' }}>
                              {Object.keys(tabGroup.groups).length}つのセクション
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* 土地情報タブの場合、法令制限自動取得ボタンを表示 */}
                      {tabGroup.tableName === 'land_info' && (
                        <div style={{ marginBottom: '16px' }}>
                          <button
                            type="button"
                            onClick={() => setIsRegulationPanelOpen(true)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '12px 20px',
                              backgroundColor: '#FFFBEB',
                              border: '1px solid #FCD34D',
                              borderRadius: '8px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              fontWeight: 500,
                              color: '#92400E',
                              width: '100%',
                              justifyContent: 'center',
                            }}
                          >
                            <span style={{ fontSize: '18px' }}>⚖️</span>
                            法令制限を自動取得（用途地域・建ぺい率等）
                          </button>
                        </div>
                      )}

                      {/* フィールドグループ */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {Object.entries(tabGroup.groups).map(([groupName, groupColumns]) => {
                          if (groupName === '元請会社') {
                            const transactionType = formData.transaction_type;
                            const isBrokerage = ['3', '4', '5'].includes(String(transactionType));
                            if (!isBrokerage) return null;
                          }
                          return (
                            <div key={`${tabGroup.tableName}-${groupName}`}>
                              <FieldGroup
                                groupName={groupName}
                                columns={groupColumns}
                                disabled={false}
                                collapsible={tabGroup.tableName === 'amenities'}
                                defaultCollapsed={false}
                                onOpenGeoPanel={
                                  tabGroup.tableName === 'properties_location'
                                    ? () => setIsGeoPanelOpen(true)
                                    : undefined
                                }
                              />
                            </div>
                          );
                        })}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>

            {/* ナビゲーションボタン */}
            <div style={{
              marginTop: '8px',
              padding: '10px',
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <button
                type="button"
                onClick={() => {
                  setActiveTab(Math.max(0, activeTab - 1));
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
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

              {autoSave && (() => {
                const status = getSaveStatusDisplay();
                if (!status) return null;
                return (
                  <span style={{
                    fontSize: '12px',
                    color: status.color,
                    backgroundColor: status.bg,
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontWeight: 500,
                  }}>
                    {status.text}
                  </span>
                );
              })()}

              <button
                type="button"
                onClick={() => {
                  setActiveTab(Math.min(tabGroups.length - 1, activeTab + 1));
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
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

            {/* 公開バリデーションエラー詳細モーダル */}
            {statusSync.showValidationErrorModal && statusSync.publicationValidationError && (
              <ValidationErrorModal
                publicationValidationError={statusSync.publicationValidationError}
                onClose={() => statusSync.setShowValidationErrorModal(false)}
                onNavigateToField={navigateToField}
              />
            )}

            {/* Geo情報管理パネル */}
            <GeoPanel
              isOpen={isGeoPanelOpen}
              onClose={() => setIsGeoPanelOpen(false)}
            />

            {/* 法令制限パネル */}
            <RegulationPanel
              isOpen={isRegulationPanelOpen}
              onClose={() => setIsRegulationPanelOpen(false)}
            />
          </div>
        </FormProvider>
      </div>
    );
  }

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
