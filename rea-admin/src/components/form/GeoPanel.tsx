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
import {
  SchoolCandidate, StationCandidate, BusStopCandidate, FacilityItem, FetchResults,
  SchoolResultSection, StationSelectList, BusStopSelectList, FacilitySelectList,
} from './GeoResultComponents';

// Leafletアイコン修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: LEAFLET_ICON_URLS.MARKER_RETINA,
  iconUrl: LEAFLET_ICON_URLS.MARKER,
  shadowUrl: LEAFLET_ICON_URLS.SHADOW,
});

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
