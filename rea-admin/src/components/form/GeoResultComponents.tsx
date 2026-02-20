/**
 * GeoPanel結果表示コンポーネント
 *
 * GeoPanel一括取得結果の学区・駅・バス停・施設を表示する子コンポーネント群
 */
import React from 'react';

// =============================================================================
// 型定義（GeoPanel共通）
// =============================================================================

export interface SchoolCandidate {
  school_name: string;
  address: string | null;
  admin_type: string | null;
  distance_meters: number;
  walk_minutes: number;
  is_in_district: boolean;
}

export interface StationCandidate {
  station_id: number;
  station_name: string;
  line_name: string | null;
  company_name: string | null;
  distance_meters: number;
  walk_minutes: number;
}

export interface BusStopCandidate {
  name: string;
  bus_type: string | null;
  operators: string[];
  routes: string[];
  distance_meters: number;
  walk_minutes: number;
}

export interface FacilityItem {
  id: string;
  name: string;
  category: string;
  category_name: string;
  address: string;
  distance_meters: number;
  walk_minutes: number;
}

/** 一括取得の結果 */
export interface FetchResults {
  schools: {
    elementary: SchoolCandidate[];
    juniorHigh: SchoolCandidate[];
  } | null;
  stations: StationCandidate[];
  busStops: BusStopCandidate[];
  facilities: FacilityItem[];
  errors: string[];
}

// =============================================================================
// 学区結果表示
// =============================================================================

/** 学区結果表示 */
export const SchoolResultSection: React.FC<{
  elementary: SchoolCandidate[];
  juniorHigh: SchoolCandidate[];
  selectedElementary: string | null;
  selectedJuniorHigh: string | null;
  onSelectElementary: (school: SchoolCandidate) => void;
  onSelectJuniorHigh: (school: SchoolCandidate) => void;
}> = ({ elementary, juniorHigh, selectedElementary, selectedJuniorHigh, onSelectElementary, onSelectJuniorHigh }) => {
  const renderList = (
    title: string,
    candidates: SchoolCandidate[],
    selectedName: string | null,
    onSelect: (s: SchoolCandidate) => void
  ) => (
    <div style={{ marginBottom: '12px' }}>
      <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>{title}</div>
      {candidates.length === 0 ? (
        <div style={{ fontSize: '12px', color: '#9CA3AF' }}>候補なし</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {candidates.slice(0, 5).map((school, i) => {
            const isSelected = selectedName === school.school_name;
            return (
              <button
                key={i}
                type="button"
                onClick={() => onSelect(school)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 10px',
                  backgroundColor: isSelected ? '#EFF6FF' : school.is_in_district ? '#FEF2F2' : '#F9FAFB',
                  border: isSelected ? '2px solid #3B82F6' : school.is_in_district ? '2px solid #EF4444' : '1px solid #E5E7EB',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div>
                  <span style={{
                    fontSize: '13px',
                    fontWeight: school.is_in_district ? 600 : 400,
                    color: school.is_in_district ? '#DC2626' : '#1F2937',
                  }}>
                    {school.school_name}
                    {school.is_in_district && (
                      <span style={{
                        marginLeft: '6px', fontSize: '10px', backgroundColor: '#DC2626',
                        color: '#fff', padding: '1px 4px', borderRadius: '3px',
                      }}>学区内</span>
                    )}
                    {isSelected && (
                      <span style={{
                        marginLeft: '6px', fontSize: '10px', backgroundColor: '#3B82F6',
                        color: '#fff', padding: '1px 4px', borderRadius: '3px',
                      }}>選択中</span>
                    )}
                  </span>
                </div>
                <span style={{ fontSize: '12px', color: '#6B7280', whiteSpace: 'nowrap', marginLeft: '8px' }}>
                  徒歩{school.walk_minutes}分
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );

  return (
    <div>
      <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }}>
        <span style={{ color: '#DC2626', fontWeight: 600 }}>●赤字</span> = 学区データあり ／ クリックで選択
      </div>
      {renderList('小学校', elementary, selectedElementary, onSelectElementary)}
      {renderList('中学校', juniorHigh, selectedJuniorHigh, onSelectJuniorHigh)}
    </div>
  );
};

// =============================================================================
// 駅選択リスト
// =============================================================================

/** 駅選択リスト */
export const StationSelectList: React.FC<{
  stations: StationCandidate[];
  selectedIndices: Set<number>;
  onToggle: (index: number) => void;
}> = ({ stations, selectedIndices, onToggle }) => {
  if (stations.length === 0) return <span style={{ fontSize: '12px', color: '#9CA3AF' }}>候補なし</span>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {stations.map((s, i) => (
        <label key={i} style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          padding: '6px 8px', borderRadius: '6px', cursor: 'pointer',
          backgroundColor: selectedIndices.has(i) ? '#EFF6FF' : '#F9FAFB',
          border: selectedIndices.has(i) ? '1px solid #93C5FD' : '1px solid #E5E7EB',
        }}>
          <input
            type="checkbox"
            checked={selectedIndices.has(i)}
            onChange={() => onToggle(i)}
            style={{ accentColor: '#3B82F6' }}
          />
          <span style={{ fontSize: '13px', color: '#1F2937', flex: 1 }}>
            {s.station_name}駅（{s.line_name || ''}）
          </span>
          <span style={{ fontSize: '12px', color: '#6B7280', whiteSpace: 'nowrap' }}>
            徒歩{s.walk_minutes}分
          </span>
        </label>
      ))}
    </div>
  );
};

// =============================================================================
// バス停選択リスト
// =============================================================================

/** バス停選択リスト */
export const BusStopSelectList: React.FC<{
  busStops: BusStopCandidate[];
  selectedIndices: Set<number>;
  onToggle: (index: number) => void;
}> = ({ busStops, selectedIndices, onToggle }) => {
  if (busStops.length === 0) return <span style={{ fontSize: '12px', color: '#9CA3AF' }}>候補なし</span>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {busStops.map((bs, i) => (
        <label key={i} style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          padding: '6px 8px', borderRadius: '6px', cursor: 'pointer',
          backgroundColor: selectedIndices.has(i) ? '#EFF6FF' : '#F9FAFB',
          border: selectedIndices.has(i) ? '1px solid #93C5FD' : '1px solid #E5E7EB',
        }}>
          <input
            type="checkbox"
            checked={selectedIndices.has(i)}
            onChange={() => onToggle(i)}
            style={{ accentColor: '#3B82F6' }}
          />
          <span style={{ fontSize: '13px', color: '#1F2937', flex: 1 }}>
            {bs.name}
            {bs.routes.length > 0 && (
              <span style={{ fontSize: '11px', color: '#6B7280', marginLeft: '4px' }}>
                ({bs.routes.join('・')})
              </span>
            )}
          </span>
          <span style={{ fontSize: '12px', color: '#6B7280', whiteSpace: 'nowrap' }}>
            徒歩{bs.walk_minutes}分
          </span>
        </label>
      ))}
    </div>
  );
};

// =============================================================================
// 施設選択リスト（カテゴリ別）
// =============================================================================

/** 施設選択リスト（カテゴリ別） */
export const FacilitySelectList: React.FC<{
  facilities: FacilityItem[];
  selectedIndices: Set<number>;
  onToggle: (index: number) => void;
}> = ({ facilities, selectedIndices, onToggle }) => {
  if (facilities.length === 0) return <span style={{ fontSize: '12px', color: '#9CA3AF' }}>候補なし</span>;
  // カテゴリ別にグルーピング（元の配列インデックスを保持）
  const byCategory: { catName: string; items: { facility: FacilityItem; originalIndex: number }[] }[] = [];
  const catMap = new Map<string, number>();
  facilities.forEach((f, i) => {
    const catIdx = catMap.get(f.category);
    if (catIdx !== undefined) {
      byCategory[catIdx].items.push({ facility: f, originalIndex: i });
    } else {
      catMap.set(f.category, byCategory.length);
      byCategory.push({ catName: f.category_name, items: [{ facility: f, originalIndex: i }] });
    }
  });
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {byCategory.map((group) => (
        <div key={group.catName}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
            {group.catName}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
            {group.items.map(({ facility, originalIndex }) => (
              <label key={originalIndex} style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '5px 8px', borderRadius: '6px', cursor: 'pointer',
                backgroundColor: selectedIndices.has(originalIndex) ? '#EFF6FF' : '#F9FAFB',
                border: selectedIndices.has(originalIndex) ? '1px solid #93C5FD' : '1px solid #E5E7EB',
              }}>
                <input
                  type="checkbox"
                  checked={selectedIndices.has(originalIndex)}
                  onChange={() => onToggle(originalIndex)}
                  style={{ accentColor: '#3B82F6' }}
                />
                <span style={{ fontSize: '13px', color: '#1F2937', flex: 1 }}>
                  {facility.name}
                </span>
                <span style={{ fontSize: '12px', color: '#6B7280', whiteSpace: 'nowrap' }}>
                  {facility.distance_meters}m（徒歩{facility.walk_minutes}分）
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
