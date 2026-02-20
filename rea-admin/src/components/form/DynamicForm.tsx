import React, { useState, useEffect } from 'react';
import { FormProvider } from 'react-hook-form';
import { FieldGroup } from './FieldFactory';
import { useMetadataForm } from '../../hooks/useMetadataForm';
import { useAutoSave } from '../../hooks/useAutoSave';
import { ColumnWithLabel, metadataService } from '../../services/metadataService';
import { API_PATHS } from '../../constants/apiPaths';
import { api } from '../../services/api';
import { AUTO_SAVE_DELAY_MS, TAB_GROUPS, GEO_GROUPS, PUBLICATION_STATUS, SALES_STATUS } from '../../constants';
import { RegulationTab } from './RegulationTab';
import { RegistryTab } from '../registry/RegistryTab';
import ErrorBanner from '../ErrorBanner';
import { GeoPanel } from './GeoPanel';

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

// 物件種別によるフィールド表示判定
const isFieldVisibleForPropertyType = (
  visibleFor: string[] | null | undefined,
  propertyType: string | null | undefined,
  columnName: string
): boolean => {
  // 物件種別と新築フィールドは常に表示
  if (columnName === 'property_type' || columnName === 'is_new_construction') return true;
  // 種別未選択なら他のフィールドは非表示
  if (!propertyType) return false;
  // visible_forがnull/undefinedなら全種別表示（未設定状態）
  if (visibleFor === null || visibleFor === undefined) return true;
  // 空配列なら非表示（ユーザーが全チェックを外した）
  if (visibleFor.length === 0) return false;
  // 種別が含まれているか
  return visibleFor.includes(propertyType);
};

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
  // 公開バリデーションエラー状態（全モードで必要なため、早期リターン前に定義）
  const [publicationValidationError, setPublicationValidationError] = useState<{
    message: string;
    groups: Record<string, string[]>;
  } | null>(null);
  // エラーモーダル表示状態
  const [showValidationErrorModal, setShowValidationErrorModal] = useState(false);
  // Geo情報管理パネル
  const [isGeoPanelOpen, setIsGeoPanelOpen] = useState(false);

  // ステータス色設定（メタデータ駆動）
  const [salesStatusConfig, setSalesStatusConfig] = useState<Record<string, { label: string; color: string; bg: string }>>({});
  const [publicationStatusConfig, setPublicationStatusConfig] = useState<Record<string, { label: string; color: string; bg: string }>>({});

  // フィルターオプション（ステータス色含む）をAPIから取得
  useEffect(() => {
    const fetchStatusConfigs = async () => {
      try {
        const options = await metadataService.getFilterOptions();

        // sales_status の色設定を構築
        if (options.sales_status) {
          const config: Record<string, { label: string; color: string; bg: string }> = {};
          for (const opt of options.sales_status) {
            config[opt.value] = {
              label: opt.label,
              color: opt.color || '#6B7280',
              bg: opt.bg || '#F3F4F6',
            };
          }
          setSalesStatusConfig(config);
        }

        // publication_status の色設定を構築
        if (options.publication_status) {
          const config: Record<string, { label: string; color: string; bg: string }> = {};
          for (const opt of options.publication_status) {
            config[opt.value] = {
              label: opt.label,
              color: opt.color || '#6B7280',
              bg: opt.bg || '#F3F4F6',
            };
          }
          setPublicationStatusConfig(config);
        }
      } catch (error) {
        console.error('Failed to fetch status configs:', error);
      }
    };

    fetchStatusConfigs();
  }, []);

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

  // フォームデータを監視
  const formData = form.watch();

  // 公開前確認バリデーション用の個別watch（useEffect依存配列の安定化）
  const watchedPubStatus = form.watch('publication_status');
  const watchedPropId = form.watch('id');

  // 初期バリデーション実行フラグ（Hooksルール: 条件付きリターンの前に宣言必須）
  const initialValidationRan = React.useRef(false);

  // 公開前確認ステータス時の初期バリデーション実行
  useEffect(() => {
    // 初回のみ実行（無限ループ防止）
    if (initialValidationRan.current) return;
    if (watchedPubStatus !== PUBLICATION_STATUS.PRE_CHECK || !watchedPropId) return;

    initialValidationRan.current = true;

    const runInitialValidation = async () => {
      try {
        const response = await api.get(
          `${API_PATHS.PROPERTIES.validatePublication(watchedPropId)}?target_status=${encodeURIComponent(PUBLICATION_STATUS.PUBLIC)}`
        );
        const result = response.data;
        if (!result.is_valid) {
          setPublicationValidationError({
            message: result.message,
            groups: result.groups,
          });
        }
      } catch (err) {
        console.error('Initial validation check failed:', err);
        setPublicationValidationError({
          message: 'バリデーションチェックに失敗しました',
          groups: {},
        });
      }
    };
    runInitialValidation();
  }, [watchedPropId, watchedPubStatus]);

  // 自動保存フック
  const autoSaveEnabled = autoSave && !metadataLoading && !externalLoading;

  const { saveStatus } = useAutoSave(formData, {
    onSave: async (data) => {
      await Promise.resolve(onSubmit(data));
    },
    delay: autoSaveDelay,
    enabled: autoSaveEnabled,
  });

  // ステータス表示テキスト
  const getSaveStatusDisplay = () => {
    if (!autoSave) return null;
    switch (saveStatus) {
      case 'unsaved':
        return { text: '下書き', color: '#F59E0B', bg: '#FEF3C7' };
      case 'saving':
        return { text: '保存中...', color: '#3B82F6', bg: '#DBEAFE' };
      case 'saved':
        return { text: '保存済み', color: '#10B981', bg: '#D1FAE5' };
      case 'error':
        return { text: '保存エラー', color: '#EF4444', bg: '#FEE2E2' };
      default:
        return { text: '保存済み', color: '#10B981', bg: '#D1FAE5' };
    }
  };

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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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

    // タブグループ定義（constants.tsで一元管理）
    const locationGroups = TAB_GROUPS.location;
    const basicInfoGroups = TAB_GROUPS.basicInfo;
    const priceDealGroups = TAB_GROUPS.priceDeal;
    const managementGroups = TAB_GROUPS.management;

    // 現在選択されている物件種別
    const currentPropertyType = formData.property_type;
    const propertiesColumns = allColumns?.['properties'] || [];

    // 物件種別未選択時の表示（タブ構築前に判定）
    if (!currentPropertyType) {
      // property_typeとis_new_constructionのみ抽出
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
              {/* アイコンとタイトル */}
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏠</div>
                <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1A1A1A', margin: '0 0 8px' }}>
                  物件種別を選択してください
                </h2>
                <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>
                  種別を選ぶと、その物件に必要な入力項目が表示されます
                </p>
              </div>

              {/* 物件種別選択フィールド */}
              <div style={{ maxWidth: '400px', margin: '0 auto' }}>
                <FieldGroup
                  groupName=""
                  columns={propertyTypeFields}
                  disabled={false}
                />
              </div>
            </div>
          </FormProvider>
        </div>
      );
    }

    // propertiesから所在地タブを分離してタブを構築
    const tabGroups: Array<{
      tableName: string;
      tableLabel: string;
      tableIcon: string;
      groups: Record<string, ColumnWithLabel[]>;
    }> = [];

    // 所在地タブ用のデータを先に準備
    const locationColumns = propertiesColumns.filter(col =>
      locationGroups.includes(col.group_name || '') &&
      isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name)
    );
    const locationTabData = locationColumns.length > 0 ? {
      tableName: 'properties_location',
      tableLabel: '所在地',
      tableIcon: '📍',
      groups: locationColumns.reduce((acc, column) => {
        const groupName = column.group_name || '所在地';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>)
    } : null;

    // GeoPanel用: 学区カラムを取得
    const schoolDistrictColumns = propertiesColumns.filter(col =>
      col.group_name === '学区' &&
      isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name)
    );

    // タブを追加（propertiesは所在地・Geoグループを除外）
    orderedTables.forEach(table => {
      const tableColumns = allColumns?.[table.table_name] || [];

      // 物件種別フィルタリング（全テーブルに適用）
      const filteredColumns = tableColumns.filter(col => {
        // propertiesの場合は所在地グループ・Geoグループを除外
        if (table.table_name === 'properties' && (locationGroups.includes(col.group_name || '') || GEO_GROUPS.includes(col.group_name || ''))) {
          return false;
        }
        // 除外グループ（ステータス、システム）はヘッダーで表示
        if (TAB_GROUPS.excluded.includes(col.group_name || '')) {
          return false;
        }
        // land_infoの法規制・ハザードグループは法令制限タブで表示するので除外
        if (table.table_name === 'land_info' && TAB_GROUPS.regulationFromLandInfo.includes(col.group_name || '')) {
          return false;
        }
        // 物件種別によるフィルタリング
        return isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name);
      });

      const grouped = filteredColumns.reduce((acc, column) => {
        const groupName = column.group_name || '基本情報';
        if (!acc[groupName]) {
          acc[groupName] = [];
        }
        acc[groupName].push(column);
        return acc;
      }, {} as Record<string, ColumnWithLabel[]>);

      // propertiesテーブルの処理
      if (table.table_name === 'properties') {
        // 所在地タブを先に追加（ユーザー要望：所在地を最初に）
        if (locationTabData) {
          tabGroups.push(locationTabData);
        }

        // グループを3つのタブに分割

        // 1. 基本情報タブ
        const basicInfoColumns = filteredColumns.filter(col =>
          basicInfoGroups.includes(col.group_name || '')
        );
        if (basicInfoColumns.length > 0) {
          const basicInfoGrouped = basicInfoColumns.reduce((acc, column) => {
            const groupName = column.group_name || '基本情報';
            if (!acc[groupName]) acc[groupName] = [];
            acc[groupName].push(column);
            return acc;
          }, {} as Record<string, ColumnWithLabel[]>);

          tabGroups.push({
            tableName: 'properties_basic',
            tableLabel: '基本情報',
            tableIcon: '🏠',
            groups: basicInfoGrouped
          });
        }

        // 2. 価格・取引タブ
        const priceDealColumns = filteredColumns.filter(col =>
          priceDealGroups.includes(col.group_name || '')
        );
        if (priceDealColumns.length > 0) {
          const priceDealGrouped = priceDealColumns.reduce((acc, column) => {
            const groupName = column.group_name || '価格情報';
            if (!acc[groupName]) acc[groupName] = [];
            acc[groupName].push(column);
            return acc;
          }, {} as Record<string, ColumnWithLabel[]>);

          tabGroups.push({
            tableName: 'properties_price',
            tableLabel: '価格・取引',
            tableIcon: '💰',
            groups: priceDealGrouped
          });
        }

        // 3. 管理・費用タブ
        const managementColumns = filteredColumns.filter(col =>
          managementGroups.includes(col.group_name || '')
        );
        if (managementColumns.length > 0) {
          const managementGrouped = managementColumns.reduce((acc, column) => {
            const groupName = column.group_name || '管理情報';
            if (!acc[groupName]) acc[groupName] = [];
            acc[groupName].push(column);
            return acc;
          }, {} as Record<string, ColumnWithLabel[]>);

          tabGroups.push({
            tableName: 'properties_management',
            tableLabel: '管理・費用',
            tableIcon: '📋',
            groups: managementGrouped
          });
        }

        // 法令制限タブを追加
        tabGroups.push({
          tableName: 'regulations',
          tableLabel: '法令制限',
          tableIcon: '⚖️',
          groups: {} // 特殊タブ：RegulationTabコンポーネントを使用
        });
        return;
      }

      // 他のテーブルの処理（フィールドがある場合のみタブ追加）
      if (Object.keys(grouped).length > 0) {
        const tableLabels: Record<string, { label: string; icon: string }> = {
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

    // 登記情報タブを追加（画像情報の後）
    tabGroups.push({
      tableName: 'registries',
      tableLabel: '登記情報',
      tableIcon: '📜',
      groups: {} // 特殊タブ：RegistryTabコンポーネントを使用
    });

    // ステータス表示用（色設定はAPIから取得済み: salesStatusConfig, publicationStatusConfig）

    const currentSalesStatus = formData.sales_status || SALES_STATUS.ASSESSMENT;
    const currentPublicationStatus = formData.publication_status || PUBLICATION_STATUS.PRIVATE;

    // 案件ステータスに応じて公開状態の選択肢を制限（販売中・商談中のみ公開可能）
    const isPublicationEditable = [SALES_STATUS.SELLING, SALES_STATUS.NEGOTIATING].includes(currentSalesStatus);

    // ステータス変更ハンドラー（連動ロジックはAPI側で一元管理）
    const handleSalesStatusChange = (newStatus: string) => {
      form.setValue('sales_status', newStatus, { shouldDirty: true });
      // publication_statusの自動設定は削除
      // 連動ロジックはAPI側（properties.py）で一元管理
      // 保存後にAPIレスポンスでUIが更新される
    };

    // 公開ステータス変更ハンドラー（リアルタイムバリデーション付き）
    const handlePublicationStatusChange = async (newStatus: string) => {
      form.setValue('publication_status', newStatus, { shouldDirty: true });
      // エラー状態をクリア
      setPublicationValidationError(null);
      setShowValidationErrorModal(false);

      // 公開/会員公開への変更時のみバリデーションを実行
      if (([PUBLICATION_STATUS.PUBLIC, PUBLICATION_STATUS.MEMBER] as string[]).includes(newStatus) && formData.id) {
        try {
          const response = await api.get(
            `${API_PATHS.PROPERTIES.validatePublication(formData.id)}?target_status=${encodeURIComponent(newStatus)}`
          );
          const result = response.data;
          if (!result.is_valid) {
            setPublicationValidationError({
              message: result.message,
              groups: result.groups,
            });
            // バリデーションエラー時は「公開前確認」に戻す
            form.setValue('publication_status', PUBLICATION_STATUS.PRE_CHECK, { shouldDirty: true });
          }
        } catch (err) {
          console.error('Publication validation check failed:', err);
        }
      }
    };

    // グループ名からタブインデックスを特定してナビゲート
    const navigateToField = (groupName: string) => {
      // グループ名とタブのマッピング
      const groupToTabIndex: Record<string, number> = {};

      // tabGroups配列を走査してマッピングを構築
      tabGroups.forEach((tab, index) => {
        // 通常タブ: groupsの各グループ名をマッピング
        Object.keys(tab.groups).forEach((grp) => {
          groupToTabIndex[grp] = index;
        });
        // TAB_GROUPSからの直接マッピング
        if (tab.tableName === 'properties_location') {
          TAB_GROUPS.location.forEach((grp) => { groupToTabIndex[grp] = index; });
        } else if (tab.tableName === 'properties_basic') {
          TAB_GROUPS.basicInfo.forEach((grp) => { groupToTabIndex[grp] = index; });
        } else if (tab.tableName === 'properties_price') {
          TAB_GROUPS.priceDeal.forEach((grp) => { groupToTabIndex[grp] = index; });
        } else if (tab.tableName === 'properties_management') {
          TAB_GROUPS.management.forEach((grp) => { groupToTabIndex[grp] = index; });
        } else if (tab.tableName === 'land_info') {
          groupToTabIndex['土地情報'] = index;
          groupToTabIndex['土地'] = index;
        } else if (tab.tableName === 'building_info') {
          groupToTabIndex['建物情報'] = index;
          groupToTabIndex['建物'] = index;
        } else if (tab.tableName === 'regulations') {
          groupToTabIndex['法規制（自動取得）'] = index;
          groupToTabIndex['ハザード情報（自動取得）'] = index;
        }
      });

      const tabIndex = groupToTabIndex[groupName];
      if (tabIndex !== undefined) {
        setActiveTab(tabIndex);
        setShowValidationErrorModal(false);
        // 少し待ってからスクロール（タブ切り替え後のレンダリングを待つ）
        setTimeout(() => {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 100);
      } else {
        // マッピングが見つからない場合はモーダルを閉じるのみ
        setShowValidationErrorModal(false);
      }
    };

    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
          {/* バリデーションエラー */}
          {validationError && (
            <ErrorBanner type="error" message={validationError} onClose={() => setValidationError(null)} />
          )}
          <div style={{ width: '100%' }}>

            {/* 固定ヘッダー：タブ + ステータス */}
            <div style={{
              position: 'sticky',
              top: '57px', // Layoutのヘッダー高さ
              zIndex: 50,
              backgroundColor: 'var(--color-bg, #FAFAFA)',
              paddingTop: '16px',
              paddingBottom: '8px',
              marginLeft: '-16px',
              marginRight: '-16px',
              paddingLeft: '16px',
              paddingRight: '16px',
            }}>
              {/* 最終更新日時（編集時のみ・日本時間） */}
              {formData.updated_at && (
                <div style={{
                  fontSize: '11px',
                  color: '#9CA3AF',
                  marginBottom: '8px',
                  textAlign: 'right',
                }}>
                  最終更新: {new Date(formData.updated_at).toLocaleString('ja-JP', {
                    timeZone: 'Asia/Tokyo',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              )}

              {/* ステータスバー - 二段レイアウト */}
              <div style={{
                marginBottom: '12px',
                padding: '8px 12px',
                backgroundColor: '#fff',
                borderRadius: '8px',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
              }}>
                {/* 上段：案件ステータス */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 500, width: '32px' }}>案件</span>
                  <div style={{ display: 'flex', gap: '3px', flexWrap: 'wrap' }}>
                    {Object.entries(salesStatusConfig).map(([status, config]) => (
                      <button
                        key={status}
                        type="button"
                        onClick={() => handleSalesStatusChange(status)}
                        style={{
                          padding: '3px 8px',
                          borderRadius: '4px',
                          border: currentSalesStatus === status ? `1.5px solid ${config.color}` : '1px solid #E5E7EB',
                          backgroundColor: currentSalesStatus === status ? config.bg : 'transparent',
                          color: currentSalesStatus === status ? config.color : '#9CA3AF',
                          fontSize: '11px',
                          fontWeight: currentSalesStatus === status ? 600 : 400,
                          cursor: 'pointer',
                          transition: 'all 100ms',
                        }}
                      >
                        {config.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 下段：公開ステータス + 保存ボタン */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 500, width: '32px' }}>公開</span>
                    <div style={{ display: 'flex', gap: '3px' }}>
                      {Object.entries(publicationStatusConfig).map(([status, config]) => {
                        const isDisabled = !isPublicationEditable && status !== PUBLICATION_STATUS.PRIVATE;
                        return (
                          <button
                            key={status}
                            type="button"
                            onClick={() => !isDisabled && handlePublicationStatusChange(status)}
                            disabled={isDisabled}
                            style={{
                              padding: '3px 8px',
                              borderRadius: '4px',
                              border: currentPublicationStatus === status ? `1.5px solid ${config.color}` : '1px solid #E5E7EB',
                              backgroundColor: currentPublicationStatus === status ? config.bg : 'transparent',
                              color: currentPublicationStatus === status ? config.color : (isDisabled ? '#D1D5DB' : '#9CA3AF'),
                              fontSize: '11px',
                              fontWeight: currentPublicationStatus === status ? 600 : 400,
                              cursor: isDisabled ? 'not-allowed' : 'pointer',
                              transition: 'all 100ms',
                              opacity: isDisabled ? 0.5 : 1,
                            }}
                          >
                            {config.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* 保存ボタン */}
                  {!autoSave && (
                    <button
                      type="button"
                      disabled={!!publicationValidationError}
                      onClick={async () => {
                        try {
                          await submitForm();
                          // 成功時はエラー状態をクリア
                          setPublicationValidationError(null);
                          setShowValidationErrorModal(false);
                        } catch (err: any) {
                          // 公開バリデーションエラーの場合
                          if (err?.type === 'publication_validation') {
                            setPublicationValidationError({
                              message: err.message,
                              groups: err.groups,
                            });
                            setShowValidationErrorModal(true);
                          }
                          // その他のエラーは親コンポーネントで処理済み
                        }
                      }}
                      style={{
                        backgroundColor: publicationValidationError ? '#9CA3AF' : '#10B981',
                        color: '#fff',
                        border: 'none',
                        padding: '5px 16px',
                        borderRadius: '4px',
                        cursor: publicationValidationError ? 'not-allowed' : 'pointer',
                        fontWeight: 600,
                        fontSize: '11px',
                        transition: 'all 100ms',
                        opacity: publicationValidationError ? 0.7 : 1,
                      }}
                      onMouseOver={(e) => {
                        if (!publicationValidationError) {
                          e.currentTarget.style.backgroundColor = '#059669';
                        }
                      }}
                      onMouseOut={(e) => {
                        if (!publicationValidationError) {
                          e.currentTarget.style.backgroundColor = '#10B981';
                        }
                      }}
                    >
                      保存
                    </button>
                  )}
                </div>
              </div>

              {/* 公開バリデーションエラー表示 */}
              {publicationValidationError && (
                <div style={{
                  marginBottom: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  color: '#991B1B',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>⚠️</span>
                      <span>{publicationValidationError.message}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowValidationErrorModal(true)}
                      style={{
                        backgroundColor: '#DC2626',
                        color: '#fff',
                        border: 'none',
                        padding: '4px 12px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 500,
                        cursor: 'pointer',
                      }}
                    >
                      詳細を見る
                    </button>
                  </div>
                </div>
              )}

              {/* タブヘッダー */}
              <div style={{ overflowX: 'auto' }}>
                <div style={{ display: 'flex', gap: '6px', minWidth: 'max-content', paddingBottom: '4px' }}>
                  {tabGroups.map((tabGroup, index) => (
                    <button
                      key={tabGroup.tableName}
                      type="button"
                      onClick={() => {
                        setActiveTab(index);
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                      }}
                      style={{
                        backgroundColor: activeTab === index ? '#3B82F6' : '#fff',
                        color: activeTab === index ? '#ffffff' : '#6B7280',
                        border: activeTab === index ? 'none' : '1px solid #E5E7EB',
                        padding: '10px 16px',
                        borderRadius: '8px',
                        fontSize: '13px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all 150ms',
                        whiteSpace: 'nowrap',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        boxShadow: activeTab === index ? '0 2px 4px rgba(59, 130, 246, 0.3)' : 'none',
                      }}
                      onMouseEnter={(e) => {
                        if (activeTab !== index) {
                          e.currentTarget.style.backgroundColor = '#F3F4F6';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (activeTab !== index) {
                          e.currentTarget.style.backgroundColor = '#fff';
                        }
                      }}
                    >
                      <span>{tabGroup.tableIcon}</span>
                      {tabGroup.tableLabel}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* タブコンテンツ */}
            <div style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              padding: '16px',
              marginTop: '16px',
              minHeight: '400px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
            }}>
              {tabGroups.map((tabGroup, index) => (
                <div
                  key={tabGroup.tableName}
                  style={{ display: activeTab === index ? 'block' : 'none' }}
                >
                  {/* 特殊タブ：法令制限 */}
                  {tabGroup.tableName === 'regulations' ? (
                    <>
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontSize: '32px' }}>{tabGroup.tableIcon}</span>
                          <div>
                            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
                              {tabGroup.tableLabel}
                            </h2>
                            <p style={{ fontSize: '13px', color: '#9CA3AF', margin: '4px 0 0' }}>
                              用途地域・ハザード情報を自動取得
                            </p>
                          </div>
                        </div>
                      </div>
                      <RegulationTab />
                    </>
                  ) : tabGroup.tableName === 'registries' ? (
                    /* 特殊タブ：登記情報 */
                    <>
                      <div style={{ marginBottom: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ fontSize: '32px' }}>{tabGroup.tableIcon}</span>
                          <div>
                            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
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
                    /* 通常タブ */
                    <>
                      {/* タブタイトル */}
                      <div style={{ marginBottom: '12px' }}>
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

                      {/* 所在地タブの場合、周辺情報管理ボタンを表示 */}
                      {tabGroup.tableName === 'properties_location' && (
                        <div style={{ marginBottom: '16px' }}>
                          <button
                            type="button"
                            onClick={() => setIsGeoPanelOpen(true)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '12px 20px',
                              backgroundColor: '#EFF6FF',
                              border: '1px solid #BFDBFE',
                              borderRadius: '8px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              fontWeight: 500,
                              color: '#1D4ED8',
                              width: '100%',
                              justifyContent: 'center',
                            }}
                          >
                            <span style={{ fontSize: '18px' }}>🗺️</span>
                            周辺情報を管理（学区・駅・バス・施設）
                          </button>
                        </div>
                      )}

                      {/* フィールドグループ */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {Object.entries(tabGroup.groups).map(([groupName, groupColumns]) => {
                          // 元請会社グループは仲介（3:専任媒介, 4:一般媒介, 5:専属専任）の場合のみ表示
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

            {/* ナビゲーションボタン（保存ボタンなし） */}
            <div style={{
              marginTop: '12px',
              padding: '16px',
              backgroundColor: '#F9FAFB',
              borderRadius: '12px',
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

              {/* 中央: 保存ステータス（自動保存時のみ） */}
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
            {showValidationErrorModal && publicationValidationError && (
              <div
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 1000,
                }}
                onClick={() => setShowValidationErrorModal(false)}
              >
                <div
                  style={{
                    backgroundColor: '#fff',
                    borderRadius: '12px',
                    padding: '24px',
                    maxWidth: '500px',
                    width: '90%',
                    maxHeight: '80vh',
                    overflow: 'auto',
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* モーダルヘッダー */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '20px',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '24px' }}>⚠️</span>
                      <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#DC2626', margin: 0 }}>
                        公開に必要な項目が未入力です
                      </h3>
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowValidationErrorModal(false)}
                      style={{
                        background: 'none',
                        border: 'none',
                        fontSize: '24px',
                        cursor: 'pointer',
                        color: '#9CA3AF',
                        padding: '4px',
                      }}
                    >
                      ×
                    </button>
                  </div>

                  {/* エラー内容（グループ別） */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {Object.entries(publicationValidationError.groups).map(([groupName, fields]) => (
                      <div key={groupName} style={{
                        backgroundColor: '#FEF2F2',
                        borderRadius: '8px',
                        padding: '12px 16px',
                        border: '1px solid #FECACA',
                      }}>
                        <button
                          type="button"
                          onClick={() => navigateToField(groupName)}
                          style={{
                            width: '100%',
                            textAlign: 'left',
                            background: 'none',
                            border: 'none',
                            padding: 0,
                            cursor: 'pointer',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: '#B91C1C',
                            marginBottom: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                        >
                          <span>📋</span>
                          {groupName}
                          <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#DC2626' }}>→移動</span>
                        </button>
                        <ul style={{
                          margin: 0,
                          paddingLeft: '20px',
                          color: '#991B1B',
                          fontSize: '13px',
                        }}>
                          {fields.map((field, idx) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>{field}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>

                  {/* 閉じるボタン */}
                  <div style={{ marginTop: '20px', textAlign: 'center' }}>
                    <button
                      type="button"
                      onClick={() => setShowValidationErrorModal(false)}
                      style={{
                        backgroundColor: '#6B7280',
                        color: '#fff',
                        border: 'none',
                        padding: '10px 32px',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: 500,
                        cursor: 'pointer',
                      }}
                    >
                      閉じる
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Geo情報管理パネル（FormProvider内に配置） */}
            <GeoPanel
              isOpen={isGeoPanelOpen}
              onClose={() => setIsGeoPanelOpen(false)}
              schoolDistrictColumns={schoolDistrictColumns}
            />
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
