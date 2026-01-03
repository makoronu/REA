/**
 * 法令制限・ハザードMAP表示コンポーネント
 *
 * 不動産情報ライブラリAPIからGeoJSONを取得してMAP上に表示
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';

interface RegulationMapProps {
  lat: number;
  lng: number;
}

// 用途地域の色マッピング（youto_id → 色）
const ZONE_COLORS: Record<number, string> = {
  1: '#00FF00',   // 第一種低層住居専用
  2: '#80FF00',   // 第二種低層住居専用
  3: '#FFFF00',   // 第一種中高層住居専用
  4: '#FFCC00',   // 第二種中高層住居専用
  5: '#FF9900',   // 第一種住居
  6: '#FF6600',   // 第二種住居
  7: '#FF3300',   // 準住居
  8: '#FF00FF',   // 近隣商業
  9: '#FF0000',   // 商業
  10: '#00FFFF',  // 準工業
  11: '#0080FF',  // 工業
  12: '#0000FF',  // 工業専用
  21: '#90EE90',  // 田園住居
  99: '#CCCCCC',  // 無指定
};

// 用途地域凡例
const ZONE_LEGEND = [
  { code: 1, name: '1低専', color: '#00FF00' },
  { code: 2, name: '2低専', color: '#80FF00' },
  { code: 3, name: '1中高', color: '#FFFF00' },
  { code: 4, name: '2中高', color: '#FFCC00' },
  { code: 5, name: '1住居', color: '#FF9900' },
  { code: 6, name: '2住居', color: '#FF6600' },
  { code: 7, name: '準住居', color: '#FF3300' },
  { code: 8, name: '近商', color: '#FF00FF' },
  { code: 9, name: '商業', color: '#FF0000' },
  { code: 10, name: '準工', color: '#00FFFF' },
  { code: 11, name: '工業', color: '#0080FF' },
  { code: 12, name: '工専', color: '#0000FF' },
  { code: 21, name: '田園', color: '#90EE90' },
];

// 防火地域の色
const FIRE_COLORS: Record<string, string> = {
  '防火地域': '#FF0000',
  '準防火地域': '#FF9900',
};

// 浸水深の色
const FLOOD_COLORS: Record<string, string> = {
  '0.5m未満': '#FFFFCC',
  '0.5～3m': '#FFCC66',
  '3～5m': '#FF9933',
  '5～10m': '#FF6600',
  '10m以上': '#CC0000',
};

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
        `${API_BASE_URL}${API_PATHS.REINFOLIB.tile(layerCode)}?lat=${lat}&lng=${lng}`
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

        // 色決定関数
        const getFeatureColor = (props: any): string => {
          if (layerCode === 'XKT002') {
            // 用途地域: youto_id で色分け
            const youtoId = props.youto_id || 99;
            return ZONE_COLORS[youtoId] || '#CCCCCC';
          } else if (layerCode === 'XKT014') {
            // 防火地域
            const fireType = props.fire_prevent_ja || '';
            return FIRE_COLORS[fireType] || '#F97316';
          } else if (layerCode === 'XKT026' || layerCode === 'XKT027' || layerCode === 'XKT028') {
            // 浸水系: 浸水深で色分け
            const depth = props.depth_ja || '';
            return FLOOD_COLORS[depth] || '#06B6D4';
          } else if (layerCode === 'XKT029') {
            // 土砂災害: 警戒区域=黄, 特別警戒区域=赤
            const type = props.kiken_type_ja || '';
            return type.includes('特別') ? '#FF0000' : '#FFCC00';
          }
          return layerDef?.color || '#666';
        };

        const layer = L.geoJSON(geojson, {
          style: (feature) => {
            const color = getFeatureColor(feature?.properties || {});
            return {
              fillColor: color,
              fillOpacity: 0.5,
              color: '#333',
              weight: 1,
            };
          },
          onEachFeature: (feature, layer) => {
            // ポップアップ表示
            const props = feature.properties;
            let content = '';

            if (layerCode === 'XKT002') {
              content = `<strong>${props.use_area_ja || '用途地域'}</strong><br/>`;
              content += `建ぺい率: ${props.u_building_coverage_ratio_ja || '-'}<br/>`;
              content += `容積率: ${props.u_floor_area_ratio_ja || '-'}<br/>`;
              content += `${props.city_name || ''}`;
            } else if (layerCode === 'XKT014') {
              content = `<strong>${props.fire_prevent_ja || '防火地域'}</strong>`;
            } else if (layerCode === 'XKT026') {
              content = `<strong>洪水浸水想定</strong><br/>`;
              content += `浸水深: ${props.depth_ja || '-'}<br/>`;
              content += `河川: ${props.river_name || '-'}`;
            } else if (layerCode === 'XKT029') {
              content = `<strong>土砂災害警戒区域</strong><br/>`;
              content += `種別: ${props.kiken_type_ja || '-'}<br/>`;
              content += `現象: ${props.gensyo_type_ja || '-'}`;
            } else {
              content = `<strong>${layerDef?.name || layerCode}</strong>`;
            }

            layer.bindPopup(content);

            // ホバー効果
            layer.on('mouseover', (e) => {
              (e.target as L.Path).setStyle({ fillOpacity: 0.8, weight: 2 });
            });
            layer.on('mouseout', (e) => {
              (e.target as L.Path).setStyle({ fillOpacity: 0.5, weight: 1 });
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

    // タブ内での表示時にサイズを再計算
    setTimeout(() => {
      map.invalidateSize();
      activeLayers.forEach(code => fetchLayerData(code));
    }, 100);

    // ResizeObserverでコンテナサイズ変化を検出
    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize();
    });
    resizeObserver.observe(mapContainerRef.current);

    return () => {
      resizeObserver.disconnect();
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

      {/* 地図と凡例 */}
      <div style={{ display: 'flex', gap: '12px' }}>
        {/* 地図 */}
        <div
          ref={mapContainerRef}
          style={{
            flex: 1,
            height: '450px',
            borderRadius: '8px',
            border: '1px solid #E5E7EB',
          }}
        />

        {/* 凡例（用途地域選択時のみ表示） */}
        {activeLayers.includes('XKT002') && (
          <div style={{
            width: '140px',
            backgroundColor: '#fff',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '11px',
            maxHeight: '450px',
            overflowY: 'auto',
          }}>
            <div style={{
              fontWeight: 600,
              color: '#374151',
              marginBottom: '8px',
              paddingBottom: '6px',
              borderBottom: '1px solid #E5E7EB',
            }}>
              用途地域
            </div>
            {ZONE_LEGEND.map((item) => (
              <div
                key={item.code}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '3px 0',
                }}
              >
                <div
                  style={{
                    width: '14px',
                    height: '14px',
                    backgroundColor: item.color,
                    border: '1px solid #666',
                    borderRadius: '2px',
                    flexShrink: 0,
                  }}
                />
                <span>{item.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 説明 */}
      <div style={{
        marginTop: '8px',
        padding: '8px 12px',
        backgroundColor: '#EFF6FF',
        borderRadius: '6px',
        fontSize: '11px',
        color: '#1E40AF',
      }}>
        💡 ポリゴンをクリックすると詳細情報が表示されます。赤丸が物件位置です。
      </div>
    </div>
  );
};

export default RegulationMap;
