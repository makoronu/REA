/**
 * フィールド表示設定管理画面
 * 管理者専用：物件種別ごとにどのフィールドを表示するかを設定
 *
 * レイアウト: 物件種別が行、フィールドが列（横スクロール不要）
 */
import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';

// 型定義
interface PropertyType {
  id: string;
  label: string;
  group_name: string;
}

interface FieldVisibility {
  table_name: string;
  column_name: string;
  japanese_label: string;
  visible_for: string[] | null;
  required_for_publication: string[] | null;
  group_name: string;
  group_order: number;
  display_order: number;
}

type SettingType = 'visibility' | 'required';

// テーブル表示名（将来的にはAPIから取得）
const TABLE_LABELS: Record<string, string> = {
  properties: '物件基本情報',
  building_info: '建物情報',
  land_info: '土地情報',
  amenities: '設備・周辺環境',
};

// 物件種別グループの表示順（将来的にはAPIから取得）
const TYPE_GROUP_ORDER = ['居住用', '事業用', '投資用', 'その他'];

const FieldVisibilityPage: React.FC = () => {
  const [propertyTypes, setPropertyTypes] = useState<PropertyType[]>([]);
  const [fields, setFields] = useState<FieldVisibility[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('properties');
  const [selectedFieldGroup, setSelectedFieldGroup] = useState<string | null>(null);
  const [settingType, setSettingType] = useState<SettingType>('visibility');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [pendingChanges, setPendingChanges] = useState<Map<string, string[] | null>>(new Map());

  // 物件種別をグループ化してソート
  const groupedPropertyTypes = propertyTypes.reduce((acc, pt) => {
    if (!acc[pt.group_name]) acc[pt.group_name] = [];
    acc[pt.group_name].push(pt);
    return acc;
  }, {} as Record<string, PropertyType[]>);

  const sortedTypeGroups = TYPE_GROUP_ORDER.filter(g => groupedPropertyTypes[g]);

  // データ取得
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const ptRes = await fetch(`${API_BASE_URL}${API_PATHS.ADMIN.PROPERTY_TYPES}`);
        if (ptRes.ok) {
          const ptData = await ptRes.json();
          setPropertyTypes(ptData);
        }

        const fvRes = await fetch(`${API_BASE_URL}${API_PATHS.ADMIN.FIELD_VISIBILITY}?table_name=${selectedTable}`);
        if (fvRes.ok) {
          const fvData = await fvRes.json();
          setFields(fvData);
          // 最初のグループを選択（group_orderでソート）
          if (fvData.length > 0) {
            // グループ名とその最小group_orderを取得
            const groupOrders = new Map<string, number>();
            fvData.forEach((f: FieldVisibility) => {
              const group = f.group_name || 'その他';
              const existing = groupOrders.get(group);
              if (existing === undefined || f.group_order < existing) {
                groupOrders.set(group, f.group_order);
              }
            });
            // group_orderでソート
            const sorted = Array.from(groupOrders.entries())
              .sort((a, b) => a[1] - b[1])
              .map(([name]) => name);
            setSelectedFieldGroup(sorted[0] || null);
          }
        }
      } catch (err) {
        console.error('データ取得エラー:', err);
        setMessage({ type: 'error', text: 'データの取得に失敗しました' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [selectedTable]);

  // フィールドをグループ化（group_order情報も保持）
  const groupedFields = fields.reduce((acc, f) => {
    const group = f.group_name || 'その他';
    if (!acc[group]) acc[group] = { fields: [], minOrder: f.group_order };
    acc[group].fields.push(f);
    if (f.group_order < acc[group].minOrder) {
      acc[group].minOrder = f.group_order;
    }
    return acc;
  }, {} as Record<string, { fields: FieldVisibility[], minOrder: number }>);

  // グループをgroup_orderでソート
  const sortedGroups = Object.entries(groupedFields)
    .sort((a, b) => a[1].minOrder - b[1].minOrder)
    .map(([name]) => name);

  // 表示するフィールド
  const displayFields = selectedFieldGroup ? (groupedFields[selectedFieldGroup]?.fields || []) : [];

  // フィールドの設定変更（settingTypeに応じて切替）
  const handleToggle = (field: FieldVisibility, typeId: string) => {
    const key = `${field.table_name}.${field.column_name}`;
    const fieldValue = settingType === 'required'
      ? field.required_for_publication
      : field.visible_for;
    const currentValue: string[] | null | undefined = pendingChanges.has(key)
      ? pendingChanges.get(key)
      : fieldValue;

    let newValue: string[] | null;
    if (currentValue === null || currentValue === undefined) {
      newValue = propertyTypes.map(pt => pt.id).filter(id => id !== typeId);
    } else if (currentValue.includes(typeId)) {
      newValue = currentValue.filter(id => id !== typeId);
      if (newValue.length === 0) newValue = null;
    } else {
      newValue = [...currentValue, typeId];
      if (newValue.length === propertyTypes.length) newValue = null;
    }

    setPendingChanges(prev => {
      const next = new Map(prev);
      next.set(key, newValue);
      return next;
    });
  };

  // 行（物件種別）の全選択/全解除
  const handleRowSelectAll = (typeId: string, select: boolean) => {
    setPendingChanges(prev => {
      const next = new Map(prev);
      displayFields.forEach(field => {
        const key = `${field.table_name}.${field.column_name}`;
        const fieldValue = settingType === 'required'
          ? field.required_for_publication
          : field.visible_for;
        const currentValue: string[] | null | undefined = next.has(key) ? next.get(key) : fieldValue;

        let newValue: string[] | null;
        if (select) {
          // 追加
          if (currentValue === null || currentValue === undefined) {
            newValue = null; // 既に全表示
          } else if (currentValue.includes(typeId)) {
            newValue = currentValue; // 既に含まれている
          } else {
            newValue = [...currentValue, typeId];
            if (newValue.length === propertyTypes.length) newValue = null;
          }
        } else {
          // 除外
          if (currentValue === null || currentValue === undefined) {
            newValue = propertyTypes.map(pt => pt.id).filter(id => id !== typeId);
          } else {
            newValue = currentValue.filter(id => id !== typeId);
          }
        }
        next.set(key, newValue);
      });
      return next;
    });
  };

  // 列（フィールド）の全選択/全解除
  const handleColSelectAll = (field: FieldVisibility, select: boolean) => {
    const key = `${field.table_name}.${field.column_name}`;
    setPendingChanges(prev => {
      const next = new Map(prev);
      next.set(key, select ? null : []);
      return next;
    });
  };

  // 保存
  const handleSave = async () => {
    if (pendingChanges.size === 0) {
      setMessage({ type: 'error', text: '変更がありません' });
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    // 空配列チェック（全物件種別OFFを防止）
    for (const [key, value] of pendingChanges.entries()) {
      if (Array.isArray(value) && value.length === 0) {
        const [, columnName] = key.split('.');
        const field = fields.find(f => f.column_name === columnName);
        const fieldLabel = field?.japanese_label || columnName;
        setMessage({ type: 'error', text: `「${fieldLabel}」は最低1つの物件種別を選択してください` });
        setTimeout(() => setMessage(null), 5000);
        return;
      }
    }

    setIsSaving(true);
    try {
      const updates = Array.from(pendingChanges.entries()).map(([key, value]) => {
        const [table_name, column_name] = key.split('.');
        // settingTypeに応じて適切なフィールドに値を設定
        if (settingType === 'required') {
          return { table_name, column_name, required_for_publication: value };
        }
        return { table_name, column_name, visible_for: value };
      });

      const res = await fetch(
        `${API_BASE_URL}${API_PATHS.ADMIN.FIELD_VISIBILITY_BULK}?field_type=${settingType}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updates),
        }
      );

      if (res.ok) {
        const label = settingType === 'required' ? '必須設定' : '表示設定';
        setMessage({ type: 'success', text: `${updates.length}件の${label}を保存しました` });
        setPendingChanges(new Map());
        const fvRes = await fetch(`${API_BASE_URL}${API_PATHS.ADMIN.FIELD_VISIBILITY}?table_name=${selectedTable}`);
        if (fvRes.ok) {
          const fvData = await fvRes.json();
          setFields(fvData);
        }
      } else {
        setMessage({ type: 'error', text: '保存に失敗しました' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: '保存に失敗しました' });
    } finally {
      setIsSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  // 現在の値を取得（pending優先、settingTypeに応じて切替）
  const getCurrentValue = (field: FieldVisibility): string[] | null => {
    const key = `${field.table_name}.${field.column_name}`;
    if (pendingChanges.has(key)) {
      return pendingChanges.get(key)!;
    }
    return settingType === 'required'
      ? field.required_for_publication
      : field.visible_for;
  };

  // チェック状態判定
  const isChecked = (field: FieldVisibility, typeId: string): boolean => {
    const value = getCurrentValue(field);
    if (value === null) return true;
    return value.includes(typeId);
  };

  // 変更があるか
  const hasFieldChange = (field: FieldVisibility): boolean => {
    const key = `${field.table_name}.${field.column_name}`;
    return pendingChanges.has(key);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      {/* ヘッダー */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
          フィールド設定
        </h1>
        <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '8px' }}>
          {settingType === 'required'
            ? '公開時に必須となるフィールドを物件種別ごとに設定します'
            : '物件種別ごとに表示するフィールドを設定します'}
        </p>
      </div>

      {/* 設定タイプ切替タブ */}
      <div style={{
        display: 'flex',
        gap: '0',
        marginBottom: '16px',
        borderBottom: '2px solid #E5E7EB',
      }}>
        <button
          onClick={() => {
            if (settingType !== 'visibility') {
              setPendingChanges(new Map());
              setSettingType('visibility');
            }
          }}
          style={{
            padding: '12px 24px',
            border: 'none',
            backgroundColor: 'transparent',
            color: settingType === 'visibility' ? '#3B82F6' : '#6B7280',
            fontWeight: settingType === 'visibility' ? 600 : 400,
            fontSize: '14px',
            cursor: 'pointer',
            borderBottom: settingType === 'visibility' ? '2px solid #3B82F6' : '2px solid transparent',
            marginBottom: '-2px',
          }}
        >
          表示設定
        </button>
        <button
          onClick={() => {
            if (settingType !== 'required') {
              setPendingChanges(new Map());
              setSettingType('required');
            }
          }}
          style={{
            padding: '12px 24px',
            border: 'none',
            backgroundColor: 'transparent',
            color: settingType === 'required' ? '#3B82F6' : '#6B7280',
            fontWeight: settingType === 'required' ? 600 : 400,
            fontSize: '14px',
            cursor: 'pointer',
            borderBottom: settingType === 'required' ? '2px solid #3B82F6' : '2px solid transparent',
            marginBottom: '-2px',
          }}
        >
          公開時必須設定
        </button>
      </div>

      {/* メッセージ */}
      {message && (
        <div style={{
          padding: '12px 16px',
          marginBottom: '16px',
          borderRadius: '8px',
          backgroundColor: message.type === 'success' ? '#D1FAE5' : '#FEE2E2',
          color: message.type === 'success' ? '#065F46' : '#991B1B',
          fontSize: '14px',
        }}>
          {message.text}
        </div>
      )}

      {/* テーブル選択 & 保存ボタン */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        padding: '16px',
        backgroundColor: '#F9FAFB',
        borderRadius: '12px',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {Object.entries(TABLE_LABELS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSelectedTable(key)}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: selectedTable === key ? '#3B82F6' : '#fff',
                color: selectedTable === key ? '#fff' : '#374151',
                fontWeight: 500,
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              {label}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {pendingChanges.size > 0 && (
            <span style={{ fontSize: '13px', color: '#F59E0B' }}>
              {pendingChanges.size}件の変更
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving || pendingChanges.size === 0}
            style={{
              padding: '8px 20px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: pendingChanges.size === 0 ? '#E5E7EB' : '#3B82F6',
              color: pendingChanges.size === 0 ? '#9CA3AF' : '#fff',
              fontWeight: 600,
              cursor: pendingChanges.size === 0 ? 'not-allowed' : 'pointer',
              fontSize: '13px',
            }}
          >
            {isSaving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      {/* フィールドグループ選択 */}
      <div style={{
        display: 'flex',
        gap: '6px',
        marginBottom: '16px',
        flexWrap: 'wrap',
      }}>
        {sortedGroups.map(group => (
          <button
            key={group}
            onClick={() => setSelectedFieldGroup(group)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: selectedFieldGroup === group ? '2px solid #3B82F6' : '1px solid #E5E7EB',
              backgroundColor: selectedFieldGroup === group ? '#EFF6FF' : '#fff',
              color: selectedFieldGroup === group ? '#1D4ED8' : '#6B7280',
              fontWeight: selectedFieldGroup === group ? 600 : 400,
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            {group} ({groupedFields[group]?.fields.length || 0})
          </button>
        ))}
      </div>

      {/* ローディング */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '48px', color: '#6B7280' }}>
          読み込み中...
        </div>
      ) : (
        <div style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          maxHeight: 'calc(100vh - 300px)',
          overflowY: 'auto',
          position: 'relative',
        }}>
          {/* テーブル */}
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            {/* ヘッダー：フィールド名 */}
            <thead>
              <tr style={{ backgroundColor: '#F3F4F6' }}>
                <th style={{
                  padding: '12px 16px',
                  textAlign: 'left',
                  fontWeight: 600,
                  fontSize: '13px',
                  color: '#374151',
                  borderBottom: '1px solid #E5E7EB',
                  position: 'sticky',
                  top: 0,
                  backgroundColor: '#F3F4F6',
                  zIndex: 10,
                  minWidth: '120px',
                }}>
                  物件種別
                </th>
                {displayFields.map(field => (
                  <th
                    key={field.column_name}
                    style={{
                      padding: '8px 4px',
                      textAlign: 'center',
                      fontWeight: 500,
                      fontSize: '11px',
                      color: hasFieldChange(field) ? '#F59E0B' : '#374151',
                      borderBottom: '1px solid #E5E7EB',
                      position: 'sticky',
                      top: 0,
                      backgroundColor: hasFieldChange(field) ? '#FEF3C7' : '#F3F4F6',
                      zIndex: 10,
                      minWidth: '60px',
                      maxWidth: '80px',
                    }}
                  >
                    <div style={{ marginBottom: '4px' }}>
                      {field.japanese_label || field.column_name}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '2px' }}>
                      <button
                        onClick={() => handleColSelectAll(field, true)}
                        style={{
                          padding: '1px 4px',
                          fontSize: '9px',
                          border: '1px solid #D1D5DB',
                          borderRadius: '3px',
                          backgroundColor: '#fff',
                          cursor: 'pointer',
                          color: '#6B7280',
                        }}
                        title="全種別ON"
                      >
                        全
                      </button>
                      <button
                        onClick={() => handleColSelectAll(field, false)}
                        style={{
                          padding: '1px 4px',
                          fontSize: '9px',
                          border: '1px solid #D1D5DB',
                          borderRadius: '3px',
                          backgroundColor: '#fff',
                          cursor: 'pointer',
                          color: '#6B7280',
                        }}
                        title="全種別OFF"
                      >
                        無
                      </button>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            {/* ボディ：物件種別ごとの行 */}
            <tbody>
              {sortedTypeGroups.map(groupName => (
                <React.Fragment key={groupName}>
                  {/* グループヘッダー */}
                  <tr>
                    <td
                      colSpan={displayFields.length + 1}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#F9FAFB',
                        fontWeight: 600,
                        fontSize: '12px',
                        color: '#6B7280',
                        borderBottom: '1px solid #E5E7EB',
                      }}
                    >
                      {groupName}
                    </td>
                  </tr>

                  {/* 物件種別の行 */}
                  {groupedPropertyTypes[groupName]?.map(pt => (
                    <tr key={pt.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                      <td style={{
                        padding: '10px 16px',
                        fontSize: '13px',
                        color: '#1F2937',
                        backgroundColor: '#fff',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <span>{pt.label}</span>
                          <div style={{ display: 'flex', gap: '2px' }}>
                            <button
                              onClick={() => handleRowSelectAll(pt.id, true)}
                              style={{
                                padding: '2px 6px',
                                fontSize: '9px',
                                border: '1px solid #D1D5DB',
                                borderRadius: '3px',
                                backgroundColor: '#fff',
                                cursor: 'pointer',
                                color: '#6B7280',
                              }}
                              title="この行を全てON"
                            >
                              全
                            </button>
                            <button
                              onClick={() => handleRowSelectAll(pt.id, false)}
                              style={{
                                padding: '2px 6px',
                                fontSize: '9px',
                                border: '1px solid #D1D5DB',
                                borderRadius: '3px',
                                backgroundColor: '#fff',
                                cursor: 'pointer',
                                color: '#6B7280',
                              }}
                              title="この行を全てOFF"
                            >
                              無
                            </button>
                          </div>
                        </div>
                      </td>
                      {displayFields.map(field => (
                        <td
                          key={field.column_name}
                          style={{
                            padding: '8px 4px',
                            textAlign: 'center',
                            backgroundColor: hasFieldChange(field) ? 'rgba(251, 191, 36, 0.05)' : '#fff',
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked(field, pt.id)}
                            onChange={() => handleToggle(field, pt.id)}
                            style={{
                              width: '18px',
                              height: '18px',
                              cursor: 'pointer',
                              accentColor: '#3B82F6',
                            }}
                          />
                        </td>
                      ))}
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>

          {displayFields.length === 0 && (
            <div style={{ padding: '48px', textAlign: 'center', color: '#9CA3AF' }}>
              フィールドグループを選択してください
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FieldVisibilityPage;
