import React, { useState } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import { geoService, NearestStation, PropertyStation } from '../../services/geoService';

interface TransportationFieldProps {
  disabled?: boolean;
}

export const TransportationField: React.FC<TransportationFieldProps> = ({ disabled = false }) => {
  const { watch, control } = useFormContext();

  // フォームの値を監視
  const prefecture = watch('prefecture') || '';
  const city = watch('city') || '';
  const address = watch('address') || '';
  const latitude = watch('latitude');
  const longitude = watch('longitude');

  const fullAddress = [prefecture, city, address].filter(Boolean).join('');
  const hasCoords = latitude && longitude && !isNaN(latitude) && !isNaN(longitude);

  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<NearestStation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchRadius, setSearchRadius] = useState(2000);
  const [manualStation, setManualStation] = useState({ station_name: '', line_name: '', walk_minutes: '' });

  // 座標から検索
  const handleSearchByCoords = async () => {
    if (!hasCoords) {
      setError('緯度経度が設定されていません。先に「住所から座標を取得」してください');
      return;
    }
    setIsSearching(true);
    setError(null);
    try {
      const result = await geoService.getNearestStations(latitude, longitude, searchRadius, 20);
      setSearchResults(result.stations);
    } catch (err) {
      setError('最寄駅の検索に失敗しました');
    } finally {
      setIsSearching(false);
    }
  };

  // 住所から検索
  const handleSearchByAddress = async () => {
    if (!fullAddress) {
      setError('住所を入力してください');
      return;
    }
    setIsSearching(true);
    setError(null);
    try {
      const geocodeResult = await geoService.geocode(fullAddress);
      const result = await geoService.getNearestStations(
        geocodeResult.latitude,
        geocodeResult.longitude,
        searchRadius,
        20
      );
      setSearchResults(result.stations);
    } catch (err) {
      setError('最寄駅の検索に失敗しました');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Controller
      name="transportation"
      control={control}
      defaultValue={[]}
      render={({ field }) => {
        const stations: PropertyStation[] = field.value || [];

        const addStation = (station: NearestStation) => {
          if (stations.length >= 10) {
            setError('最寄駅は10件まで登録できます');
            return;
          }
          const isDuplicate = stations.some(
            s => s.station_name === station.station_name && s.line_name === (station.line_name || '')
          );
          if (isDuplicate) return;

          field.onChange([...stations, {
            station_name: station.station_name,
            line_name: station.line_name || '',
            walk_minutes: station.walk_minutes
          }]);
        };

        const addManualStation = () => {
          if (!manualStation.station_name) return;
          if (stations.length >= 10) {
            setError('最寄駅は10件まで登録できます');
            return;
          }
          field.onChange([...stations, {
            station_name: manualStation.station_name,
            line_name: manualStation.line_name,
            walk_minutes: parseInt(manualStation.walk_minutes) || 0
          }]);
          setManualStation({ station_name: '', line_name: '', walk_minutes: '' });
        };

        const removeStation = (index: number) => {
          field.onChange(stations.filter((_, i) => i !== index));
        };

        const updateWalkMinutes = (index: number, minutes: number) => {
          const newStations = [...stations];
          newStations[index] = { ...newStations[index], walk_minutes: minutes };
          field.onChange(newStations);
        };

        return (
          <div style={{ marginTop: '8px' }}>
            {/* 登録済み駅 */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                登録済み（{stations.length}/10）
              </div>
              {stations.length === 0 ? (
                <p style={{ fontSize: '13px', color: '#9CA3AF' }}>最寄駅が登録されていません</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {stations.map((station, index) => (
                    <div
                      key={`${station.station_name}-${station.line_name}-${index}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '10px 12px',
                        backgroundColor: '#F9FAFB',
                        borderRadius: '8px',
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 500 }}>{station.station_name}</span>
                        {station.line_name && (
                          <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '8px' }}>
                            （{station.line_name}）
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '13px', color: '#6B7280' }}>徒歩</span>
                        <input
                          type="number"
                          value={station.walk_minutes}
                          onChange={(e) => updateWalkMinutes(index, parseInt(e.target.value) || 0)}
                          disabled={disabled}
                          min="1"
                          style={{
                            width: '60px',
                            padding: '4px 8px',
                            fontSize: '13px',
                            border: '1px solid #E5E7EB',
                            borderRadius: '4px',
                            textAlign: 'right',
                          }}
                        />
                        <span style={{ fontSize: '13px', color: '#6B7280' }}>分</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeStation(index)}
                        disabled={disabled}
                        style={{
                          padding: '4px',
                          backgroundColor: 'transparent',
                          border: 'none',
                          cursor: disabled ? 'not-allowed' : 'pointer',
                          color: '#EF4444',
                        }}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 自動検索 */}
            <div style={{ padding: '12px', backgroundColor: '#F0F9FF', borderRadius: '8px', marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#1E40AF', marginBottom: '8px' }}>
                最寄駅を自動検索
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
                <select
                  value={searchRadius}
                  onChange={(e) => setSearchRadius(parseInt(e.target.value))}
                  disabled={disabled}
                  style={{
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #BFDBFE',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                >
                  <option value={500}>500m以内</option>
                  <option value={1000}>1km以内</option>
                  <option value={2000}>2km以内</option>
                  <option value={3000}>3km以内</option>
                </select>
                <button
                  type="button"
                  onClick={handleSearchByCoords}
                  disabled={disabled || isSearching || !hasCoords}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    backgroundColor: hasCoords ? '#10B981' : '#9CA3AF',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: disabled || isSearching || !hasCoords ? 'not-allowed' : 'pointer',
                  }}
                >
                  {isSearching ? '検索中...' : '座標から検索'}
                </button>
                <button
                  type="button"
                  onClick={handleSearchByAddress}
                  disabled={disabled || isSearching || !fullAddress}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    backgroundColor: fullAddress ? '#3B82F6' : '#9CA3AF',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: disabled || isSearching || !fullAddress ? 'not-allowed' : 'pointer',
                  }}
                >
                  {isSearching ? '検索中...' : '住所から検索'}
                </button>
              </div>
              {!hasCoords && !fullAddress && (
                <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '8px' }}>
                  住所または緯度経度を入力すると検索できます
                </p>
              )}
            </div>

            {/* エラー */}
            {error && (
              <div style={{ padding: '8px 12px', backgroundColor: '#FEF2F2', color: '#DC2626', fontSize: '13px', borderRadius: '6px', marginBottom: '12px' }}>
                {error}
              </div>
            )}

            {/* 検索結果 */}
            {searchResults.length > 0 && (
              <div style={{ padding: '12px', backgroundColor: '#ECFDF5', borderRadius: '8px', marginBottom: '16px' }}>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#065F46', marginBottom: '8px' }}>
                  検索結果（クリックで追加）
                </div>
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  {searchResults.map((station, index) => {
                    const isAdded = stations.some(
                      s => s.station_name === station.station_name && s.line_name === (station.line_name || '')
                    );
                    return (
                      <button
                        key={`${station.station_id}-${index}`}
                        type="button"
                        onClick={() => addStation(station)}
                        disabled={isAdded || disabled}
                        style={{
                          width: '100%',
                          textAlign: 'left',
                          padding: '8px 12px',
                          marginBottom: '4px',
                          backgroundColor: isAdded ? '#D1D5DB' : '#fff',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: isAdded || disabled ? 'not-allowed' : 'pointer',
                          opacity: isAdded ? 0.6 : 1,
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <span style={{ fontWeight: 500 }}>{station.station_name}</span>
                            {station.line_name && (
                              <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '8px' }}>
                                （{station.line_name}）
                              </span>
                            )}
                          </div>
                          <span style={{ fontSize: '12px', color: '#6B7280' }}>
                            {station.distance_meters}m / 徒歩{station.walk_minutes}分
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
                <button
                  type="button"
                  onClick={() => setSearchResults([])}
                  style={{
                    marginTop: '8px',
                    fontSize: '12px',
                    color: '#6B7280',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  検索結果を閉じる
                </button>
              </div>
            )}

            {/* 手動追加 */}
            <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '8px' }}>
                手動で追加
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                <input
                  type="text"
                  value={manualStation.station_name}
                  onChange={(e) => setManualStation({ ...manualStation, station_name: e.target.value })}
                  placeholder="駅名"
                  disabled={disabled}
                  style={{
                    flex: 1,
                    minWidth: '120px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                  }}
                />
                <input
                  type="text"
                  value={manualStation.line_name}
                  onChange={(e) => setManualStation({ ...manualStation, line_name: e.target.value })}
                  placeholder="路線名"
                  disabled={disabled}
                  style={{
                    flex: 1,
                    minWidth: '120px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                  }}
                />
                <input
                  type="number"
                  value={manualStation.walk_minutes}
                  onChange={(e) => setManualStation({ ...manualStation, walk_minutes: e.target.value })}
                  placeholder="徒歩(分)"
                  disabled={disabled}
                  min="1"
                  style={{
                    width: '80px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                  }}
                />
                <button
                  type="button"
                  onClick={addManualStation}
                  disabled={disabled || !manualStation.station_name}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    backgroundColor: manualStation.station_name ? '#6B7280' : '#D1D5DB',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: disabled || !manualStation.station_name ? 'not-allowed' : 'pointer',
                  }}
                >
                  追加
                </button>
              </div>
            </div>
          </div>
        );
      }}
    />
  );
};

export default TransportationField;
