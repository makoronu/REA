import React, { useState, useEffect, useRef } from 'react';
import { useFormContext } from 'react-hook-form';
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { geoService } from '../../services/geoService';

// Leafletのデフォルトアイコン問題を修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// 地図の中心を変更するコンポーネント
const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
};

// ドラッグ可能なマーカー
const DraggableMarker: React.FC<{
  position: [number, number];
  onPositionChange: (lat: number, lng: number) => void;
}> = ({ position, onPositionChange }) => {
  const markerRef = useRef<L.Marker>(null);

  const eventHandlers = {
    dragend() {
      const marker = markerRef.current;
      if (marker) {
        const latlng = marker.getLatLng();
        onPositionChange(latlng.lat, latlng.lng);
      }
    },
  };

  return (
    <Marker
      draggable={true}
      eventHandlers={eventHandlers}
      position={position}
      ref={markerRef}
    />
  );
};

// 地図クリックで位置を設定
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

interface LocationFieldProps {
  disabled?: boolean;
}

export const LocationField: React.FC<LocationFieldProps> = ({ disabled = false }) => {
  const { watch, setValue } = useFormContext();

  // フォームの値を監視
  const prefecture = watch('prefecture') || '';
  const city = watch('city') || '';
  const address = watch('address') || '';
  const addressDetail = watch('address_detail') || '';
  const formLatitude = watch('latitude');
  const formLongitude = watch('longitude');

  // ローカル状態（setValueの更新がwatchに即座に反映されない問題の回避）
  const [localLatitude, setLocalLatitude] = useState<number | null>(null);
  const [localLongitude, setLocalLongitude] = useState<number | null>(null);

  // フォームの値を優先、ローカルがあればローカルを使用
  const latitude = localLatitude !== null ? localLatitude : formLatitude;
  const longitude = localLongitude !== null ? localLongitude : formLongitude;

  const [isGeocoding, setIsGeocoding] = useState(false);
  const [geocodeStatus, setGeocodeStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [geocodeMessage, setGeocodeMessage] = useState('');
  const [showMap, setShowMap] = useState(false);

  // フォームの値が変わったらローカル状態をクリア
  useEffect(() => {
    if (formLatitude !== null && formLatitude !== undefined) {
      setLocalLatitude(null);
    }
    if (formLongitude !== null && formLongitude !== undefined) {
      setLocalLongitude(null);
    }
  }, [formLatitude, formLongitude]);

  // 有効な座標があるか
  const hasValidCoords = latitude && longitude && !isNaN(latitude) && !isNaN(longitude);

  // 地図の中心（デフォルトは東京駅）
  const mapCenter: [number, number] = hasValidCoords
    ? [latitude, longitude]
    : [35.6812, 139.7671];

  // 住所から座標を取得
  const handleGeocode = async () => {
    const fullAddress = [prefecture, city, address, addressDetail].filter(Boolean).join('');

    if (!fullAddress) {
      setGeocodeStatus('error');
      setGeocodeMessage('住所を入力してください');
      return;
    }

    setIsGeocoding(true);
    setGeocodeStatus('idle');

    try {
      const result = await geoService.geocode(fullAddress);

      // ローカル状態を更新（即座にUIに反映）
      setLocalLatitude(result.latitude);
      setLocalLongitude(result.longitude);

      // フォームの値も更新（保存時に使用）
      setValue('latitude', result.latitude, { shouldDirty: true });
      setValue('longitude', result.longitude, { shouldDirty: true });

      setGeocodeStatus('success');
      setGeocodeMessage('座標を取得しました');
      setShowMap(true);
    } catch (err) {
      setGeocodeStatus('error');
      setGeocodeMessage('座標の取得に失敗しました');
      console.error('Geocode error:', err);
    } finally {
      setIsGeocoding(false);
      setTimeout(() => setGeocodeStatus('idle'), 3000);
    }
  };

  // 地図上でマーカーを動かした時
  const handlePositionChange = (lat: number, lng: number) => {
    setValue('latitude', Math.round(lat * 1000000) / 1000000, { shouldDirty: true });
    setValue('longitude', Math.round(lng * 1000000) / 1000000, { shouldDirty: true });
  };

  return (
    <div style={{ marginTop: '16px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '12px' }}>
      {/* ヘッダー */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>
          位置情報（緯度・経度）
        </h4>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {hasValidCoords && (
            <span style={{ fontSize: '12px', color: '#10B981' }}>
              ✓ 設定済み
            </span>
          )}
          <button
            type="button"
            onClick={() => setShowMap(!showMap)}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              backgroundColor: 'transparent',
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              cursor: 'pointer',
              color: '#6B7280',
            }}
          >
            {showMap ? '地図を閉じる' : '地図を表示'}
          </button>
        </div>
      </div>

      {/* 座標表示と取得ボタン */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ fontSize: '13px', color: '#6B7280' }}>緯度:</label>
          <input
            type="number"
            value={latitude || ''}
            onChange={(e) => setValue('latitude', parseFloat(e.target.value) || null, { shouldDirty: true })}
            disabled={disabled}
            step="0.000001"
            style={{
              width: '140px',
              padding: '8px',
              fontSize: '13px',
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              backgroundColor: disabled ? '#F9FAFB' : '#fff',
            }}
            placeholder="35.681236"
          />
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ fontSize: '13px', color: '#6B7280' }}>経度:</label>
          <input
            type="number"
            value={longitude || ''}
            onChange={(e) => setValue('longitude', parseFloat(e.target.value) || null, { shouldDirty: true })}
            disabled={disabled}
            step="0.000001"
            style={{
              width: '140px',
              padding: '8px',
              fontSize: '13px',
              border: '1px solid #E5E7EB',
              borderRadius: '6px',
              backgroundColor: disabled ? '#F9FAFB' : '#fff',
            }}
            placeholder="139.767125"
          />
        </div>
        <button
          type="button"
          onClick={handleGeocode}
          disabled={disabled || isGeocoding || (!prefecture && !city && !address)}
          style={{
            padding: '8px 16px',
            fontSize: '13px',
            backgroundColor: isGeocoding ? '#9CA3AF' : '#3B82F6',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: disabled || isGeocoding ? 'not-allowed' : 'pointer',
            transition: 'background-color 150ms',
          }}
        >
          {isGeocoding ? '取得中...' : '住所から座標を取得'}
        </button>

        {/* ステータス表示 */}
        {geocodeStatus === 'success' && (
          <span style={{ fontSize: '12px', color: '#10B981' }}>✓ {geocodeMessage}</span>
        )}
        {geocodeStatus === 'error' && (
          <span style={{ fontSize: '12px', color: '#EF4444' }}>✗ {geocodeMessage}</span>
        )}
      </div>

      {/* 地図 */}
      {showMap && (
        <div style={{ marginTop: '16px' }}>
          <p style={{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }}>
            マーカーをドラッグするか、地図をクリックして位置を調整できます
          </p>
          <div style={{ height: '300px', borderRadius: '8px', overflow: 'hidden', border: '1px solid #E5E7EB', position: 'relative', zIndex: 0 }}>
            <MapContainer
              center={mapCenter}
              zoom={hasValidCoords ? 16 : 10}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapController center={mapCenter} zoom={hasValidCoords ? 16 : 10} />
              <MapClickHandler onPositionChange={handlePositionChange} />
              {hasValidCoords && (
                <DraggableMarker
                  position={[latitude, longitude]}
                  onPositionChange={handlePositionChange}
                />
              )}
            </MapContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationField;
