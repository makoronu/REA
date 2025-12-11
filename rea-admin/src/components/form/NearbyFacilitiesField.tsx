import React, { useState } from 'react';
import { useFormContext, Controller } from 'react-hook-form';

interface NearbyFacility {
  facility_name: string;
  category: string;
  distance_meters: number;
  walk_minutes: number;
}

interface NearbyFacilitiesFieldProps {
  disabled?: boolean;
}

// 施設カテゴリ
const FACILITY_CATEGORIES = [
  { value: 'convenience', label: 'コンビニ' },
  { value: 'supermarket', label: 'スーパー' },
  { value: 'hospital', label: '病院・クリニック' },
  { value: 'bank', label: '銀行・ATM' },
  { value: 'post_office', label: '郵便局' },
  { value: 'park', label: '公園' },
  { value: 'drugstore', label: 'ドラッグストア' },
  { value: 'restaurant', label: '飲食店' },
  { value: 'shopping', label: 'ショッピング施設' },
  { value: 'gym', label: 'スポーツ施設' },
  { value: 'library', label: '図書館' },
  { value: 'other', label: 'その他' },
];

export const NearbyFacilitiesField: React.FC<NearbyFacilitiesFieldProps> = ({ disabled = false }) => {
  const { control } = useFormContext();
  const [newFacility, setNewFacility] = useState({
    facility_name: '',
    category: 'convenience',
    distance_meters: '',
    walk_minutes: ''
  });

  const getCategoryLabel = (value: string) => {
    return FACILITY_CATEGORIES.find(c => c.value === value)?.label || value;
  };

  return (
    <Controller
      name="nearby_facilities"
      control={control}
      defaultValue={[]}
      render={({ field }) => {
        const facilities: NearbyFacility[] = field.value || [];

        const addFacility = () => {
          if (!newFacility.facility_name) return;
          if (facilities.length >= 10) return;

          const distance = parseInt(newFacility.distance_meters) || 0;
          const walkMinutes = newFacility.walk_minutes
            ? parseInt(newFacility.walk_minutes)
            : Math.ceil(distance / 80); // 80m/分で概算

          field.onChange([...facilities, {
            facility_name: newFacility.facility_name,
            category: newFacility.category,
            distance_meters: distance,
            walk_minutes: walkMinutes
          }]);
          setNewFacility({ facility_name: '', category: 'convenience', distance_meters: '', walk_minutes: '' });
        };

        const removeFacility = (index: number) => {
          field.onChange(facilities.filter((_, i) => i !== index));
        };

        return (
          <div style={{ marginTop: '8px' }}>
            {/* 登録済み施設 */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                登録済み（{facilities.length}/10）
              </div>
              {facilities.length === 0 ? (
                <p style={{ fontSize: '13px', color: '#9CA3AF' }}>近隣施設が登録されていません</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {facilities.map((facility, index) => (
                    <div
                      key={`${facility.facility_name}-${index}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '10px 12px',
                        backgroundColor: '#F9FAFB',
                        borderRadius: '8px',
                      }}
                    >
                      <span style={{
                        padding: '2px 8px',
                        backgroundColor: '#E0E7FF',
                        color: '#3730A3',
                        fontSize: '11px',
                        fontWeight: 500,
                        borderRadius: '4px',
                      }}>
                        {getCategoryLabel(facility.category)}
                      </span>
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 500 }}>{facility.facility_name}</span>
                      </div>
                      <div style={{ fontSize: '13px', color: '#6B7280' }}>
                        {facility.distance_meters}m（徒歩{facility.walk_minutes}分）
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFacility(index)}
                        disabled={disabled}
                        style={{
                          padding: '4px',
                          backgroundColor: 'transparent',
                          border: 'none',
                          cursor: disabled ? 'not-allowed' : 'pointer',
                          color: '#EF4444',
                        }}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 追加フォーム */}
            <div style={{ padding: '12px', backgroundColor: '#EDE9FE', borderRadius: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#5B21B6', marginBottom: '8px' }}>
                近隣施設を追加
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                <select
                  value={newFacility.category}
                  onChange={(e) => setNewFacility({ ...newFacility, category: e.target.value })}
                  disabled={disabled || facilities.length >= 10}
                  style={{
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #C4B5FD',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                >
                  {FACILITY_CATEGORIES.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
                <input
                  type="text"
                  value={newFacility.facility_name}
                  onChange={(e) => setNewFacility({ ...newFacility, facility_name: e.target.value })}
                  placeholder="施設名"
                  disabled={disabled || facilities.length >= 10}
                  style={{
                    flex: 1,
                    minWidth: '150px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #C4B5FD',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <input
                  type="number"
                  value={newFacility.distance_meters}
                  onChange={(e) => setNewFacility({ ...newFacility, distance_meters: e.target.value })}
                  placeholder="距離(m)"
                  disabled={disabled || facilities.length >= 10}
                  min="0"
                  style={{
                    width: '80px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #C4B5FD',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <input
                  type="number"
                  value={newFacility.walk_minutes}
                  onChange={(e) => setNewFacility({ ...newFacility, walk_minutes: e.target.value })}
                  placeholder="徒歩(分)"
                  disabled={disabled || facilities.length >= 10}
                  min="1"
                  style={{
                    width: '80px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #C4B5FD',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <button
                  type="button"
                  onClick={addFacility}
                  disabled={disabled || !newFacility.facility_name || facilities.length >= 10}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    backgroundColor: newFacility.facility_name && facilities.length < 10 ? '#7C3AED' : '#D1D5DB',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: disabled || !newFacility.facility_name || facilities.length >= 10 ? 'not-allowed' : 'pointer',
                  }}
                >
                  追加
                </button>
              </div>
              <p style={{ fontSize: '11px', color: '#6B7280', marginTop: '8px' }}>
                ※ 徒歩分数を空欄にすると距離から自動計算します（80m/分）
              </p>
            </div>
          </div>
        );
      }}
    />
  );
};

export default NearbyFacilitiesField;
