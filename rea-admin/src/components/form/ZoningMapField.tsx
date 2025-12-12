import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useFormContext } from 'react-hook-form';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

// ユニークIDを生成（再マウント時の問題を防ぐ）
let mapIdCounter = 0;

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

// 都市計画区域の色マッピング（境界線のみ表示）
const URBAN_PLANNING_COLORS: Record<number, string> = {
  1: '#FF0000',  // 市街化区域（赤）
  2: '#00AA00',  // 市街化調整区域（緑）
  3: '#0066FF',  // その他用途地域（青）
  4: '#999999',  // 用途未設定（グレー）
};

// 凡例データ（略称 + 標準建ぺい率/容積率）
const ZONE_LEGEND = [
  { code: 1, name: '1低専', color: '#00FF00', ratio: '30-60/50-200' },
  { code: 2, name: '2低専', color: '#80FF00', ratio: '30-60/50-200' },
  { code: 3, name: '1中高', color: '#FFFF00', ratio: '30-60/100-500' },
  { code: 4, name: '2中高', color: '#FFCC00', ratio: '30-60/100-500' },
  { code: 5, name: '1住居', color: '#FF9900', ratio: '50-80/100-500' },
  { code: 6, name: '2住居', color: '#FF6600', ratio: '50-80/100-500' },
  { code: 7, name: '準住居', color: '#FF3300', ratio: '50-80/100-500' },
  { code: 8, name: '近商', color: '#FF00FF', ratio: '60-80/100-500' },
  { code: 9, name: '商業', color: '#FF0000', ratio: '80/200-1300' },
  { code: 10, name: '準工', color: '#00FFFF', ratio: '50-80/100-500' },
  { code: 11, name: '工業', color: '#0080FF', ratio: '50-60/100-400' },
  { code: 12, name: '工専', color: '#0000FF', ratio: '30-60/100-400' },
  { code: 21, name: '田園', color: '#90EE90', ratio: '30-60/50-200' },
];

// 都市計画区域凡例
const URBAN_PLANNING_LEGEND = [
  { code: 1, name: '市街化区域', color: '#FF0000' },
  { code: 2, name: '市街化調整', color: '#00AA00' },
  { code: 3, name: '非線引区域', color: '#0066FF' },
  { code: 4, name: '区域外', color: '#999999' },
];

export const ZoningMapField: React.FC = () => {
  const { watch } = useFormContext();
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);
  const urbanPlanningLayerRef = useRef<L.GeoJSON | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const initializingRef = useRef(false);

  // ユニークなマップIDを保持（再マウント対策）
  const [mapId] = useState(() => `zoning-map-${++mapIdCounter}`);
  const [isLoading, setIsLoading] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [selectedZone, setSelectedZone] = useState<any>(null);
  const [contextMenu, setContextMenu] = useState<{
    lat: number;
    lng: number;
    x: number;
    y: number;
    zoning: any;
    urban: any;
    loading: boolean;
  } | null>(null);

  const lat = watch('latitude');
  const lng = watch('longitude');

  // マップ初期化関数
  const initializeMap = useCallback(() => {
    // 既に初期化中または初期化済みならスキップ
    if (initializingRef.current || mapInstanceRef.current) return;

    const container = mapContainerRef.current;
    if (!container) return;

    // コンテナのサイズをチェック（0だと初期化失敗する）
    const rect = container.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      console.log('ZoningMap: Container has no size, retrying...');
      return;
    }

    initializingRef.current = true;
    setInitError(null);

    try {
      // 初期位置（緯度経度がなければ札幌駅）
      const initialLat = lat || 43.0686;
      const initialLng = lng || 141.3508;

      const map = L.map(container, {
        scrollWheelZoom: true,
      }).setView([initialLat, initialLng], 17);
      mapInstanceRef.current = map;

    // 地理院タイル
    L.tileLayer('https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png', {
      attribution: '<a href="https://maps.gsi.go.jp/development/ichiran.html">地理院タイル</a>',
      maxZoom: 18,
    }).addTo(map);

    // 移動・ズーム時にポリゴンを再取得
    const loadData = async () => {
      const bounds = map.getBounds();
      const zoom = map.getZoom();
      const minLat = bounds.getSouth();
      const minLng = bounds.getWest();
      const maxLat = bounds.getNorth();
      const maxLng = bounds.getEast();
      const simplify = zoom < 14 ? 0.0005 : 0.0001;
      const urbanSimplify = zoom < 14 ? 0.001 : 0.0002;

      // 用途地域を取得
      try {
        const response = await fetch(
          `${API_URL}/api/v1/geo/zoning/geojson?min_lat=${minLat}&min_lng=${minLng}&max_lat=${maxLat}&max_lng=${maxLng}&simplify=${simplify}`
        );
        const geojson = await response.json();

        if (geoJsonLayerRef.current && map) {
          map.removeLayer(geoJsonLayerRef.current);
        }

        if (geojson.features?.length > 0) {
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
              layer.on('mouseover', (e) => {
                (e.target as L.Path).setStyle({ fillOpacity: 0.8, weight: 2 });
              });
              layer.on('mouseout', (e) => {
                (e.target as L.Path).setStyle({ fillOpacity: 0.5, weight: 1 });
              });
            },
          });
          layer.addTo(map);
          geoJsonLayerRef.current = layer;
        }
      } catch (err) {
        console.error('用途地域データ取得エラー:', err);
      }

      // 都市計画区域を取得
      try {
        const response = await fetch(
          `${API_URL}/api/v1/geo/urban-planning/geojson?min_lat=${minLat}&min_lng=${minLng}&max_lat=${maxLat}&max_lng=${maxLng}&simplify=${urbanSimplify}`
        );
        const geojson = await response.json();

        if (urbanPlanningLayerRef.current && map) {
          map.removeLayer(urbanPlanningLayerRef.current);
        }

        if (geojson.features?.length > 0) {
          const layer = L.geoJSON(geojson, {
            style: (feature) => {
              const layerNo = feature?.properties?.layer_no || 4;
              return {
                fillColor: 'transparent',
                fillOpacity: 0,
                color: URBAN_PLANNING_COLORS[layerNo] || '#999999',
                weight: 3,
                dashArray: '8, 4',
              };
            },
            onEachFeature: (feature, layer) => {
              layer.on('click', () => {
                setSelectedZone({ ...feature.properties, isUrbanPlanning: true });
              });
            },
          });
          layer.addTo(map);
          urbanPlanningLayerRef.current = layer;
        }
      } catch (err) {
        console.error('都市計画区域データ取得エラー:', err);
      }

      setIsLoading(false);
    };

    map.on('moveend', loadData);

    // 右クリックで情報取得
    map.on('contextmenu', async (e: L.LeafletMouseEvent) => {
      const { lat: clickLat, lng: clickLng } = e.latlng;
      const containerPoint = e.containerPoint;

      // ダイアログを表示（ローディング状態）
      setContextMenu({
        lat: clickLat,
        lng: clickLng,
        x: containerPoint.x,
        y: containerPoint.y,
        zoning: null,
        urban: null,
        loading: true,
      });

      // APIから情報を取得
      try {
        const [zoningRes, urbanRes] = await Promise.all([
          fetch(`${API_URL}/api/v1/geo/zoning?lat=${clickLat}&lng=${clickLng}`),
          fetch(`${API_URL}/api/v1/geo/urban-planning?lat=${clickLat}&lng=${clickLng}`)
        ]);

        const zoningData = await zoningRes.json();
        const urbanData = await urbanRes.json();

        setContextMenu(prev => prev ? {
          ...prev,
          zoning: zoningData.zones?.[0] || null,
          urban: urbanData.areas?.[0] || null,
          loading: false,
        } : null);
      } catch (err) {
        console.error('情報取得エラー:', err);
        setContextMenu(prev => prev ? { ...prev, loading: false } : null);
      }
    });

    // クリックでダイアログを閉じる
    map.on('click', () => {
      setContextMenu(null);
    });

    // 初回読み込み
    setIsLoading(true);
    loadData();
    setMapReady(true);

    // サイズを再計算（Leafletの既知の問題対策）
    setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 200);

    } catch (err) {
      console.error('ZoningMap: Initialization error', err);
      setInitError('地図の初期化に失敗しました');
    } finally {
      initializingRef.current = false;
    }
  }, [lat, lng]);

  // マップ初期化用useEffect
  useEffect(() => {
    // 初期化をリトライするインターバル
    let retryCount = 0;
    const maxRetries = 10;

    const tryInit = () => {
      if (mapInstanceRef.current) return; // 既に初期化済み

      initializeMap();

      // まだ初期化できていなければリトライ
      if (!mapInstanceRef.current && retryCount < maxRetries) {
        retryCount++;
        setTimeout(tryInit, 100);
      }
    };

    // 初回は少し待ってから実行（DOM描画を待つ）
    const timer = setTimeout(tryInit, 50);

    return () => {
      clearTimeout(timer);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
      initializingRef.current = false;
      setMapReady(false);
    };
  }, [initializeMap]);

  // 緯度経度が変わったらマップを移動
  useEffect(() => {
    if (!mapInstanceRef.current || !lat || !lng) return;

    mapInstanceRef.current.setView([lat, lng], 17);

    // マーカーを更新
    if (markerRef.current) {
      markerRef.current.setLatLng([lat, lng]);
    } else {
      markerRef.current = L.marker([lat, lng], {
        icon: L.divIcon({
          className: 'custom-marker',
          html: '<div style="width:20px;height:20px;background:#DC2626;border:3px solid #fff;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>',
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        }),
      }).addTo(mapInstanceRef.current);
    }
  }, [lat, lng]);

  return (
    <div style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', gap: '16px' }}>
        {/* 地図 */}
        <div style={{ flex: 1, position: 'relative' }}>
          <div
            ref={mapContainerRef}
            id={mapId}
            style={{
              width: '100%',
              height: '300px',
              borderRadius: '8px',
              border: '1px solid #E5E7EB',
              backgroundColor: '#F3F4F6',
              position: 'relative',
            }}
          />
          {/* 地図初期化前のプレースホルダー */}
          {!mapReady && !initError && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#F3F4F6',
              borderRadius: '8px',
              color: '#6B7280',
              fontSize: '12px',
            }}>
              地図を読み込み中...
            </div>
          )}
          {/* エラー表示 */}
          {initError && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#FEE2E2',
              borderRadius: '8px',
              color: '#991B1B',
              fontSize: '12px',
            }}>
              {initError}
            </div>
          )}
          {isLoading && (
            <div style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              backgroundColor: 'rgba(255,255,255,0.9)',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '11px',
            }}>
              読み込み中...
            </div>
          )}

          {/* 右クリックダイアログ */}
          {contextMenu && (
            <div
              style={{
                position: 'absolute',
                left: Math.min(contextMenu.x, 280),
                top: Math.min(contextMenu.y, 180),
                backgroundColor: '#fff',
                borderRadius: '8px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.25)',
                padding: '12px',
                minWidth: '200px',
                fontSize: '12px',
                zIndex: 1000,
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* ヘッダー */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px',
                paddingBottom: '8px',
                borderBottom: '1px solid #E5E7EB',
              }}>
                <span style={{ fontWeight: 600, color: '#374151' }}>地点情報</span>
                <button
                  onClick={() => setContextMenu(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '16px',
                    cursor: 'pointer',
                    color: '#9CA3AF',
                    padding: '0 4px',
                  }}
                >
                  ×
                </button>
              </div>

              {contextMenu.loading ? (
                <div style={{ color: '#6B7280', padding: '8px 0' }}>読み込み中...</div>
              ) : (
                <>
                  {/* 用途地域 */}
                  <div style={{ marginBottom: '10px' }}>
                    <div style={{ color: '#9CA3AF', fontSize: '10px', marginBottom: '2px' }}>用途地域</div>
                    <div style={{ fontWeight: 600, color: contextMenu.zoning ? '#1F2937' : '#9CA3AF' }}>
                      {contextMenu.zoning?.zone_name || '指定なし'}
                    </div>
                  </div>

                  {/* 都市計画 */}
                  <div style={{ marginBottom: '10px' }}>
                    <div style={{ color: '#9CA3AF', fontSize: '10px', marginBottom: '2px' }}>都市計画</div>
                    <div style={{ fontWeight: 600, color: contextMenu.urban ? '#1F2937' : '#9CA3AF' }}>
                      {contextMenu.urban?.area_type || '指定なし'}
                    </div>
                  </div>

                  {/* 建ぺい率・容積率 */}
                  {contextMenu.zoning && (
                    <div style={{
                      display: 'flex',
                      gap: '16px',
                      padding: '8px 0',
                      borderTop: '1px solid #E5E7EB',
                    }}>
                      <div>
                        <div style={{ color: '#9CA3AF', fontSize: '10px' }}>建ぺい率</div>
                        <div style={{ fontWeight: 600 }}>
                          {contextMenu.zoning.building_coverage_ratio ?? '-'}%
                        </div>
                      </div>
                      <div>
                        <div style={{ color: '#9CA3AF', fontSize: '10px' }}>容積率</div>
                        <div style={{ fontWeight: 600 }}>
                          {contextMenu.zoning.floor_area_ratio ?? '-'}%
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 座標 */}
                  <div style={{
                    marginTop: '8px',
                    paddingTop: '8px',
                    borderTop: '1px solid #E5E7EB',
                    color: '#9CA3AF',
                    fontSize: '10px',
                    fontFamily: 'monospace',
                  }}>
                    {contextMenu.lat.toFixed(6)}, {contextMenu.lng.toFixed(6)}
                  </div>
                </>
              )}
            </div>
          )}

          {/* 選択したエリア情報 */}
          {selectedZone && (
            <div style={{
              position: 'absolute',
              bottom: '8px',
              left: '8px',
              right: '8px',
              backgroundColor: 'rgba(255,255,255,0.95)',
              padding: '10px',
              borderRadius: '6px',
              fontSize: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            }}>
              {selectedZone.isUrbanPlanning ? (
                // 都市計画区域
                <div style={{ fontWeight: 600, color: URBAN_PLANNING_COLORS[selectedZone.layer_no] || '#333' }}>
                  {selectedZone.area_type}
                </div>
              ) : (
                // 用途地域
                <>
                  <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                    {selectedZone.zone_name}
                  </div>
                  <div style={{ color: '#6B7280' }}>
                    {selectedZone.city_name && <span>{selectedZone.city_name} / </span>}
                    建ぺい率: {selectedZone.building_coverage_ratio ?? '-'}% /
                    容積率: {selectedZone.floor_area_ratio ?? '-'}%
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* 凡例 */}
        <div style={{
          width: '200px',
          backgroundColor: '#fff',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          padding: '10px',
          fontSize: '10px',
          maxHeight: '300px',
          overflowY: 'auto',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '6px',
            paddingBottom: '4px',
            borderBottom: '1px solid #E5E7EB',
          }}>
            <span style={{ fontWeight: 600, color: '#374151' }}>凡例</span>
            <span style={{ color: '#9CA3AF', fontSize: '9px' }}>建/容(%)</span>
          </div>
          {ZONE_LEGEND.map((item) => (
            <div
              key={item.code}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '2px 0',
              }}
            >
              <div
                style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: item.color,
                  border: '1px solid #888',
                  borderRadius: '2px',
                  flexShrink: 0,
                }}
              />
              <span style={{ flex: 1, lineHeight: 1.1 }}>{item.name}</span>
              <span style={{ color: '#6B7280', fontSize: '9px', fontFamily: 'monospace' }}>{item.ratio}</span>
            </div>
          ))}

          {/* 都市計画区域凡例 */}
          <div style={{
            marginTop: '8px',
            paddingTop: '6px',
            borderTop: '1px solid #E5E7EB',
          }}>
            <div style={{ fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
              都市計画 <span style={{ fontWeight: 400, color: '#9CA3AF', fontSize: '9px' }}>(破線)</span>
            </div>
            {URBAN_PLANNING_LEGEND.map((item) => (
              <div
                key={item.code}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '2px 0',
                }}
              >
                <div
                  style={{
                    width: '16px',
                    height: '0',
                    borderTop: `3px dashed ${item.color}`,
                    flexShrink: 0,
                  }}
                />
                <span style={{ lineHeight: 1.1 }}>{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ヘルプ */}
      <div style={{
        marginTop: '8px',
        padding: '8px 12px',
        backgroundColor: '#EFF6FF',
        borderRadius: '6px',
        fontSize: '11px',
        color: '#1E40AF',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
      }}>
        <span style={{ fontSize: '13px' }}>💡</span>
        <span>地図上で<strong>右クリック</strong>すると、その地点の用途地域・都市計画・建ぺい率/容積率が表示されます</span>
      </div>

      {/* 注意書き */}
      {!lat || !lng ? (
        <div style={{
          marginTop: '8px',
          padding: '8px 12px',
          backgroundColor: '#FEF3C7',
          borderRadius: '6px',
          fontSize: '11px',
          color: '#92400E',
        }}>
          緯度・経度を入力すると、物件位置にマーカーが表示されます
        </div>
      ) : null}
    </div>
  );
};

export default ZoningMapField;
