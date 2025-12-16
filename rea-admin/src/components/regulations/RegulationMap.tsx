/**
 * 法令制限・ハザードMAP表示コンポーネント
 *
 * 不動産情報ライブラリAPIからGeoJSONを取得してMAP上に表示
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { API_URL } from '../../config';

interface RegulationMapProps {
  lat: number;
  lng: number;
}

// レイヤー定義
const LAYER_DEFINITIONS = [
  { code: 'XKT002', name: '用途地域', color: '#3B82F6', checked: true },
  { code: 'XKT014', name: '防火地域', color: '#F97316', checked: false },
  { code: 'XKT026', name: '洪水浸水', color: '#06B6D4', checked: false },
  { code: 'XKT029', name: '土砂災害', color: '#EAB308', checked: false },
  { code: 'XKT028', name: '津波浸水', color: '#A855F7', checked: false },
  { code: 'XKT027', name: '高潮浸水', color: '#14B8A6', checked: false },
  { code: 'XKT003', name: '立地適正化', color: '#22C55E', checked: false },
  { code: 'XKT024', name: '地区計画', color: '#6366F1', checked: false },
  { code: 'XKT030', name: '都市計画道路', color: '#EF4444', checked: false },
];

export const RegulationMap: React.FC<RegulationMapProps> = ({ lat, lng }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layersRef = useRef<Record<string, L.GeoJSON>>({});
  const markerRef = useRef<L.Marker | null>(null);

  const [activeLayers, setActiveLayers] = useState<string[]>(['XKT002']);
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  // GeoJSONデータを取得
  const fetchLayerData = useCallback(async (layerCode: string) => {
    if (!mapInstanceRef.current) return;

    setLoading(prev => ({ ...prev, [layerCode]: true }));
    setErrors(prev => ({ ...prev, [layerCode]: '' }));

    try {
      const response = await fetch(
        `${API_URL}/api/v1/reinfolib/tile/${layerCode}?lat=${lat}&lng=${lng}`
      );

      if (!response.ok) {
        throw new Error('データ取得失敗');
      }

      const geojson = await response.json();

      // 既存レイヤーを削除
      if (layersRef.current[layerCode]) {
        mapInstanceRef.current.removeLayer(layersRef.current[layerCode]);
        delete layersRef.current[layerCode];
      }

      // GeoJSONがあればレイヤーを追加
      if (geojson.features && geojson.features.length > 0) {
        const layerDef = LAYER_DEFINITIONS.find(l => l.code === layerCode);
        const color = layerDef?.color || '#666';

        const layer = L.geoJSON(geojson, {
          style: () => ({
            fillColor: color,
            fillOpacity: 0.4,
            color: color,
            weight: 2,
          }),
          onEachFeature: (feature, layer) => {
            // ポップアップ表示
            const props = feature.properties;
            let content = `<strong>${layerDef?.name || layerCode}</strong><br/>`;

            // プロパティを表示
            Object.entries(props).forEach(([key, value]) => {
              if (value && key !== 'fid') {
                content += `${key}: ${value}<br/>`;
              }
            });

            layer.bindPopup(content);

            // ホバー効果
            layer.on('mouseover', (e) => {
              (e.target as L.Path).setStyle({ fillOpacity: 0.7, weight: 3 });
            });
            layer.on('mouseout', (e) => {
              (e.target as L.Path).setStyle({ fillOpacity: 0.4, weight: 2 });
            });
          },
        });

        layer.addTo(mapInstanceRef.current);
        layersRef.current[layerCode] = layer;
      }
    } catch (err) {
      console.error(`${layerCode} 取得エラー:`, err);
      setErrors(prev => ({ ...prev, [layerCode]: 'データなし' }));
    } finally {
      setLoading(prev => ({ ...prev, [layerCode]: false }));
    }
  }, [lat, lng]);

  // レイヤー削除
  const removeLayer = useCallback((layerCode: string) => {
    if (mapInstanceRef.current && layersRef.current[layerCode]) {
      mapInstanceRef.current.removeLayer(layersRef.current[layerCode]);
      delete layersRef.current[layerCode];
    }
  }, []);

  // レイヤー切り替え
  const toggleLayer = useCallback((layerCode: string) => {
    setActiveLayers(prev => {
      if (prev.includes(layerCode)) {
        removeLayer(layerCode);
        return prev.filter(c => c !== layerCode);
      } else {
        fetchLayerData(layerCode);
        return [...prev, layerCode];
      }
    });
  }, [fetchLayerData, removeLayer]);

  // マップ初期化
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      scrollWheelZoom: true,
    }).setView([lat, lng], 16);

    L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
      attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>',
      maxZoom: 18,
    }).addTo(map);

    // 物件マーカー
    markerRef.current = L.marker([lat, lng], {
      icon: L.divIcon({
        className: 'property-marker',
        html: '<div style="width:24px;height:24px;background:#DC2626;border:3px solid #fff;border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,0.4);"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      }),
    }).addTo(map);

    mapInstanceRef.current = map;

    // 初期レイヤーを読み込み
    setTimeout(() => {
      activeLayers.forEach(code => fetchLayerData(code));
    }, 500);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        layersRef.current = {};
        markerRef.current = null;
      }
    };
  }, [lat, lng]);

  return (
    <div style={{ marginTop: '16px' }}>
      <div style={{ marginBottom: '12px', fontSize: '14px', fontWeight: 600, color: '#374151' }}>
        MAP表示
      </div>

      {/* レイヤー選択 */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginBottom: '12px',
        padding: '12px',
        backgroundColor: '#F9FAFB',
        borderRadius: '8px',
      }}>
        {LAYER_DEFINITIONS.map(layer => {
          const isActive = activeLayers.includes(layer.code);
          const isLoading = loading[layer.code];
          const hasError = errors[layer.code];

          return (
            <button
              key={layer.code}
              onClick={() => toggleLayer(layer.code)}
              disabled={isLoading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                fontWeight: 500,
                border: '1px solid',
                borderColor: isActive ? layer.color : '#D1D5DB',
                borderRadius: '6px',
                backgroundColor: isActive ? `${layer.color}15` : '#fff',
                color: isActive ? layer.color : '#6B7280',
                cursor: isLoading ? 'wait' : 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <span
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '2px',
                  backgroundColor: isActive ? layer.color : '#D1D5DB',
                }}
              />
              {layer.name}
              {isLoading && <span style={{ fontSize: '10px' }}>...</span>}
              {hasError && !isLoading && <span style={{ fontSize: '10px', color: '#9CA3AF' }}>×</span>}
            </button>
          );
        })}
      </div>

      {/* 地図 */}
      <div
        ref={mapContainerRef}
        style={{
          width: '100%',
          height: '400px',
          borderRadius: '8px',
          border: '1px solid #E5E7EB',
        }}
      />

      {/* 説明 */}
      <div style={{
        marginTop: '8px',
        padding: '8px 12px',
        backgroundColor: '#EFF6FF',
        borderRadius: '6px',
        fontSize: '11px',
        color: '#1E40AF',
      }}>
        💡 上のボタンで表示レイヤーを切り替えられます。ポリゴンをクリックすると詳細が表示されます。
      </div>
    </div>
  );
};

export default RegulationMap;
