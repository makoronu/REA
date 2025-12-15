import React, { useEffect, useState, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { API_URL } from '../../config';

// 用途地域の色マッピング
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

interface ZoneLegend {
  code: number;
  name: string;
  color: string;
  description: string;
}

interface ZoningFeature {
  type: 'Feature';
  properties: {
    id: number;
    zone_code: number;
    zone_name: string;
    building_coverage_ratio: number | null;
    floor_area_ratio: number | null;
    city_name: string | null;
  };
  geometry: any;
}

export const ZoningMapPage: React.FC = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);

  const [legend, setLegend] = useState<ZoneLegend[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [featureCount, setFeatureCount] = useState(0);
  const [selectedZone, setSelectedZone] = useState<ZoningFeature['properties'] | null>(null);

  // 凡例を取得
  useEffect(() => {
    fetch(`${API_URL}/api/v1/geo/zoning/legend`)
      .then(res => res.json())
      .then(data => setLegend(data))
      .catch(err => console.error('凡例取得エラー:', err));
  }, []);

  // マップ初期化
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // 札幌駅を初期表示（北海道データのみのため）
    const map = L.map(mapRef.current).setView([43.0686, 141.3508], 13);
    mapInstanceRef.current = map;

    // 地理院タイル
    L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
      attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>',
      maxZoom: 18,
    }).addTo(map);

    // 移動・ズーム時にポリゴンを再取得
    const loadZoning = () => {
      const bounds = map.getBounds();
      fetchZoningData(
        bounds.getSouth(),
        bounds.getWest(),
        bounds.getNorth(),
        bounds.getEast(),
        map.getZoom()
      );
    };

    map.on('moveend', loadZoning);
    map.on('zoomend', loadZoning);

    // 初回読み込み
    loadZoning();

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // ポリゴンデータ取得
  const fetchZoningData = async (
    minLat: number,
    minLng: number,
    maxLat: number,
    maxLng: number,
    zoom: number
  ) => {
    setIsLoading(true);

    // ズームレベルに応じて簡略化の度合いを調整
    const simplify = zoom < 12 ? 0.001 : zoom < 14 ? 0.0005 : 0.0001;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/geo/zoning/geojson?min_lat=${minLat}&min_lng=${minLng}&max_lat=${maxLat}&max_lng=${maxLng}&simplify=${simplify}`
      );
      const geojson = await response.json();

      setFeatureCount(geojson.features?.length || 0);

      // 既存レイヤーを削除
      if (geoJsonLayerRef.current && mapInstanceRef.current) {
        mapInstanceRef.current.removeLayer(geoJsonLayerRef.current);
      }

      // 新しいGeoJSONレイヤーを追加
      if (mapInstanceRef.current && geojson.features?.length > 0) {
        const layer = L.geoJSON(geojson, {
          style: (feature) => {
            const zoneCode = feature?.properties?.zone_code || 99;
            return {
              fillColor: ZONE_COLORS[zoneCode] || '#CCCCCC',
              fillOpacity: 0.5,
              color: '#333',
              weight: 1,
            };
          },
          onEachFeature: (feature, layer) => {
            layer.on('click', () => {
              setSelectedZone(feature.properties);
            });

            // ホバー時のハイライト
            layer.on('mouseover', (e) => {
              const target = e.target as L.Path;
              target.setStyle({
                fillOpacity: 0.8,
                weight: 2,
              });
            });
            layer.on('mouseout', (e) => {
              const target = e.target as L.Path;
              target.setStyle({
                fillOpacity: 0.5,
                weight: 1,
              });
            });
          },
        });

        layer.addTo(mapInstanceRef.current);
        geoJsonLayerRef.current = layer;
      }
    } catch (err) {
      console.error('用途地域データ取得エラー:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
      {/* サイドパネル - 凡例 */}
      <div style={{
        width: '280px',
        backgroundColor: '#fff',
        borderRight: '1px solid #E5E7EB',
        padding: '16px',
        overflowY: 'auto',
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
          用途地域マップ
        </h2>

        {/* 読み込み状態 */}
        <div style={{ marginBottom: '16px', fontSize: '13px', color: '#6B7280' }}>
          {isLoading ? (
            <span>読み込み中...</span>
          ) : (
            <span>表示中: {featureCount.toLocaleString()} 区域</span>
          )}
        </div>

        {/* 選択中のエリア情報 */}
        {selectedZone && (
          <div style={{
            marginBottom: '16px',
            padding: '12px',
            backgroundColor: '#F3F4F6',
            borderRadius: '8px',
          }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
              選択中のエリア
            </h3>
            <div style={{ fontSize: '13px' }}>
              <div style={{ marginBottom: '4px' }}>
                <strong>{selectedZone.zone_name}</strong>
              </div>
              {selectedZone.city_name && (
                <div style={{ color: '#6B7280', marginBottom: '4px' }}>
                  {selectedZone.city_name}
                </div>
              )}
              <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
                <div>
                  <span style={{ color: '#6B7280' }}>建ぺい率:</span>{' '}
                  <strong>{selectedZone.building_coverage_ratio ?? '-'}%</strong>
                </div>
                <div>
                  <span style={{ color: '#6B7280' }}>容積率:</span>{' '}
                  <strong>{selectedZone.floor_area_ratio ?? '-'}%</strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 凡例 */}
        <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>
          凡例
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {legend.map((item) => (
            <div
              key={item.code}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 8px',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'background-color 150ms',
              }}
              title={item.description}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#F3F4F6';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: item.color,
                  border: '1px solid #333',
                  borderRadius: '2px',
                  flexShrink: 0,
                }}
              />
              <span style={{ fontSize: '12px', lineHeight: 1.3 }}>
                {item.name}
              </span>
            </div>
          ))}
        </div>

        {/* 注意書き */}
        <div style={{
          marginTop: '16px',
          padding: '12px',
          backgroundColor: '#FEF3C7',
          borderRadius: '8px',
          fontSize: '11px',
          color: '#92400E',
        }}>
          <strong>注意:</strong> 現在は北海道のデータのみ表示されます。
          データは国土数値情報（用途地域データ）を使用しています。
        </div>
      </div>

      {/* 地図 */}
      <div style={{ flex: 1, position: 'relative' }}>
        <div ref={mapRef} style={{ width: '100%', height: '100%' }} />

        {/* 読み込み中オーバーレイ */}
        {isLoading && (
          <div style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            padding: '8px 16px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <div
              style={{
                width: '16px',
                height: '16px',
                border: '2px solid #3B82F6',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }}
            />
            <span style={{ fontSize: '13px' }}>読み込み中...</span>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ZoningMapPage;
