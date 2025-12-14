import React, { useState } from 'react';
import { FormProvider, useFormContext } from 'react-hook-form';
import { FieldGroup } from './FieldFactory';
import { useMetadataForm } from '../../hooks/useMetadataForm';
import { useAutoSave } from '../../hooks/useAutoSave';
import { ColumnWithLabel } from '../../services/metadataService';
import { SelectableListModal, SelectableItem, Category } from '../common/SelectableListModal';

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

// 駅自動取得・選択コンポーネント（モーダル版）
const StationAutoFetchButton: React.FC = () => {
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
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geo/nearest-stations?lat=${lat}&lng=${lng}&radius=5000&limit=15`
      );

      if (!response.ok) {
        throw new Error('駅情報の取得に失敗しました');
      }

      const data = await response.json();
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
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || '駅情報の取得に失敗しました' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const currentStations = getValues('transportation') || [];
    const rawData = (item as any)._raw;

    const newStation = {
      station_name: rawData?.station_name || item.name.replace('駅', ''),
      line_name: rawData?.line_name || '',
      walk_minutes: rawData?.walk_minutes,
    };

    setValue('transportation', [...currentStations, newStation], { shouldDirty: true });
  };

  const handleRemove = (item: SelectableItem) => {
    const currentStations = getValues('transportation') || [];
    const updated = currentStations.filter((s: any) =>
      `${s.station_name}_${s.line_name}` !== item.id
    );
    setValue('transportation', updated, { shouldDirty: true });
  };

  const currentStations = getValues('transportation') || [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentStations.map((s: any) => ({
    id: `${s.station_name}_${s.line_name}`,
    name: `${s.station_name}駅`,
    subText: `${s.line_name ? s.line_name + ' ・ ' : ''}徒歩${s.walk_minutes}分`,
  }));

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* 選択済み駅リスト（常に表示） */}
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

      {/* 駅選択モーダル */}
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
    </div>
  );
};

// バス停自動取得・選択コンポーネント（モーダル版）
const BusStopAutoFetchButton: React.FC = () => {
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
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geo/nearest-bus-stops?lat=${lat}&lng=${lng}&limit=15`
      );

      if (!response.ok) {
        throw new Error('バス停情報の取得に失敗しました');
      }

      const data = await response.json();
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
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'バス停情報の取得に失敗しました' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const currentBusStops = getValues('bus_stops') || [];
    const rawData = (item as any)._raw;

    const newBusStop = {
      name: rawData?.name || item.name,
      walk_minutes: rawData?.walk_minutes,
      routes: rawData?.routes || [],
    };

    setValue('bus_stops', [...currentBusStops, newBusStop], { shouldDirty: true });
  };

  const handleRemove = (item: SelectableItem) => {
    const currentBusStops = getValues('bus_stops') || [];
    const updated = currentBusStops.filter((bs: any) => bs.name !== item.id);
    setValue('bus_stops', updated, { shouldDirty: true });
  };

  const currentBusStops = getValues('bus_stops') || [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentBusStops.map((bs: any) => ({
    id: bs.name,
    name: bs.name,
    subText: `徒歩${bs.walk_minutes}分`,
  }));

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* 選択済みバス停リスト（常に表示） */}
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

      {/* バス停選択モーダル */}
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
    </div>
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
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geo/nearest-facilities-by-category?lat=${lat}&lng=${lng}&limit_per_category=5`
      );

      if (!response.ok) {
        throw new Error('施設情報の取得に失敗しました');
      }

      const data = await response.json();

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
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || '施設情報の取得に失敗しました' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (item: SelectableItem) => {
    const currentFacilities = getValues('nearby_facilities') || [];
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
    const currentFacilities = getValues('nearby_facilities') || [];
    const updated = currentFacilities.filter((f: any) => f.id !== item.id);
    setValue('nearby_facilities', updated, { shouldDirty: true });
  };

  const currentFacilities = getValues('nearby_facilities') || [];

  // 選択済みアイテムをSelectableItem形式に変換
  const selectedItems: SelectableItem[] = currentFacilities.map((f: any) => ({
    id: f.id,
    name: f.name,
    subText: `徒歩${f.walk_minutes}分`,
    category: f.category,
  }));

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* 選択済み施設リスト（常に表示） */}
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

      {/* 施設選択モーダル */}
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
  // visible_forがnull/undefinedなら全種別表示
  if (visibleFor === null || visibleFor === undefined) return true;
  // visible_forが空配列なら全種別で非表示
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

    // 所在地・周辺情報タブに含めるグループ名
    const locationGroups = ['所在地', '学区', '電車・鉄道', 'バス', '周辺施設'];

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

    // propertiesから所在地・周辺情報を分離してタブを構築
    const tabGroups: Array<{
      tableName: string;
      tableLabel: string;
      tableIcon: string;
      groups: Record<string, ColumnWithLabel[]>;
    }> = [];

    // 所在地・周辺情報タブ用のデータを先に準備
    const locationColumns = propertiesColumns.filter(col =>
      locationGroups.includes(col.group_name || '') &&
      isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name)
    );
    const locationTabData = locationColumns.length > 0 ? {
      tableName: 'properties_location',
      tableLabel: '所在地・周辺情報',
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

    // タブを追加（propertiesは所在地・周辺情報を除外）
    orderedTables.forEach(table => {
      const tableColumns = allColumns?.[table.table_name] || [];

      // 物件種別フィルタリング（全テーブルに適用）
      const filteredColumns = tableColumns.filter(col => {
        // propertiesの場合は所在地・周辺情報グループを除外
        if (table.table_name === 'properties' && locationGroups.includes(col.group_name || '')) {
          return false;
        }
        // ステータスグループはヘッダーで表示するので除外
        if (col.group_name === 'ステータス') {
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
        // 所在地・周辺情報タブを先に追加（ユーザー要望：所在地を最初に）
        if (locationTabData) {
          tabGroups.push(locationTabData);
        }
        // 基本・取引情報タブを追加（フィールドがある場合）
        if (Object.keys(grouped).length > 0) {
          tabGroups.push({
            tableName: 'properties',
            tableLabel: '基本・取引情報',
            tableIcon: '🏠',
            groups: grouped
          });
        }
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

    // ステータス表示用
    // 販売状況の色マップ
    const salesStatusConfig: Record<string, { label: string; color: string; bg: string }> = {
      '準備中': { label: '準備中', color: '#6B7280', bg: '#F3F4F6' },
      '販売中': { label: '販売中', color: '#059669', bg: '#D1FAE5' },
      '商談中': { label: '商談中', color: '#D97706', bg: '#FEF3C7' },
      '成約済み': { label: '成約済み', color: '#DC2626', bg: '#FEE2E2' },
      '販売終了': { label: '販売終了', color: '#374151', bg: '#E5E7EB' },
    };

    // 公開状態の色マップ
    const publicationStatusConfig: Record<string, { label: string; color: string; bg: string }> = {
      '非公開': { label: '非公開', color: '#6B7280', bg: '#F3F4F6' },
      '会員公開': { label: '会員公開', color: '#3B82F6', bg: '#DBEAFE' },
      '公開': { label: '公開', color: '#059669', bg: '#D1FAE5' },
    };

    const currentSalesStatus = formData.sales_status || '準備中';
    const currentPublicationStatus = formData.publication_status || '非公開';

    // 販売状況に応じて公開状態の選択肢を制限
    const isPublicationEditable = ['販売中', '商談中'].includes(currentSalesStatus);

    // ステータス変更ハンドラー
    const handleSalesStatusChange = (newStatus: string) => {
      form.setValue('sales_status', newStatus, { shouldDirty: true });

      // 連動ロジック: 準備中/成約済み/販売終了は強制的に非公開
      if (['準備中', '成約済み', '販売終了'].includes(newStatus)) {
        form.setValue('publication_status', '非公開', { shouldDirty: true });
      }
      // 販売中に変更した場合、デフォルトで公開に
      if (newStatus === '販売中' && currentPublicationStatus === '非公開') {
        form.setValue('publication_status', '公開', { shouldDirty: true });
      }
    };

    const handlePublicationStatusChange = (newStatus: string) => {
      form.setValue('publication_status', newStatus, { shouldDirty: true });
    };

    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
        <FormProvider {...form}>
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

              {/* ステータスバー - 販売状況・公開状態 */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px',
                padding: '12px 16px',
                backgroundColor: '#fff',
                borderRadius: '10px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
              }}>
                {/* 左：販売状況 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '12px', color: '#6B7280', fontWeight: 500 }}>販売:</span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {Object.entries(salesStatusConfig).map(([status, config]) => (
                      <button
                        key={status}
                        type="button"
                        onClick={() => handleSalesStatusChange(status)}
                        style={{
                          padding: '6px 12px',
                          borderRadius: '6px',
                          border: currentSalesStatus === status ? `2px solid ${config.color}` : '1px solid #E5E7EB',
                          backgroundColor: currentSalesStatus === status ? config.bg : '#fff',
                          color: currentSalesStatus === status ? config.color : '#6B7280',
                          fontSize: '12px',
                          fontWeight: currentSalesStatus === status ? 600 : 400,
                          cursor: 'pointer',
                          transition: 'all 150ms',
                        }}
                      >
                        {config.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 右：公開状態 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '12px', color: '#6B7280', fontWeight: 500 }}>公開:</span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {Object.entries(publicationStatusConfig).map(([status, config]) => {
                      const isDisabled = !isPublicationEditable && status !== '非公開';
                      return (
                        <button
                          key={status}
                          type="button"
                          onClick={() => !isDisabled && handlePublicationStatusChange(status)}
                          disabled={isDisabled}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '6px',
                            border: currentPublicationStatus === status ? `2px solid ${config.color}` : '1px solid #E5E7EB',
                            backgroundColor: currentPublicationStatus === status ? config.bg : (isDisabled ? '#F9FAFB' : '#fff'),
                            color: currentPublicationStatus === status ? config.color : (isDisabled ? '#D1D5DB' : '#6B7280'),
                            fontSize: '12px',
                            fontWeight: currentPublicationStatus === status ? 600 : 400,
                            cursor: isDisabled ? 'not-allowed' : 'pointer',
                            transition: 'all 150ms',
                            opacity: isDisabled ? 0.5 : 1,
                          }}
                        >
                          {config.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

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
              padding: '24px',
              marginTop: '16px',
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
                        {/* 電車・鉄道グループの場合、駅自動取得ボタンのみ表示（FieldGroup不要） */}
                        {groupName === '電車・鉄道' ? (
                          <div>
                            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
                              電車・鉄道
                            </h3>
                            <StationAutoFetchButton />
                          </div>
                        ) : groupName === 'バス' ? (
                          /* バスグループの場合、バス停自動取得ボタンのみ表示（FieldGroup不要） */
                          <div>
                            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
                              バス
                            </h3>
                            <BusStopAutoFetchButton />
                          </div>
                        ) : groupName === '周辺施設' ? (
                          /* 周辺施設グループの場合、施設自動取得ボタンのみ表示 */
                          <div>
                            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>
                              周辺施設
                            </h3>
                            <FacilityAutoFetchButton />
                          </div>
                        ) : (
                          <FieldGroup
                            groupName={groupName}
                            columns={groupColumns}
                            disabled={false}
                          />
                        )}
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

              {/* 中央: 保存ステータス */}
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
