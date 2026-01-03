import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../../config';

// =================================================================
// 共通インターフェース
// =================================================================

interface JsonEditorProps<T> {
  value: T[];
  onChange: (value: T[]) => void;
  disabled?: boolean;
}

// RoadInfoEditor専用インターフェース（接道なしフラグ対応）
interface RoadInfoEditorProps {
  value: RoadInfo[] | { no_road_access?: boolean } | null;
  onChange: (value: RoadInfo[] | { no_road_access: boolean }) => void;
  disabled?: boolean;
}

// =================================================================
// 接道情報エディタ
// =================================================================

interface RoadInfo {
  direction: string;
  road_type: string;
  road_width: number;
  frontage: number;
  road_status: string;
}

const ROAD_DIRECTIONS = [
  { value: '1', label: '北' },
  { value: '2', label: '北東' },
  { value: '3', label: '東' },
  { value: '4', label: '南東' },
  { value: '5', label: '南' },
  { value: '6', label: '南西' },
  { value: '7', label: '西' },
  { value: '8', label: '北西' },
];

const ROAD_TYPES = [
  { value: '1', label: '公道' },
  { value: '2', label: '私道' },
];

const ROAD_STATUS = [
  { value: '1', label: '建築基準法上の道路' },
  { value: '2', label: '42条1項1号' },
  { value: '3', label: '42条1項2号' },
  { value: '4', label: '42条1項3号' },
  { value: '5', label: '42条2項道路' },
  { value: '9', label: 'その他' },
];

export const RoadInfoEditor: React.FC<RoadInfoEditorProps> = ({
  value,
  onChange,
  disabled
}) => {
  // 「接道なし」フラグのチェック
  const isNoRoadAccess = (v: any): boolean => {
    return v && typeof v === 'object' && !Array.isArray(v) && v.no_road_access === true;
  };

  const noRoadAccess = isNoRoadAccess(value);

  // valueが配列でない場合（オブジェクト形式のroad_info）を配列に変換
  const normalizeValue = (v: any): RoadInfo[] => {
    if (!v) return [];
    // 「接道なし」フラグの場合は空配列
    if (isNoRoadAccess(v)) return [];
    if (Array.isArray(v)) return v;
    // オブジェクト形式の場合（road1_type, road1_width, road1_direction, road1_frontage...）
    if (typeof v === 'object') {
      const roads: RoadInfo[] = [];
      // road1, road2 の形式で複数の道路情報がある可能性
      for (let i = 1; i <= 2; i++) {
        const prefix = `road${i}_`;
        const direction = v[`${prefix}direction`] || v['road_access'] || '';
        const roadType = v[`${prefix}type`] || '';
        const width = v[`${prefix}width`] || 0;
        const frontage = v[`${prefix}frontage`] || 0;

        // 値があれば追加
        if (direction || roadType || width || frontage) {
          roads.push({
            direction: String(direction).replace(/^\d+:/, ''), // "4:南東" -> "南東"
            road_type: String(roadType).replace(/^\d+:/, ''), // "1:公道" -> "公道"
            road_width: Number(width) || 0,
            frontage: Number(frontage) || 0,
            road_status: ''
          });
        }
      }
      return roads;
    }
    return [];
  };

  const normalizedValue = normalizeValue(value);

  // 「接道なし」チェックボックスの切り替え
  const handleNoRoadAccessChange = (checked: boolean) => {
    if (checked) {
      onChange({ no_road_access: true });
    } else {
      onChange([]);
    }
  };

  const addItem = () => {
    onChange([...normalizedValue, {
      direction: '',
      road_type: '',
      road_width: 0,
      frontage: 0,
      road_status: ''
    }]);
  };

  const removeItem = (index: number) => {
    onChange(normalizedValue.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof RoadInfo, fieldValue: string | number) => {
    const newValue = [...normalizedValue];
    newValue[index] = { ...newValue[index], [field]: fieldValue };
    onChange(newValue);
  };

  return (
    <div className="space-y-3">
      {/* 接道なしチェックボックス */}
      <label
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px 16px',
          backgroundColor: noRoadAccess ? '#FEF3C7' : '#F9FAFB',
          borderRadius: '8px',
          cursor: disabled ? 'not-allowed' : 'pointer',
          border: noRoadAccess ? '1px solid #F59E0B' : '1px solid #E5E7EB',
        }}
      >
        <input
          type="checkbox"
          checked={noRoadAccess}
          onChange={(e) => handleNoRoadAccessChange(e.target.checked)}
          disabled={disabled}
          style={{ width: '18px', height: '18px', accentColor: '#F59E0B' }}
        />
        <span style={{ fontSize: '14px', fontWeight: 500, color: noRoadAccess ? '#92400E' : '#374151' }}>
          接道なし（袋地）
        </span>
      </label>

      {/* 接道情報入力欄（接道なしの場合は非表示） */}
      {!noRoadAccess && (
        <>
          {normalizedValue.map((item, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg bg-white"
              style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr) auto', gap: '12px', alignItems: 'end' }}
            >
              <div>
                <label className="block text-xs text-gray-600 mb-1">接道方向</label>
                <select
                  value={item.direction}
                  onChange={(e) => updateItem(index, 'direction', e.target.value)}
                  disabled={disabled}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                >
                  <option value="">選択</option>
                  {ROAD_DIRECTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">接道種別</label>
                <select
                  value={item.road_type}
                  onChange={(e) => updateItem(index, 'road_type', e.target.value)}
                  disabled={disabled}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                >
                  <option value="">選択</option>
                  {ROAD_TYPES.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">道路幅員(m)</label>
                <input
                  type="number"
                  step="0.1"
                  value={item.road_width || ''}
                  onChange={(e) => updateItem(index, 'road_width', parseFloat(e.target.value) || 0)}
                  disabled={disabled}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                  placeholder="4.0"
                />
              </div>
              <button
                type="button"
                onClick={() => removeItem(index)}
                disabled={disabled}
                className="px-3 py-2 text-red-600 hover:bg-red-50 rounded text-sm"
              >
                削除
              </button>
              <div>
                <label className="block text-xs text-gray-600 mb-1">間口(m)</label>
                <input
                  type="number"
                  step="0.1"
                  value={item.frontage || ''}
                  onChange={(e) => updateItem(index, 'frontage', parseFloat(e.target.value) || 0)}
                  disabled={disabled}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                  placeholder="5.0"
                />
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <label className="block text-xs text-gray-600 mb-1">接道状況</label>
                <select
                  value={item.road_status}
                  onChange={(e) => updateItem(index, 'road_status', e.target.value)}
                  disabled={disabled}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                >
                  <option value="">選択</option>
                  {ROAD_STATUS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={addItem}
            disabled={disabled}
            className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
          >
            + 接道情報を追加
          </button>
        </>
      )}
    </div>
  );
};

// =================================================================
// 間取り詳細エディタ
// =================================================================

interface FloorPlan {
  floor: number;
  room_type: string;
  room_size: number;
  room_count: number;
}

const ROOM_TYPES = [
  { value: '10', label: 'R' },
  { value: '20', label: 'K' },
  { value: '25', label: 'SK' },
  { value: '30', label: 'DK' },
  { value: '35', label: 'SDK' },
  { value: '40', label: 'LK' },
  { value: '45', label: 'SLK' },
  { value: '50', label: 'LDK' },
  { value: '55', label: 'SLDK' },
];

export const FloorPlansEditor: React.FC<JsonEditorProps<FloorPlan>> = ({
  value = [],
  onChange,
  disabled
}) => {
  const addItem = () => {
    onChange([...value, { floor: 1, room_type: '', room_size: 0, room_count: 1 }]);
  };

  const removeItem = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof FloorPlan, fieldValue: string | number) => {
    const newValue = [...value];
    newValue[index] = { ...newValue[index], [field]: fieldValue };
    onChange(newValue);
  };

  return (
    <div className="space-y-3">
      {value.map((item, index) => (
        <div
          key={index}
          className="p-4 border border-gray-200 rounded-lg bg-white"
          style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr) auto', gap: '12px', alignItems: 'end' }}
        >
          <div>
            <label className="block text-xs text-gray-600 mb-1">階数</label>
            <input
              type="number"
              value={item.floor || ''}
              onChange={(e) => updateItem(index, 'floor', parseInt(e.target.value) || 1)}
              disabled={disabled}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              min="1"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">間取タイプ</label>
            <select
              value={item.room_type}
              onChange={(e) => updateItem(index, 'room_type', e.target.value)}
              disabled={disabled}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            >
              <option value="">選択</option>
              {ROOM_TYPES.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">広さ(帖)</label>
            <input
              type="number"
              step="0.5"
              value={item.room_size || ''}
              onChange={(e) => updateItem(index, 'room_size', parseFloat(e.target.value) || 0)}
              disabled={disabled}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">室数</label>
            <input
              type="number"
              value={item.room_count || ''}
              onChange={(e) => updateItem(index, 'room_count', parseInt(e.target.value) || 1)}
              disabled={disabled}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              min="1"
            />
          </div>
          <button
            type="button"
            onClick={() => removeItem(index)}
            disabled={disabled}
            className="px-3 py-2 text-red-600 hover:bg-red-50 rounded text-sm"
          >
            削除
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={addItem}
        disabled={disabled}
        className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
      >
        + 間取り情報を追加
      </button>
    </div>
  );
};

// =================================================================
// 設備エディタ（API連携版）
// =================================================================

interface Facility {
  code: string;
  name: string;
  category: string;
}

interface EquipmentItem {
  id: string;
  item_name: string;
  display_name: string;
}

export const FacilitiesEditor: React.FC<JsonEditorProps<Facility>> = ({
  value = [],
  onChange,
  disabled
}) => {
  const [categories, setCategories] = useState<Record<string, EquipmentItem[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // APIから設備マスターを取得
  useEffect(() => {
    const fetchEquipment = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/v1/equipment/grouped`);
        setCategories(response.data);
        setLoading(false);
      } catch (err) {
        console.error('設備マスター取得エラー:', err);
        setError('設備マスターの取得に失敗しました');
        setLoading(false);
      }
    };
    fetchEquipment();
  }, []);

  const isSelected = (code: string) => value.some(v => v.code === code);

  const toggleFacility = (code: string, name: string, category: string) => {
    if (isSelected(code)) {
      onChange(value.filter(v => v.code !== code));
    } else {
      onChange([...value, { code, name, category }]);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px' }}>
        {/* スケルトンローディング - スピナー禁止 */}
        {[1, 2, 3].map(i => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className="skeleton" style={{ width: '120px', height: '20px' }} />
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
              {[1, 2, 3, 4, 5, 6, 7, 8].map(j => (
                <div key={j} className="skeleton" style={{ height: '36px', borderRadius: '6px' }} />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '16px',
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        borderRadius: '8px',
        color: '#DC2626',
        fontSize: '14px',
      }}>
        {error}
      </div>
    );
  }

  // カテゴリをグループ化（親カテゴリ/子カテゴリ形式）
  const groupedCategories = Object.keys(categories).reduce((acc, fullCategoryName) => {
    const parts = fullCategoryName.split('/');
    const parentCategory = parts[0] || 'その他';
    const childCategory = parts.slice(1).join('/') || fullCategoryName;

    if (!acc[parentCategory]) {
      acc[parentCategory] = [];
    }
    acc[parentCategory].push({
      fullName: fullCategoryName,
      displayName: childCategory,
      items: categories[fullCategoryName]
    });
    return acc;
  }, {} as Record<string, { fullName: string; displayName: string; items: EquipmentItem[] }[]>);

  // 親カテゴリの表示順序（使用頻度順）
  const parentCategoryOrder = ['条件・設備', '金銭・建物', '土地', '金銭・条件'];
  const sortedParentCategories = parentCategoryOrder.filter(cat => groupedCategories[cat]);

  // 子カテゴリの表示順序（インフラ優先→使用頻度順）
  const childCategoryPriority: Record<string, number> = {
    // 最優先：インフラ系（ガス・水道・電気・排水）
    '設備(左) ガス': 1,
    '設備(左) 水道': 2,
    '設備(左) 電気': 3,
    '設備(左) 排水': 4,
    // 高優先：よく使う設備
    '設備(右) キッチン': 10,
    '設備(左) バス・トイレ': 11,
    '設備(左) 冷暖房・その他': 12,
    '設備(右) 収納': 13,
    '設備(右) セキュリティ': 14,
    '設備(右) 放送・通信・回線': 15,
    // 中優先
    '駐車場': 20,
    '設備(右) 駐輪・バイク': 21,
    '設備(左) 共有': 22,
    '設備(左) 構造・性能・仕様': 23,
    '設備(右) 構造・性能・仕様': 24,
    // 低優先：その他
    '設備(左) その他バス・トイレ': 30,
    '設備(右) その他キッチン': 31,
    '設備(左) その他設備': 32,
    '設備(右) その他': 33,
    // 土地系
    '権利・制限': 40,
    '面積・区画': 41,
    // 検査・証明系
    '設備(左) 建物検査': 50,
    '設備(左) 評価・証明書': 51,
    '空き家バンク': 52,
    // 建物
    '建物': 60,
    '部屋': 61,
  };

  // 子カテゴリをソート
  Object.keys(groupedCategories).forEach(parentCat => {
    groupedCategories[parentCat].sort((a, b) => {
      const priorityA = childCategoryPriority[a.displayName] || 100;
      const priorityB = childCategoryPriority[b.displayName] || 100;
      return priorityA - priorityB;
    });
  });

  // カテゴリアイコン取得
  const getCategoryIcon = (name: string) => {
    if (name.includes('キッチン')) return '🍳';
    if (name.includes('バス') || name.includes('トイレ')) return '🛁';
    if (name.includes('セキュリティ')) return '🔒';
    if (name.includes('収納')) return '🗄️';
    if (name.includes('通信') || name.includes('回線')) return '📡';
    if (name.includes('駐輪') || name.includes('バイク')) return '🚴';
    if (name.includes('駐車場')) return '🚗';
    if (name.includes('ガス')) return '🔥';
    if (name.includes('水道')) return '💧';
    if (name.includes('電気')) return '⚡';
    if (name.includes('排水')) return '🚿';
    if (name.includes('構造') || name.includes('性能')) return '🏗️';
    if (name.includes('評価') || name.includes('証明')) return '📜';
    if (name.includes('検査')) return '🔍';
    if (name.includes('共有')) return '🏢';
    if (name.includes('空き家')) return '🏚️';
    if (name.includes('土地')) return '🗺️';
    if (name.includes('建物')) return '🏠';
    if (name.includes('部屋')) return '🚪';
    if (name.includes('権利')) return '📋';
    if (name.includes('面積')) return '📐';
    return '⚙️';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* ヘッダー - 選択数表示 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 16px',
        backgroundColor: value.length > 0 ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
        borderRadius: '8px',
      }}>
        <span style={{ fontSize: '14px', color: '#6B7280' }}>
          選択中: <span style={{ fontWeight: 600, color: '#3B82F6' }}>{value.length}件</span>
        </span>
        {value.length > 0 && (
          <button
            type="button"
            onClick={() => onChange([])}
            disabled={disabled}
            style={{
              fontSize: '13px',
              color: '#EF4444',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px 8px',
            }}
          >
            すべて解除
          </button>
        )}
      </div>

      {/* 親カテゴリごとに表示 - 線なし、余白で区切る */}
      {sortedParentCategories.map(parentCategory => (
        <div key={parentCategory}>
          {/* 親カテゴリヘッダー - 線なし */}
          <h4 style={{
            fontSize: '15px',
            fontWeight: 700,
            color: '#1A1A1A',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <span style={{ fontSize: '18px' }}>
              {parentCategory === '条件・設備' && '🔧'}
              {parentCategory === '土地' && '🗺️'}
              {parentCategory === '金銭・建物' && '🏠'}
              {parentCategory === '金銭・条件' && '💰'}
            </span>
            {parentCategory}
          </h4>

          {/* 子カテゴリ - 余白で区切る */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingLeft: '8px' }}>
            {groupedCategories[parentCategory]?.map(subCat => (
              <div key={subCat.fullName}>
                {/* 子カテゴリタイトル */}
                <div style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#6B7280',
                  marginBottom: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}>
                  <span>{getCategoryIcon(subCat.displayName)}</span>
                  {subCat.displayName}
                  <span style={{
                    fontSize: '11px',
                    color: '#9CA3AF',
                    marginLeft: '4px',
                  }}>
                    {subCat.items?.filter(item => isSelected(item.id)).length || 0}/{subCat.items?.length || 0}
                  </span>
                </div>

                {/* チェックボックスグリッド - 枠線なし */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
                  gap: '4px'
                }}>
                  {subCat.items?.map(item => (
                    <label
                      key={item.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '8px 10px',
                        borderRadius: '6px',
                        cursor: disabled ? 'not-allowed' : 'pointer',
                        transition: 'background-color 150ms',
                        backgroundColor: isSelected(item.id) ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                        opacity: disabled ? 0.5 : 1,
                      }}
                      onMouseEnter={(e) => {
                        if (!disabled && !isSelected(item.id)) {
                          e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.04)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!disabled && !isSelected(item.id)) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected(item.id)}
                        onChange={() => toggleFacility(item.id, item.display_name, subCat.fullName)}
                        disabled={disabled}
                        style={{
                          marginRight: '8px',
                          width: '16px',
                          height: '16px',
                          accentColor: '#3B82F6',
                        }}
                      />
                      <span style={{
                        fontSize: '13px',
                        color: isSelected(item.id) ? '#1D4ED8' : '#374151',
                        fontWeight: isSelected(item.id) ? 500 : 400,
                      }}>
                        {item.display_name}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// =================================================================
// 交通情報エディタ
// =================================================================

interface Transportation {
  line_name: string;
  station_name: string;
  walk_minutes: number;
  bus_minutes?: number;
  bus_stop_name?: string;
}

export const TransportationEditor: React.FC<JsonEditorProps<Transportation>> = ({
  value = [],
  onChange,
  disabled
}) => {
  const addItem = () => {
    onChange([...value, {
      line_name: '',
      station_name: '',
      walk_minutes: 0
    }]);
  };

  const removeItem = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof Transportation, fieldValue: string | number | undefined) => {
    const newValue = [...value];
    newValue[index] = { ...newValue[index], [field]: fieldValue };
    onChange(newValue);
  };

  return (
    <div className="space-y-3">
      {value.map((item, index) => (
        <div
          key={index}
          className="p-4 border border-gray-200 rounded-lg bg-white"
        >
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr) auto', gap: '12px', alignItems: 'end' }}>
            <div>
              <label className="block text-xs text-gray-600 mb-1">路線名</label>
              <input
                type="text"
                value={item.line_name}
                onChange={(e) => updateItem(index, 'line_name', e.target.value)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                placeholder="JR山手線"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">駅名</label>
              <input
                type="text"
                value={item.station_name}
                onChange={(e) => updateItem(index, 'station_name', e.target.value)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                placeholder="渋谷"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">徒歩(分)</label>
              <input
                type="number"
                value={item.walk_minutes || ''}
                onChange={(e) => updateItem(index, 'walk_minutes', parseInt(e.target.value) || 0)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                min="0"
              />
            </div>
            <button
              type="button"
              onClick={() => removeItem(index)}
              disabled={disabled}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded text-sm"
            >
              削除
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginTop: '12px' }}>
            <div>
              <label className="block text-xs text-gray-600 mb-1">バス(分)※任意</label>
              <input
                type="number"
                value={item.bus_minutes || ''}
                onChange={(e) => updateItem(index, 'bus_minutes', e.target.value ? parseInt(e.target.value) : undefined)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                min="0"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">バス停名※任意</label>
              <input
                type="text"
                value={item.bus_stop_name || ''}
                onChange={(e) => updateItem(index, 'bus_stop_name', e.target.value)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              />
            </div>
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addItem}
        disabled={disabled}
        className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
      >
        + 交通情報を追加
      </button>
    </div>
  );
};

// =================================================================
// リフォーム履歴エディタ
// =================================================================

interface Renovation {
  year: number;
  month?: number;
  item: string;
  description?: string;
}

const RENOVATION_ITEMS = [
  'キッチン',
  '浴室',
  'トイレ',
  '洗面台',
  '床',
  '壁紙',
  '外壁',
  '屋根',
  '給湯器',
  '配管',
  '窓・サッシ',
  '電気設備',
  '防水工事',
  'その他',
];

export const RenovationsEditor: React.FC<JsonEditorProps<Renovation>> = ({
  value = [],
  onChange,
  disabled
}) => {
  const currentYear = new Date().getFullYear();

  const addItem = () => {
    onChange([...value, { year: currentYear, item: '' }]);
  };

  const removeItem = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof Renovation, fieldValue: string | number | undefined) => {
    const newValue = [...value];
    newValue[index] = { ...newValue[index], [field]: fieldValue };
    onChange(newValue);
  };

  return (
    <div className="space-y-3">
      {value.map((item, index) => (
        <div
          key={index}
          className="p-4 border border-gray-200 rounded-lg bg-white"
        >
          <div style={{ display: 'grid', gridTemplateColumns: '100px 80px 1fr auto', gap: '12px', alignItems: 'end' }}>
            <div>
              <label className="block text-xs text-gray-600 mb-1">実施年</label>
              <input
                type="number"
                value={item.year || ''}
                onChange={(e) => updateItem(index, 'year', parseInt(e.target.value) || currentYear)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                min="1900"
                max={currentYear}
              />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">月</label>
              <select
                value={item.month || ''}
                onChange={(e) => updateItem(index, 'month', e.target.value ? parseInt(e.target.value) : undefined)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="">--</option>
                {[...Array(12)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>{i + 1}月</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">項目</label>
              <select
                value={item.item}
                onChange={(e) => updateItem(index, 'item', e.target.value)}
                disabled={disabled}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              >
                <option value="">選択</option>
                {RENOVATION_ITEMS.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={() => removeItem(index)}
              disabled={disabled}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded text-sm"
            >
              削除
            </button>
          </div>
          <div style={{ marginTop: '12px' }}>
            <label className="block text-xs text-gray-600 mb-1">詳細説明※任意</label>
            <input
              type="text"
              value={item.description || ''}
              onChange={(e) => updateItem(index, 'description', e.target.value)}
              disabled={disabled}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
              placeholder="リフォーム内容の詳細"
            />
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={addItem}
        disabled={disabled}
        className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors"
      >
        + リフォーム履歴を追加
      </button>
    </div>
  );
};
