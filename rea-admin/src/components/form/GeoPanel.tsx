import React, { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { FieldGroup } from './FieldFactory';
import { ColumnWithLabel } from '../../services/metadataService';
import { SelectableListModal, SelectableItem, Category } from '../common/SelectableListModal';
import { API_PATHS } from '../../constants/apiPaths';
import { api } from '../../services/api';
import { GEO_SEARCH_CONFIG } from '../../constants';

// 学校候補の型
interface SchoolCandidate {
  school_name: string;
  address: string | null;
  admin_type: string | null;
  distance_meters: number;
  walk_minutes: number;
  is_in_district: boolean;
}

// バス停候補の型
interface BusStopCandidate {
  name: string;
  bus_type: string | null;
  operators: string[];
  routes: string[];
  distance_meters: number;
  walk_minutes: number;
}

// 駅候補の型
interface StationCandidate {
  station_id: number;
  station_name: string;
  line_name: string | null;
  company_name: string | null;
  distance_meters: number;
  walk_minutes: number;
}

// FacilityCandidate, FacilitiesByCategory は SelectableListModal を使うようになり不要

// =============================================================================
// Geo セクション共通コンポーネント
// =============================================================================

/** コンパクトサマリーカード（フォーム内インライン表示用） */
const GeoSectionCard: React.FC<{
  icon: string;
  title: string;
  count: number;
  statusText?: string;
  onEdit: () => void;
}> = ({ icon, title, count, statusText, onEdit }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 16px',
    backgroundColor: statusText ? '#FEF3C7' : '#F9FAFB',
    border: '1px solid #E5E7EB',
    borderRadius: '8px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span style={{ fontSize: '16px' }}>{icon}</span>
      <span style={{ fontSize: '14px', fontWeight: 600, color: '#374151' }}>{title}</span>
      {statusText ? (
        <span style={{ fontSize: '13px', color: '#92400E', fontWeight: 500 }}>{statusText}</span>
      ) : count > 0 ? (
        <span style={{
          fontSize: '12px',
          backgroundColor: '#DBEAFE',
          color: '#1E40AF',
          padding: '2px 8px',
          borderRadius: '10px',
          fontWeight: 500,
        }}>
          {count}件
        </span>
      ) : (
        <span style={{ fontSize: '13px', color: '#9CA3AF' }}>未設定</span>
      )}
    </div>
    <button
      type="button"
      onClick={onEdit}
      style={{
        padding: '6px 16px',
        backgroundColor: '#fff',
        border: '1px solid #D1D5DB',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '13px',
        color: '#374151',
        fontWeight: 500,
      }}
    >
      編集
    </button>
  </div>
);

/** Geoセクション管理モーダル */
const GeoManagementModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 999,
    }} onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflow: 'auto',
        padding: '24px',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#1F2937', margin: 0 }}>{title}</h3>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none', border: 'none', fontSize: '24px',
              cursor: 'pointer', color: '#9CA3AF', lineHeight: 1,
            }}
          >×</button>
        </div>
        {children}
      </div>
    </div>
  );
};

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
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await api.get(API_PATHS.GEO.SCHOOL_DISTRICTS, {
        params: { lat, lng }
      });

      const data = response.data;
      setElementaryCandidates(data.elementary || []);
      setJuniorHighCandidates(data.junior_high || []);
      setShowCandidates(true);

      setMessage({ type: 'success', text: '学校候補を取得しました。選択してください。' });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '学校情報の取得に失敗しました';
      setMessage({ type: 'error', text: message });
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
            {candidates.slice(0, 5).map((school, index) => {
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
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px', lineHeight: 1, padding: '0 4px', color: 'inherit' }}>&times;</button>
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

// 最寄駅なしフラグ検出
const isNoStation = (v: any): boolean => {
  return v && typeof v === 'object' && !Array.isArray(v) && v.no_station === true;
};

// 駅自動取得・選択コンポーネント（モーダル版）
const StationAutoFetchButton: React.FC = () => {
  const { getValues, setValue, watch } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);

  // 最寄駅なしの状態を監視
  const transportationValue = watch('transportation');
  const noStation = isNoStation(transportationValue);

  const handleNoStationChange = (checked: boolean) => {
    if (checked) {
      setValue('transportation', { no_station: true }, { shouldDirty: true });
    } else {
      setValue('transportation', [], { shouldDirty: true });
    }
  };

  const handleFetch = async () => {
    const lat = getValues('latitude');
    const lng = getValues('longitude');

    if (!lat || !lng) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await api.get(API_PATHS.GEO.NEAREST_STATIONS, {
        params: { lat, lng, radius: GEO_SEARCH_CONFIG.STATION.RADIUS_M, limit: GEO_SEARCH_CONFIG.STATION.LIMIT }
      });

      const data = response.data;
      const stations = data.stations || [];

      // 路線別にグループ化
      const byLine: { [key: string]: StationCandidate[] } = {};
      stations.forEach((s: StationCandidate) => {
        const line = s.line_name || '不明';
        if (!byLine[line]) byLine[line] = [];
        byLine[line].push(s);
      });

      // Category形式に変換
      const categoriesData: Category[] = Object.entries(byLine).map(([line, stns]) => ({
        code: line,
        name: line,
        icon: '🚃',
        items: stns.map((s) => ({
          id: `${s.station_name}_${s.line_name}`,
          name: `${s.station_name}駅`,
          subText: `徒歩${s.walk_minutes}分 (${s.distance_meters.toLocaleString()}m)${s.company_name ? ` - ${s.company_name}` : ''}`,
          category: line,
          _raw: { station_name: s.station_name, line_name: s.line_name, walk_minutes: s.walk_minutes },
        })),
      }));

      setCategories(categoriesData);
      setIsModalOpen(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '駅情報の取得に失敗しました';
      setMessage({ type: 'error', text: message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const val = getValues('transportation');
    const currentStations = Array.isArray(val) ? val : [];
    const rawData = (item as any)._raw;

    const newStation = {
      station_name: rawData?.station_name || item.name.replace('駅', ''),
      line_name: rawData?.line_name || '',
      walk_minutes: rawData?.walk_minutes,
    };

    setValue('transportation', [...currentStations, newStation], { shouldDirty: true });
  };

  const handleRemove = (item: SelectableItem) => {
    const val = getValues('transportation');
    const currentStations = Array.isArray(val) ? val : [];
    const updated = currentStations.filter((s: any) =>
      `${s.station_name}_${s.line_name}` !== item.id
    );
    setValue('transportation', updated, { shouldDirty: true });
  };

  const transportationVal = getValues('transportation');
  const currentStations = Array.isArray(transportationVal) ? transportationVal : [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentStations.map((s: any) => ({
    id: `${s.station_name}_${s.line_name}`,
    name: `${s.station_name}駅`,
    subText: `${s.line_name ? s.line_name + ' ・ ' : ''}徒歩${s.walk_minutes}分`,
  }));

  const [isManageOpen, setIsManageOpen] = useState(false);

  return (
    <>
      {/* コンパクトサマリーカード */}
      <GeoSectionCard
        icon="🚃"
        title="電車・鉄道"
        count={currentStations.length}
        statusText={noStation ? '最寄駅なし' : undefined}
        onEdit={() => setIsManageOpen(true)}
      />

      {/* 管理モーダル */}
      <GeoManagementModal
        isOpen={isManageOpen}
        onClose={() => setIsManageOpen(false)}
        title="電車・鉄道"
      >
        {/* 最寄駅なしチェックボックス */}
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: noStation ? '#FEF3C7' : '#F9FAFB', borderRadius: '8px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={noStation}
              onChange={(e) => handleNoStationChange(e.target.checked)}
              style={{ width: '18px', height: '18px', cursor: 'pointer' }}
            />
            <span style={{ fontWeight: 500 }}>最寄駅なし（離島・山間部等）</span>
          </label>
          {noStation && (
            <p style={{ fontSize: '12px', color: '#92400E', marginTop: '8px', marginLeft: '26px' }}>
              最寄駅がない物件として登録されます
            </p>
          )}
        </div>

        {!noStation && (
          <>
            {/* 選択済み駅リスト */}
            {currentStations.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                  登録済み駅 ({currentStations.length}件)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {currentStations.map((s: any, index: number) => (
                    <div
                      key={index}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 12px',
                        backgroundColor: '#F9FAFB',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '14px', color: '#1F2937' }}>
                          {s.station_name}駅
                        </div>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                          {s.line_name && `${s.line_name} ・ `}徒歩{s.walk_minutes}分
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemove({ id: `${s.station_name}_${s.line_name}`, name: s.station_name })}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#EF4444',
                          cursor: 'pointer',
                          padding: '4px 8px',
                          fontSize: '13px',
                        }}
                      >
                        削除
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 駅追加ボタン */}
            <button
              type="button"
              onClick={handleFetch}
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: isLoading ? '#9CA3AF' : '#fff',
                border: '1px dashed #D1D5DB',
                borderRadius: '8px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                color: '#6B7280',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.15s',
              }}
            >
              {isLoading ? (
                <>
                  <span style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '16px',
                    border: '2px solid #9CA3AF',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                  }} />
                  検索中...
                </>
              ) : (
                <>🚃 最寄駅を追加</>
              )}
            </button>
          </>
        )}

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
      </GeoManagementModal>

      {/* 駅選択モーダル（管理モーダルの上にスタック） */}
      <SelectableListModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="最寄駅を選択"
        categories={categories}
        selectedItems={selectedItems}
        onAdd={handleAdd}
        onRemove={handleRemove}
        searchable={true}
        maxItems={10}
      />

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

// バス停なしフラグ検出
const isNoBus = (v: any): boolean => {
  return v && typeof v === 'object' && !Array.isArray(v) && v.no_bus === true;
};

// バス停自動取得・選択コンポーネント（モーダル版）
const BusStopAutoFetchButton: React.FC = () => {
  const { getValues, setValue, watch } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);

  // バス停なしの状態を監視
  const busStopsValue = watch('bus_stops');
  const noBus = isNoBus(busStopsValue);

  const handleNoBusChange = (checked: boolean) => {
    if (checked) {
      setValue('bus_stops', { no_bus: true }, { shouldDirty: true });
    } else {
      setValue('bus_stops', [], { shouldDirty: true });
    }
  };

  const handleFetch = async () => {
    const lat = getValues('latitude');
    const lng = getValues('longitude');

    if (!lat || !lng) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await api.get(API_PATHS.GEO.NEAREST_BUS_STOPS, {
        params: { lat, lng, limit: GEO_SEARCH_CONFIG.BUS_STOP.LIMIT }
      });

      const data = response.data;
      const busStops = data.bus_stops || [];

      // バス種別でグループ化
      const byType: { [key: string]: BusStopCandidate[] } = {};
      busStops.forEach((bs: BusStopCandidate) => {
        const type = bs.bus_type || '路線バス';
        if (!byType[type]) byType[type] = [];
        byType[type].push(bs);
      });

      // Category形式に変換
      const categoriesData: Category[] = Object.entries(byType).map(([type, stops]) => ({
        code: type,
        name: type,
        icon: '🚌',
        items: stops.map((bs) => ({
          id: bs.name,
          name: bs.name,
          subText: `徒歩${bs.walk_minutes}分 (${bs.distance_meters.toLocaleString()}m)${bs.routes.length > 0 ? ` - ${bs.routes.slice(0, 2).join(', ')}${bs.routes.length > 2 ? '...' : ''}` : ''}`,
          category: type,
          _raw: { name: bs.name, walk_minutes: bs.walk_minutes, routes: bs.routes },
        })),
      }));

      setCategories(categoriesData);
      setIsModalOpen(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'バス停情報の取得に失敗しました';
      setMessage({ type: 'error', text: message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const val = getValues('bus_stops');
    const currentBusStops = Array.isArray(val) ? val : [];
    const rawData = (item as any)._raw;

    const newBusStop = {
      name: rawData?.name || item.name,
      walk_minutes: rawData?.walk_minutes,
      routes: rawData?.routes || [],
    };

    setValue('bus_stops', [...currentBusStops, newBusStop], { shouldDirty: true });
  };

  const handleRemove = (item: SelectableItem) => {
    const val = getValues('bus_stops');
    const currentBusStops = Array.isArray(val) ? val : [];
    const updated = currentBusStops.filter((bs: any) => bs.name !== item.id);
    setValue('bus_stops', updated, { shouldDirty: true });
  };

  const busStopsVal = getValues('bus_stops');
  const currentBusStops = Array.isArray(busStopsVal) ? busStopsVal : [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentBusStops.map((bs: any) => ({
    id: bs.name,
    name: bs.name,
    subText: `徒歩${bs.walk_minutes}分`,
  }));

  const [isManageOpen, setIsManageOpen] = useState(false);

  return (
    <>
      {/* コンパクトサマリーカード */}
      <GeoSectionCard
        icon="🚌"
        title="バス"
        count={currentBusStops.length}
        statusText={noBus ? 'バス停なし' : undefined}
        onEdit={() => setIsManageOpen(true)}
      />

      {/* 管理モーダル */}
      <GeoManagementModal
        isOpen={isManageOpen}
        onClose={() => setIsManageOpen(false)}
        title="バス"
      >
        {/* バス停なしチェックボックス */}
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: noBus ? '#FEF3C7' : '#F9FAFB', borderRadius: '8px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={noBus}
              onChange={(e) => handleNoBusChange(e.target.checked)}
              style={{ width: '18px', height: '18px', cursor: 'pointer' }}
            />
            <span style={{ fontWeight: 500 }}>バス停なし（離島・山間部等）</span>
          </label>
          {noBus && (
            <p style={{ fontSize: '12px', color: '#92400E', marginTop: '8px', marginLeft: '26px' }}>
              バス停がない物件として登録されます
            </p>
          )}
        </div>

        {!noBus && (
          <>
            {/* 選択済みバス停リスト */}
            {currentBusStops.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                  登録済みバス停 ({currentBusStops.length}件)
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {currentBusStops.map((bs: any, index: number) => (
                    <div
                      key={index}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 12px',
                        backgroundColor: '#F9FAFB',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px',
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '14px', color: '#1F2937' }}>
                          {bs.name}
                        </div>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                          徒歩{bs.walk_minutes}分
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemove({ id: bs.name, name: bs.name })}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#EF4444',
                          cursor: 'pointer',
                          padding: '4px 8px',
                          fontSize: '13px',
                        }}
                      >
                        削除
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* バス停追加ボタン */}
            <button
              type="button"
              onClick={handleFetch}
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: isLoading ? '#9CA3AF' : '#fff',
                border: '1px dashed #D1D5DB',
                borderRadius: '8px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                color: '#6B7280',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.15s',
              }}
            >
              {isLoading ? (
                <>
                  <span style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '16px',
                    border: '2px solid #9CA3AF',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                  }} />
                  検索中...
                </>
              ) : (
                <>🚌 バス停を追加</>
              )}
            </button>
          </>
        )}

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
      </GeoManagementModal>

      {/* バス停選択モーダル（管理モーダルの上にスタック） */}
      <SelectableListModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="バス停を選択"
        categories={categories}
        selectedItems={selectedItems}
        onAdd={handleAdd}
        onRemove={handleRemove}
        searchable={true}
        maxItems={5}
      />

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

// 周辺施設自動取得コンポーネント（モーダル版）
const FacilityAutoFetchButton: React.FC = () => {
  const { getValues, setValue } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);

  const handleFetch = async () => {
    const lat = getValues('latitude');
    const lng = getValues('longitude');

    if (!lat || !lng) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await api.get(API_PATHS.GEO.NEAREST_FACILITIES, {
        params: { lat, lng, limit_per_category: GEO_SEARCH_CONFIG.FACILITY.LIMIT_PER_CATEGORY }
      });

      const data = response.data;

      // APIレスポンスをモーダル用のCategory形式に変換
      const categoriesData: Category[] = Object.entries(data.categories || {}).map(
        ([catCode, catData]: [string, any]) => ({
          code: catCode,
          name: catData.category_name,
          icon: catData.icon,
          items: catData.facilities.map((f: any) => ({
            id: f.id,
            name: f.name,
            subText: `徒歩${f.walk_minutes}分 (${f.distance_meters.toLocaleString()}m)`,
            category: catCode,
            // 追加データ保持用
            _raw: {
              address: f.address,
              walk_minutes: f.walk_minutes,
              category_name: catData.category_name,
            },
          })),
        })
      ).filter((cat) => cat.items.length > 0);

      setCategories(categoriesData);
      setIsModalOpen(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '施設情報の取得に失敗しました';
      setMessage({ type: 'error', text: message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const val = getValues('nearby_facilities');
    const currentFacilities = Array.isArray(val) ? val : [];
    const rawData = (item as any)._raw;

    const newFacility = {
      id: item.id,
      name: item.name,
      category: item.category,
      category_name: rawData?.category_name || item.category,
      address: rawData?.address,
      walk_minutes: rawData?.walk_minutes,
    };

    setValue('nearby_facilities', [...currentFacilities, newFacility], { shouldDirty: true });
  };

  const handleRemove = (item: SelectableItem) => {
    const val = getValues('nearby_facilities');
    const currentFacilities = Array.isArray(val) ? val : [];
    const updated = currentFacilities.filter((f: any) => f.id !== item.id);
    setValue('nearby_facilities', updated, { shouldDirty: true });
  };

  const facilitiesVal = getValues('nearby_facilities');
  const currentFacilities = Array.isArray(facilitiesVal) ? facilitiesVal : [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentFacilities.map((f: any) => ({
    id: f.id,
    name: f.name,
    subText: `徒歩${f.walk_minutes}分`,
    category: f.category,
  }));

  const [isManageOpen, setIsManageOpen] = useState(false);

  return (
    <>
      {/* コンパクトサマリーカード */}
      <GeoSectionCard
        icon="🏪"
        title="周辺施設"
        count={currentFacilities.length}
        onEdit={() => setIsManageOpen(true)}
      />

      {/* 管理モーダル */}
      <GeoManagementModal
        isOpen={isManageOpen}
        onClose={() => setIsManageOpen(false)}
        title="周辺施設"
      >
        {/* 選択済み施設リスト */}
        {currentFacilities.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
              登録済み施設 ({currentFacilities.length}件)
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {currentFacilities.map((f: any) => (
                <div
                  key={f.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 12px',
                    backgroundColor: '#F9FAFB',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '14px', color: '#1F2937' }}>
                      {f.name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                      {f.category_name} ・ 徒歩{f.walk_minutes}分
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemove({ id: f.id, name: f.name })}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#EF4444',
                      cursor: 'pointer',
                      padding: '4px 8px',
                      fontSize: '13px',
                    }}
                  >
                    削除
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 施設追加ボタン */}
        <button
          type="button"
          onClick={handleFetch}
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '12px 16px',
            backgroundColor: isLoading ? '#9CA3AF' : '#fff',
            border: '1px dashed #D1D5DB',
            borderRadius: '8px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            color: '#6B7280',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            transition: 'all 0.15s',
          }}
        >
          {isLoading ? (
            <>
              <span style={{
                display: 'inline-block',
                width: '16px',
                height: '16px',
                border: '2px solid #9CA3AF',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }} />
              検索中...
            </>
          ) : (
            <>🏪 周辺施設を追加</>
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
      </GeoManagementModal>

      {/* 施設選択モーダル（管理モーダルの上にスタック） */}
      <SelectableListModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="周辺施設を選択"
        categories={categories}
        selectedItems={selectedItems}
        onAdd={handleAdd}
        onRemove={handleRemove}
        searchable={true}
        maxItems={20}
      />

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

// =============================================================================
// GeoPanel: Geo情報管理モーダル
// =============================================================================

interface GeoPanelProps {
  isOpen: boolean;
  onClose: () => void;
  schoolDistrictColumns?: ColumnWithLabel[];
}

export const GeoPanel: React.FC<GeoPanelProps> = ({ isOpen, onClose, schoolDistrictColumns }) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }} onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{
        backgroundColor: '#fff',
        borderRadius: '12px',
        width: '95%',
        maxWidth: '800px',
        maxHeight: '90vh',
        overflow: 'auto',
        padding: '24px',
      }}>
        {/* ヘッダー */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          paddingBottom: '16px',
          borderBottom: '1px solid #E5E7EB',
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1F2937', margin: 0 }}>
            周辺情報を管理
          </h2>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none', border: 'none', fontSize: '28px',
              cursor: 'pointer', color: '#9CA3AF', lineHeight: 1,
            }}
          >×</button>
        </div>

        {/* 学区セクション */}
        <div style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
            🏫 学区
          </h3>
          <SchoolDistrictAutoFetchButton />
          {schoolDistrictColumns && schoolDistrictColumns.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <FieldGroup
                groupName="学区"
                columns={schoolDistrictColumns}
                disabled={false}
              />
            </div>
          )}
        </div>

        {/* 電車・鉄道セクション */}
        <div style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
            🚃 電車・鉄道
          </h3>
          <StationAutoFetchButton />
        </div>

        {/* バスセクション */}
        <div style={{ marginBottom: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
            🚌 バス
          </h3>
          <BusStopAutoFetchButton />
        </div>

        {/* 周辺施設セクション */}
        <div style={{ marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
            🏪 周辺施設
          </h3>
          <FacilityAutoFetchButton />
        </div>

        {/* 閉じるボタン */}
        <div style={{ textAlign: 'center', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #E5E7EB' }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '10px 32px',
              backgroundColor: '#3B82F6',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 500,
              fontSize: '14px',
            }}
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
};
