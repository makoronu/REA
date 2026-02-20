/**
 * GeoPanel: 周辺情報一括取得ウィザード
 *
 * 地図でピン指定 → 学区・駅・バス・施設を一括取得 → 結果確認 → フォームに反映
 * useFormContext経由でDynamicFormのフォームと連携
 */
import React, { useState, useEffect, useRef } from 'react';
import { useFormContext } from 'react-hook-form';
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { ColumnWithLabel } from '../../services/metadataService';
import { FieldGroup } from './FieldFactory';
import { API_PATHS } from '../../constants/apiPaths';
import { api } from '../../services/api';
import { GEO_SEARCH_CONFIG, MAP_TILES, LEAFLET_ICON_URLS } from '../../constants';

// Leafletアイコン修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: LEAFLET_ICON_URLS.MARKER_RETINA,
  iconUrl: LEAFLET_ICON_URLS.MARKER,
  shadowUrl: LEAFLET_ICON_URLS.SHADOW,
});

// =============================================================================
// 型定義
// =============================================================================

interface SchoolCandidate {
  school_name: string;
  address: string | null;
  admin_type: string | null;
  distance_meters: number;
  walk_minutes: number;
  is_in_district: boolean;
}

interface StationCandidate {
  station_id: number;
  station_name: string;
  line_name: string | null;
  company_name: string | null;
  distance_meters: number;
  walk_minutes: number;
}

interface BusStopCandidate {
  name: string;
  bus_type: string | null;
  operators: string[];
  routes: string[];
  distance_meters: number;
  walk_minutes: number;
}

interface FacilityItem {
  id: string;
  name: string;
  category: string;
  category_name: string;
  address: string;
  distance_meters: number;
  walk_minutes: number;
}

/** 一括取得の結果 */
interface FetchResults {
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
// 地図コンポーネント
// =============================================================================

/** 地図の中心・ズーム変更 */
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

/** ドラッグ可能マーカー */
const DraggableMarker: React.FC<{
  position: [number, number];
  onPositionChange: (lat: number, lng: number) => void;
}> = ({ position, onPositionChange }) => {
  const markerRef = useRef<L.Marker>(null);

  return (
    <Marker
      draggable={true}
      eventHandlers={{
        dragend() {
          const marker = markerRef.current;
          if (marker) {
            const latlng = marker.getLatLng();
            onPositionChange(latlng.lat, latlng.lng);
          }
        },
      }}
      position={position}
      ref={markerRef}
    />
  );
};

/** 地図クリックで座標変更 */
const MapClickHandler: React.FC<{
  onPositionChange: (lat: number, lng: number) => void;
}> = ({ onPositionChange }) => {
  useMapEvents({
    click(e) {
      onPositionChange(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

// =============================================================================
// 結果サマリーコンポーネント
// =============================================================================

/** 学区結果表示 */
const SchoolResultSection: React.FC<{
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

/** 駅選択リスト */
const StationSelectList: React.FC<{
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

/** バス停選択リスト */
const BusStopSelectList: React.FC<{
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

/** 施設選択リスト（カテゴリ別） */
const FacilitySelectList: React.FC<{
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

// =============================================================================
// GeoPanel メインコンポーネント
// =============================================================================

interface GeoPanelProps {
  isOpen: boolean;
  onClose: () => void;
  schoolDistrictColumns?: ColumnWithLabel[];
}

export const GeoPanel: React.FC<GeoPanelProps> = ({ isOpen, onClose, schoolDistrictColumns }) => {
  const { getValues, setValue } = useFormContext();

  // ピン座標（地図操作用のローカル状態）
  const formLat = getValues('latitude');
  const formLng = getValues('longitude');
  const hasFormCoords = formLat && formLng && !isNaN(Number(formLat)) && !isNaN(Number(formLng));

  const [pinLat, setPinLat] = useState<number>(hasFormCoords ? Number(formLat) : 35.6812);
  const [pinLng, setPinLng] = useState<number>(hasFormCoords ? Number(formLng) : 139.7671);
  const [hasPin, setHasPin] = useState(hasFormCoords);

  // 取得状態
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState<FetchResults | null>(null);

  // 学区選択状態
  const [selectedElementary, setSelectedElementary] = useState<string | null>(
    getValues('elementary_school') || null
  );
  const [selectedJuniorHigh, setSelectedJuniorHigh] = useState<string | null>(
    getValues('junior_high_school') || null
  );
  const [selectedElementaryMinutes, setSelectedElementaryMinutes] = useState<number | null>(
    getValues('elementary_school_minutes') || null
  );
  const [selectedJuniorHighMinutes, setSelectedJuniorHighMinutes] = useState<number | null>(
    getValues('junior_high_school_minutes') || null
  );

  // 駅・バス停・施設の選択状態（インデックスのSet）
  const [selectedStationIndices, setSelectedStationIndices] = useState<Set<number>>(new Set());
  const [selectedBusStopIndices, setSelectedBusStopIndices] = useState<Set<number>>(new Set());
  const [selectedFacilityIndices, setSelectedFacilityIndices] = useState<Set<number>>(new Set());

  // モーダルが開いた時にフォームから座標を同期
  useEffect(() => {
    if (isOpen) {
      const lat = getValues('latitude');
      const lng = getValues('longitude');
      if (lat && lng && !isNaN(Number(lat)) && !isNaN(Number(lng))) {
        setPinLat(Number(lat));
        setPinLng(Number(lng));
        setHasPin(true);
      }
      setSelectedElementary(getValues('elementary_school') || null);
      setSelectedJuniorHigh(getValues('junior_high_school') || null);
      setSelectedElementaryMinutes(getValues('elementary_school_minutes') || null);
      setSelectedJuniorHighMinutes(getValues('junior_high_school_minutes') || null);
      setResults(null);
    }
  }, [isOpen, getValues]);

  if (!isOpen) return null;

  // 地図上でピン移動
  const handlePositionChange = (lat: number, lng: number) => {
    setPinLat(Math.round(lat * 1000000) / 1000000);
    setPinLng(Math.round(lng * 1000000) / 1000000);
    setHasPin(true);
    // ピンを動かしたら前回の結果をクリア
    setResults(null);
  };

  // 一括取得
  const handleBulkFetch = async () => {
    if (!hasPin) return;

    setIsFetching(true);
    const errors: string[] = [];

    const [schoolRes, stationRes, busRes, facilityRes] = await Promise.allSettled([
      api.get(API_PATHS.GEO.SCHOOL_DISTRICTS, { params: { lat: pinLat, lng: pinLng } }),
      api.get(API_PATHS.GEO.NEAREST_STATIONS, {
        params: { lat: pinLat, lng: pinLng, radius: GEO_SEARCH_CONFIG.STATION.RADIUS_M, limit: GEO_SEARCH_CONFIG.STATION.LIMIT }
      }),
      api.get(API_PATHS.GEO.NEAREST_BUS_STOPS, {
        params: { lat: pinLat, lng: pinLng, limit: GEO_SEARCH_CONFIG.BUS_STOP.LIMIT }
      }),
      api.get(API_PATHS.GEO.NEAREST_FACILITIES, {
        params: { lat: pinLat, lng: pinLng, limit_per_category: GEO_SEARCH_CONFIG.FACILITY.LIMIT_PER_CATEGORY }
      }),
    ]);

    // 学区
    let schools: FetchResults['schools'] = null;
    if (schoolRes.status === 'fulfilled') {
      const d = schoolRes.value.data;
      schools = { elementary: d.elementary || [], juniorHigh: d.junior_high || [] };
      // 学区内の学校を自動選択
      const inDistrictElem = (d.elementary || []).find((s: SchoolCandidate) => s.is_in_district);
      const inDistrictJH = (d.junior_high || []).find((s: SchoolCandidate) => s.is_in_district);
      if (inDistrictElem) {
        setSelectedElementary(inDistrictElem.school_name);
        setSelectedElementaryMinutes(inDistrictElem.walk_minutes);
      }
      if (inDistrictJH) {
        setSelectedJuniorHigh(inDistrictJH.school_name);
        setSelectedJuniorHighMinutes(inDistrictJH.walk_minutes);
      }
    } else {
      errors.push('学区');
    }

    // 駅
    let stations: StationCandidate[] = [];
    if (stationRes.status === 'fulfilled') {
      stations = stationRes.value.data.stations || [];
    } else {
      errors.push('駅');
    }

    // バス
    let busStops: BusStopCandidate[] = [];
    if (busRes.status === 'fulfilled') {
      busStops = busRes.value.data.bus_stops || [];
    } else {
      errors.push('バス停');
    }

    // 施設
    const facilities: FacilityItem[] = [];
    if (facilityRes.status === 'fulfilled') {
      const catData = facilityRes.value.data.categories || {};
      Object.entries(catData).forEach(([catCode, catVal]: [string, any]) => {
        (catVal.facilities || []).forEach((f: any) => {
          facilities.push({
            id: f.id,
            name: f.name,
            category: catCode,
            category_name: catVal.category_name,
            address: f.address,
            distance_meters: f.distance_meters,
            walk_minutes: f.walk_minutes,
          });
        });
      });
    } else {
      errors.push('施設');
    }

    setResults({ schools, stations, busStops, facilities, errors });

    // 駅: デフォルト上位N件を選択
    const stationLimit = GEO_SEARCH_CONFIG.PROPERTY_STATIONS.LIMIT;
    setSelectedStationIndices(new Set(stations.slice(0, stationLimit).map((_, i) => i)));

    // バス停: デフォルト上位N件を選択
    const busLimit = GEO_SEARCH_CONFIG.PROPERTY_BUS_STOPS.LIMIT;
    setSelectedBusStopIndices(new Set(busStops.slice(0, busLimit).map((_, i) => i)));

    // 施設: デフォルト各カテゴリ最寄り1件を選択
    const facilityDefaults = new Set<number>();
    const seenCategories = new Set<string>();
    facilities.forEach((f, i) => {
      if (!seenCategories.has(f.category)) {
        seenCategories.add(f.category);
        facilityDefaults.add(i);
      }
    });
    setSelectedFacilityIndices(facilityDefaults);

    setIsFetching(false);
  };

  // フォームに反映して閉じる
  const handleApply = () => {
    if (!results) return;

    // 座標をフォームに反映
    setValue('latitude', pinLat, { shouldDirty: true });
    setValue('longitude', pinLng, { shouldDirty: true });

    // 学区
    if (selectedElementary) {
      setValue('elementary_school', selectedElementary, { shouldDirty: true });
      if (selectedElementaryMinutes !== null) {
        setValue('elementary_school_minutes', selectedElementaryMinutes, { shouldDirty: true });
      }
    }
    if (selectedJuniorHigh) {
      setValue('junior_high_school', selectedJuniorHigh, { shouldDirty: true });
      if (selectedJuniorHighMinutes !== null) {
        setValue('junior_high_school_minutes', selectedJuniorHighMinutes, { shouldDirty: true });
      }
    }

    // 駅（選択した駅のみ反映）
    const selectedStations = results.stations.filter((_, i) => selectedStationIndices.has(i));
    const transportationData = selectedStations.map(s => ({
      station_name: s.station_name,
      line_name: s.line_name || '',
      walk_minutes: s.walk_minutes,
    }));
    setValue('transportation', transportationData, { shouldDirty: true });

    // バス停（選択したバス停のみ反映）
    const selectedBusStops = results.busStops.filter((_, i) => selectedBusStopIndices.has(i));
    const busData = selectedBusStops.map(bs => ({
      bus_stop_name: bs.name,
      line_name: (bs.routes || []).join('・'),
      walk_minutes: bs.walk_minutes,
    }));
    setValue('bus_stops', busData, { shouldDirty: true });

    // 施設（選択した施設のみ反映）
    const selectedFacilities = results.facilities.filter((_, i) => selectedFacilityIndices.has(i));
    const facilityData = selectedFacilities.map(f => ({
      facility_name: f.name,
      category: f.category,
      distance_meters: f.distance_meters || Math.round((f.walk_minutes || 0) * 80),
      walk_minutes: f.walk_minutes,
    }));
    setValue('nearby_facilities', facilityData, { shouldDirty: true });

    onClose();
  };

  // 学区選択ハンドラ
  const handleSelectElementary = (school: SchoolCandidate) => {
    setSelectedElementary(school.school_name);
    setSelectedElementaryMinutes(school.walk_minutes);
  };
  const handleSelectJuniorHigh = (school: SchoolCandidate) => {
    setSelectedJuniorHigh(school.school_name);
    setSelectedJuniorHighMinutes(school.walk_minutes);
  };

  const mapCenter: [number, number] = [pinLat, pinLng];
  const mapZoom = hasPin ? 15 : 10;

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
          marginBottom: '16px',
          paddingBottom: '12px',
          borderBottom: '1px solid #E5E7EB',
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', margin: 0 }}>
            🗺️ 周辺情報を自動取得
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

        {/* ステップ1: 地図 */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
            地図をクリックまたはマーカーをドラッグして位置を指定してください
          </div>
          <div style={{
            height: '300px', borderRadius: '8px', overflow: 'hidden',
            border: '1px solid #E5E7EB', position: 'relative', zIndex: 0,
          }}>
            <MapContainer
              center={mapCenter}
              zoom={mapZoom}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution={MAP_TILES.OSM.ATTRIBUTION}
                url={MAP_TILES.OSM.URL}
              />
              <MapController center={mapCenter} zoom={mapZoom} />
              <MapClickHandler onPositionChange={handlePositionChange} />
              {hasPin && (
                <DraggableMarker
                  position={[pinLat, pinLng]}
                  onPositionChange={handlePositionChange}
                />
              )}
            </MapContainer>
          </div>
          <div style={{
            display: 'flex', gap: '16px', alignItems: 'center',
            marginTop: '8px', fontSize: '13px', color: '#374151',
          }}>
            <span>緯度: <strong>{pinLat.toFixed(6)}</strong></span>
            <span>経度: <strong>{pinLng.toFixed(6)}</strong></span>
            {!hasFormCoords && !hasPin && (
              <span style={{ color: '#EF4444', fontSize: '12px' }}>
                ※ 座標未設定。地図をクリックしてください
              </span>
            )}
          </div>
        </div>

        {/* 一括取得ボタン */}
        <div style={{ marginBottom: '16px' }}>
          <button
            type="button"
            onClick={() => { void handleBulkFetch(); }}
            disabled={!hasPin || isFetching}
            style={{
              width: '100%',
              padding: '14px 20px',
              fontSize: '15px',
              fontWeight: 600,
              backgroundColor: !hasPin || isFetching ? '#D1D5DB' : '#3B82F6',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: !hasPin || isFetching ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {isFetching ? (
              <>
                <span style={{
                  display: 'inline-block', width: '18px', height: '18px',
                  border: '2px solid #fff', borderTopColor: 'transparent',
                  borderRadius: '50%', animation: 'spin 1s linear infinite',
                }} />
                取得中...
              </>
            ) : (
              <>📍 この位置で周辺情報を一括取得</>
            )}
          </button>
        </div>

        {/* エラー表示 */}
        {results && results.errors.length > 0 && (
          <div style={{
            padding: '10px 14px', marginBottom: '12px', borderRadius: '8px',
            backgroundColor: '#FEF3C7', fontSize: '13px', color: '#92400E',
          }}>
            ⚠️ {results.errors.join('・')}の取得に失敗しました（他の項目は正常に取得済み）
          </div>
        )}

        {/* 取得結果 */}
        {results && (
          <div style={{
            border: '1px solid #E5E7EB', borderRadius: '8px',
            overflow: 'hidden', marginBottom: '16px',
          }}>
            {/* 学区 */}
            {results.schools && (
              <div style={{ padding: '14px 16px', borderBottom: '1px solid #E5E7EB' }}>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '8px' }}>
                  🏫 学区
                </div>
                <SchoolResultSection
                  elementary={results.schools.elementary}
                  juniorHigh={results.schools.juniorHigh}
                  selectedElementary={selectedElementary}
                  selectedJuniorHigh={selectedJuniorHigh}
                  onSelectElementary={handleSelectElementary}
                  onSelectJuniorHigh={handleSelectJuniorHigh}
                />
              </div>
            )}

            {/* 駅 */}
            <div style={{ padding: '14px 16px', borderBottom: '1px solid #E5E7EB' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '6px',
              }}>
                <span>🚃 最寄駅（{results.stations.length}件）</span>
                <span style={{ fontSize: '11px', fontWeight: 400, color: '#6B7280' }}>
                  {selectedStationIndices.size}件選択中
                </span>
              </div>
              <StationSelectList
                stations={results.stations}
                selectedIndices={selectedStationIndices}
                onToggle={(i) => {
                  setSelectedStationIndices(prev => {
                    const next = new Set(prev);
                    next.has(i) ? next.delete(i) : next.add(i);
                    return next;
                  });
                }}
              />
            </div>

            {/* バス停 */}
            <div style={{ padding: '14px 16px', borderBottom: '1px solid #E5E7EB' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '6px',
              }}>
                <span>🚌 バス停（{results.busStops.length}件）</span>
                <span style={{ fontSize: '11px', fontWeight: 400, color: '#6B7280' }}>
                  {selectedBusStopIndices.size}件選択中
                </span>
              </div>
              <BusStopSelectList
                busStops={results.busStops}
                selectedIndices={selectedBusStopIndices}
                onToggle={(i) => {
                  setSelectedBusStopIndices(prev => {
                    const next = new Set(prev);
                    next.has(i) ? next.delete(i) : next.add(i);
                    return next;
                  });
                }}
              />
            </div>

            {/* 施設 */}
            <div style={{ padding: '14px 16px' }}>
              <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '6px',
              }}>
                <span>🏪 周辺施設（{results.facilities.length}件）</span>
                <span style={{ fontSize: '11px', fontWeight: 400, color: '#6B7280' }}>
                  {selectedFacilityIndices.size}件選択中
                </span>
              </div>
              <FacilitySelectList
                facilities={results.facilities}
                selectedIndices={selectedFacilityIndices}
                onToggle={(i) => {
                  setSelectedFacilityIndices(prev => {
                    const next = new Set(prev);
                    next.has(i) ? next.delete(i) : next.add(i);
                    return next;
                  });
                }}
              />
            </div>
          </div>
        )}

        {/* 学区フィールド（FieldGroup経由で表示） */}
        {results && results.schools && schoolDistrictColumns && schoolDistrictColumns.length > 0 && (
          <div style={{
            padding: '14px 16px', marginBottom: '16px',
            backgroundColor: '#F9FAFB', borderRadius: '8px',
            border: '1px solid #E5E7EB',
          }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '8px' }}>
              学区フィールド（手動修正可）
            </div>
            <FieldGroup
              groupName="学区"
              columns={schoolDistrictColumns}
              disabled={false}
            />
          </div>
        )}

        {/* フッター */}
        <div style={{
          display: 'flex', gap: '12px', justifyContent: 'flex-end',
          paddingTop: '16px', borderTop: '1px solid #E5E7EB',
        }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '10px 24px', backgroundColor: '#fff',
              border: '1px solid #D1D5DB', borderRadius: '8px',
              cursor: 'pointer', fontSize: '14px', color: '#374151',
            }}
          >
            キャンセル
          </button>
          <button
            type="button"
            onClick={handleApply}
            disabled={!results}
            style={{
              padding: '10px 24px',
              backgroundColor: results ? '#3B82F6' : '#D1D5DB',
              color: '#fff', border: 'none', borderRadius: '8px',
              cursor: results ? 'pointer' : 'not-allowed',
              fontSize: '14px', fontWeight: 600,
            }}
          >
            フォームに反映して閉じる
          </button>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
