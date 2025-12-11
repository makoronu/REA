/**
 * フィールド表示設定管理画面
 * 管理者専用：物件種別ごとにどのフィールドを表示するかを設定
 */
import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

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
  group_name: string;
}

// テーブル表示名
const TABLE_LABELS: Record<string, string> = {
  properties: '物件基本情報',
  building_info: '建物情報',
  land_info: '土地情報',
  amenities: '設備・周辺環境',
};

// グループ表示順
const GROUP_ORDER = [
  '基本情報', '価格情報', '契約条件', '元請会社', '管理情報',
  '所在地', '学区', '電車・鉄道', 'バス', '周辺施設',
  '建物基本', '面積', '居住情報', '管理情報', '駐車場',
  '土地詳細', '接道',
  '設備', '交通', 'リフォーム', 'エコ性能',
  'システム',
];

const FieldVisibilityPage: React.FC = () => {
  const [propertyTypes, setPropertyTypes] = useState<PropertyType[]>([]);
  const [fields, setFields] = useState<FieldVisibility[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('properties');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [pendingChanges, setPendingChanges] = useState<Map<string, string[] | null>>(new Map());

  // 物件種別をグループ化
  const groupedPropertyTypes = propertyTypes.reduce((acc, pt) => {
    if (!acc[pt.group_name]) acc[pt.group_name] = [];
    acc[pt.group_name].push(pt);
    return acc;
  }, {} as Record<string, PropertyType[]>);

  // データ取得
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        // 物件種別取得
        const ptRes = await fetch(`${API_URL}/api/v1/admin/property-types`);
        if (ptRes.ok) {
          const ptData = await ptRes.json();
          setPropertyTypes(ptData);
        }

        // フィールド表示設定取得
        const fvRes = await fetch(`${API_URL}/api/v1/admin/field-visibility?table_name=${selectedTable}`);
        if (fvRes.ok) {
          const fvData = await fvRes.json();
          setFields(fvData);
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

  // フィールドをグループ化
  const groupedFields = fields.reduce((acc, f) => {
    const group = f.group_name || 'その他';
    if (!acc[group]) acc[group] = [];
    acc[group].push(f);
    return acc;
  }, {} as Record<string, FieldVisibility[]>);

  // グループをソート
  const sortedGroups = Object.keys(groupedFields).sort((a, b) => {
    const aIdx = GROUP_ORDER.indexOf(a);
    const bIdx = GROUP_ORDER.indexOf(b);
    if (aIdx === -1 && bIdx === -1) return a.localeCompare(b);
    if (aIdx === -1) return 1;
    if (bIdx === -1) return -1;
    return aIdx - bIdx;
  });

  // フィールドのvisible_for変更
  const handleToggle = (field: FieldVisibility, typeId: string) => {
    const key = `${field.table_name}.${field.column_name}`;
    const currentValue = pendingChanges.has(key)
      ? pendingChanges.get(key)
      : field.visible_for;

    let newValue: string[] | null;
    if (currentValue === null) {
      // 全表示 → 指定種別を除外（全種別から引く）
      newValue = propertyTypes.map(pt => pt.id).filter(id => id !== typeId);
    } else if (currentValue.includes(typeId)) {
      // 含まれている → 除外
      newValue = currentValue.filter(id => id !== typeId);
      if (newValue.length === 0) newValue = null; // 空なら全表示
    } else {
      // 含まれていない → 追加
      newValue = [...currentValue, typeId];
      // 全種別含まれたら null（全表示）に
      if (newValue.length === propertyTypes.length) newValue = null;
    }

    setPendingChanges(prev => {
      const next = new Map(prev);
      next.set(key, newValue);
      return next;
    });
  };

  // 全選択/全解除
  const handleSelectAll = (field: FieldVisibility, select: boolean) => {
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

    setIsSaving(true);
    try {
      const updates = Array.from(pendingChanges.entries()).map(([key, visible_for]) => {
        const [table_name, column_name] = key.split('.');
        return { table_name, column_name, visible_for };
      });

      const res = await fetch(`${API_URL}/api/v1/admin/field-visibility/bulk`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });

      if (res.ok) {
        setMessage({ type: 'success', text: `${updates.length}件の設定を保存しました` });
        setPendingChanges(new Map());
        // フィールド再取得
        const fvRes = await fetch(`${API_URL}/api/v1/admin/field-visibility?table_name=${selectedTable}`);
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

  // 現在の値を取得（pending優先）
  const getCurrentValue = (field: FieldVisibility): string[] | null => {
    const key = `${field.table_name}.${field.column_name}`;
    return pendingChanges.has(key) ? pendingChanges.get(key)! : field.visible_for;
  };

  // チェック状態判定
  const isChecked = (field: FieldVisibility, typeId: string): boolean => {
    const value = getCurrentValue(field);
    if (value === null) return true; // null = 全表示
    return value.includes(typeId);
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      {/* ヘッダー */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1A1A1A', margin: 0 }}>
          フィールド表示設定
        </h1>
        <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '8px' }}>
          物件種別ごとに表示するフィールドを設定します。チェックが入っている種別でのみフィールドが表示されます。
        </p>
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
        marginBottom: '24px',
        padding: '16px',
        backgroundColor: '#F9FAFB',
        borderRadius: '12px',
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {Object.entries(TABLE_LABELS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSelectedTable(key)}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: selectedTable === key ? '#3B82F6' : '#fff',
                color: selectedTable === key ? '#fff' : '#374151',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {label}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {pendingChanges.size > 0 && (
            <span style={{ fontSize: '13px', color: '#F59E0B' }}>
              {pendingChanges.size}件の未保存の変更
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving || pendingChanges.size === 0}
            style={{
              padding: '10px 24px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: pendingChanges.size === 0 ? '#E5E7EB' : '#3B82F6',
              color: pendingChanges.size === 0 ? '#9CA3AF' : '#fff',
              fontWeight: 600,
              cursor: pendingChanges.size === 0 ? 'not-allowed' : 'pointer',
            }}
          >
            {isSaving ? '保存中...' : '変更を保存'}
          </button>
        </div>
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
          overflow: 'hidden',
        }}>
          {/* テーブルヘッダー */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '200px 1fr',
            backgroundColor: '#F3F4F6',
            borderBottom: '1px solid #E5E7EB',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}>
            <div style={{ padding: '12px 16px', fontWeight: 600, color: '#374151' }}>
              フィールド
            </div>
            <div style={{ display: 'flex', overflowX: 'auto' }}>
              {Object.entries(groupedPropertyTypes).map(([groupName, types]) => (
                <div key={groupName} style={{ display: 'flex', flexDirection: 'column' }}>
                  <div style={{
                    padding: '8px 12px',
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#6B7280',
                    backgroundColor: '#E5E7EB',
                    textAlign: 'center',
                    borderRight: '1px solid #D1D5DB',
                  }}>
                    {groupName}
                  </div>
                  <div style={{ display: 'flex' }}>
                    {types.map(pt => (
                      <div
                        key={pt.id}
                        style={{
                          padding: '8px 8px',
                          fontSize: '11px',
                          color: '#374151',
                          textAlign: 'center',
                          minWidth: '70px',
                          borderRight: '1px solid #E5E7EB',
                          whiteSpace: 'nowrap',
                        }}
                        title={pt.label}
                      >
                        {pt.label.length > 6 ? pt.label.slice(0, 6) + '...' : pt.label}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* フィールド行 */}
          {sortedGroups.map(groupName => (
            <div key={groupName}>
              {/* グループヘッダー */}
              <div style={{
                padding: '10px 16px',
                backgroundColor: '#F9FAFB',
                borderBottom: '1px solid #E5E7EB',
                fontWeight: 600,
                fontSize: '13px',
                color: '#374151',
              }}>
                {groupName}
              </div>

              {/* フィールド */}
              {groupedFields[groupName].map(field => {
                const key = `${field.table_name}.${field.column_name}`;
                const hasChange = pendingChanges.has(key);

                return (
                  <div
                    key={key}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '200px 1fr',
                      borderBottom: '1px solid #F3F4F6',
                      backgroundColor: hasChange ? 'rgba(251, 191, 36, 0.1)' : 'transparent',
                    }}
                  >
                    {/* フィールド名 */}
                    <div style={{
                      padding: '10px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}>
                      <span style={{ fontSize: '13px', color: '#1F2937' }}>
                        {field.japanese_label || field.column_name}
                      </span>
                      <div style={{ display: 'flex', gap: '4px' }}>
                        <button
                          onClick={() => handleSelectAll(field, true)}
                          style={{
                            padding: '2px 6px',
                            fontSize: '10px',
                            border: '1px solid #D1D5DB',
                            borderRadius: '4px',
                            backgroundColor: '#fff',
                            cursor: 'pointer',
                            color: '#6B7280',
                          }}
                          title="全選択"
                        >
                          全
                        </button>
                        <button
                          onClick={() => handleSelectAll(field, false)}
                          style={{
                            padding: '2px 6px',
                            fontSize: '10px',
                            border: '1px solid #D1D5DB',
                            borderRadius: '4px',
                            backgroundColor: '#fff',
                            cursor: 'pointer',
                            color: '#6B7280',
                          }}
                          title="全解除"
                        >
                          無
                        </button>
                      </div>
                    </div>

                    {/* チェックボックス */}
                    <div style={{ display: 'flex' }}>
                      {Object.entries(groupedPropertyTypes).map(([groupName, types]) => (
                        <div key={groupName} style={{ display: 'flex' }}>
                          {types.map(pt => (
                            <div
                              key={pt.id}
                              style={{
                                minWidth: '70px',
                                padding: '8px',
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                borderRight: '1px solid #F3F4F6',
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
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FieldVisibilityPage;
