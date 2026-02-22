/**
 * GeoPanel: 周辺情報一括取得ウィザード
 *
 * 地図でピン指定 → 学区・駅・バス・施設を一括取得 → 結果確認 → フォームに反映
 * useFormContext経由でDynamicFormのフォームと連携
 */
import React, { useState, useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MAP_TILES, LEAFLET_ICON_URLS } from '../../constants';
import {
  SchoolCandidate,
  MapController, DraggableMarker, MapClickHandler,
  SchoolResultSection, StationSelectList, BusStopSelectList, FacilitySelectList,
} from './GeoResultComponents';
import { useGeoFetch } from './useGeoFetch';

// Leafletアイコン修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: LEAFLET_ICON_URLS.MARKER_RETINA,
  iconUrl: LEAFLET_ICON_URLS.MARKER,
  shadowUrl: LEAFLET_ICON_URLS.SHADOW,
});

// =============================================================================
// GeoPanel メインコンポーネント
// =============================================================================

interface GeoPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GeoPanel: React.FC<GeoPanelProps> = ({ isOpen, onClose }) => {
  const { getValues, setValue } = useFormContext();

  // ピン座標（地図操作用のローカル状態）
  const formLat = getValues('latitude');
  const formLng = getValues('longitude');
  const hasFormCoords = formLat && formLng && !isNaN(Number(formLat)) && !isNaN(Number(formLng));

  const [pinLat, setPinLat] = useState<number>(hasFormCoords ? Number(formLat) : 35.6812);
  const [pinLng, setPinLng] = useState<number>(hasFormCoords ? Number(formLng) : 139.7671);
  const [hasPin, setHasPin] = useState(hasFormCoords);

  // 一括取得フック
  const {
    isFetching, results,
    selectedStationIndices, selectedBusStopIndices, selectedFacilityIndices,
    schoolSelection, setSchoolSelection,
    setSelectedStationIndices, setSelectedBusStopIndices, setSelectedFacilityIndices,
    handleBulkFetch, clearResults,
  } = useGeoFetch();

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
      setSchoolSelection({
        elementary: getValues('elementary_school') || null,
        elementaryMinutes: getValues('elementary_school_minutes') || null,
        juniorHigh: getValues('junior_high_school') || null,
        juniorHighMinutes: getValues('junior_high_school_minutes') || null,
      });
      clearResults();
    }
  }, [isOpen, getValues, setSchoolSelection, clearResults]);

  if (!isOpen) return null;

  // 地図上でピン移動
  const handlePositionChange = (lat: number, lng: number) => {
    setPinLat(Math.round(lat * 1000000) / 1000000);
    setPinLng(Math.round(lng * 1000000) / 1000000);
    setHasPin(true);
    clearResults();
  };

  // フォームに反映して閉じる
  const handleApply = () => {
    if (!results) return;

    // 座標をフォームに反映
    setValue('latitude', pinLat, { shouldDirty: true });
    setValue('longitude', pinLng, { shouldDirty: true });

    // 学区
    if (schoolSelection.elementary) {
      setValue('elementary_school', schoolSelection.elementary, { shouldDirty: true });
      if (schoolSelection.elementaryMinutes !== null) {
        setValue('elementary_school_minutes', schoolSelection.elementaryMinutes, { shouldDirty: true });
      }
    }
    if (schoolSelection.juniorHigh) {
      setValue('junior_high_school', schoolSelection.juniorHigh, { shouldDirty: true });
      if (schoolSelection.juniorHighMinutes !== null) {
        setValue('junior_high_school_minutes', schoolSelection.juniorHighMinutes, { shouldDirty: true });
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
    setSchoolSelection(prev => ({
      ...prev, elementary: school.school_name, elementaryMinutes: school.walk_minutes,
    }));
  };
  const handleSelectJuniorHigh = (school: SchoolCandidate) => {
    setSchoolSelection(prev => ({
      ...prev, juniorHigh: school.school_name, juniorHighMinutes: school.walk_minutes,
    }));
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
            🗺️ 地図確定＋周辺取得
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
            onClick={() => { void handleBulkFetch(pinLat, pinLng); }}
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
              <>📍 この位置で一括取得</>
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
                  selectedElementary={schoolSelection.elementary}
                  selectedJuniorHigh={schoolSelection.juniorHigh}
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
