import React, { useState } from 'react';
import { geoService, NearestStation, PropertyStation } from '../services/geoService';

interface NearestStationsEditorProps {
  // 現在の最寄駅リスト
  stations: PropertyStation[];
  // 変更時のコールバック
  onChange: (stations: PropertyStation[]) => void;
  // 緯度（自動取得用）
  latitude?: number | null;
  // 経度（自動取得用）
  longitude?: number | null;
  // 住所（ジオコーディング用）
  address?: string;
  // 最大登録数
  maxStations?: number;
}

const NearestStationsEditor: React.FC<NearestStationsEditorProps> = ({
  stations,
  onChange,
  latitude,
  longitude,
  address,
  maxStations = 10
}) => {
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<NearestStation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchRadius, setSearchRadius] = useState(2000);

  // 住所から座標を取得して最寄駅検索
  const handleSearchByAddress = async () => {
    if (!address) {
      setError('住所を入力してください');
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults([]);

    try {
      // 住所から座標を取得
      const geocodeResult = await geoService.geocode(address);

      // 座標から最寄駅を検索
      const result = await geoService.getNearestStations(
        geocodeResult.latitude,
        geocodeResult.longitude,
        searchRadius,
        20  // 多めに取得
      );

      setSearchResults(result.stations);
    } catch (err) {
      setError('最寄駅の検索に失敗しました');
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  // 座標から直接最寄駅検索
  const handleSearchByCoordinates = async () => {
    if (!latitude || !longitude) {
      setError('緯度経度が設定されていません');
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults([]);

    try {
      const result = await geoService.getNearestStations(
        latitude,
        longitude,
        searchRadius,
        20
      );
      setSearchResults(result.stations);
    } catch (err) {
      setError('最寄駅の検索に失敗しました');
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  // 検索結果から駅を追加
  const handleAddStation = (station: NearestStation) => {
    if (stations.length >= maxStations) {
      setError(`最寄駅は${maxStations}件まで登録できます`);
      return;
    }

    // 重複チェック（同じ駅名+路線名）
    const isDuplicate = stations.some(
      s => s.station_name === station.station_name && s.line_name === (station.line_name || '')
    );
    if (isDuplicate) {
      return;
    }

    const newStation: PropertyStation = {
      station_name: station.station_name,
      line_name: station.line_name || '',
      walk_minutes: station.walk_minutes
    };

    onChange([...stations, newStation]);
  };

  // 駅を削除
  const handleRemoveStation = (index: number) => {
    const newStations = stations.filter((_, i) => i !== index);
    onChange(newStations);
  };

  // 手動で駅を追加
  const [manualStation, setManualStation] = useState({ station_name: '', line_name: '', walk_minutes: '' });

  const handleAddManualStation = () => {
    if (!manualStation.station_name) return;
    if (stations.length >= maxStations) {
      setError(`最寄駅は${maxStations}件まで登録できます`);
      return;
    }

    const newStation: PropertyStation = {
      station_name: manualStation.station_name,
      line_name: manualStation.line_name,
      walk_minutes: parseInt(manualStation.walk_minutes) || 0
    };

    onChange([...stations, newStation]);
    setManualStation({ station_name: '', line_name: '', walk_minutes: '' });
  };

  // 徒歩分数を更新
  const handleUpdateWalkMinutes = (index: number, minutes: number) => {
    const newStations = [...stations];
    newStations[index] = { ...newStations[index], walk_minutes: minutes };
    onChange(newStations);
  };

  return (
    <div className="space-y-4">
      {/* 登録済み最寄駅 */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">
          登録済み最寄駅（{stations.length}/{maxStations}）
        </h4>
        {stations.length === 0 ? (
          <p className="text-sm text-gray-500">最寄駅が登録されていません</p>
        ) : (
          <div className="space-y-2">
            {stations.map((station, index) => (
              <div
                key={`${station.station_name}-${station.line_name}-${index}`}
                className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <span className="font-medium">{station.station_name}</span>
                  {station.line_name && (
                    <span className="text-sm text-gray-500 ml-2">（{station.line_name}）</span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-sm text-gray-500">徒歩</span>
                  <input
                    type="number"
                    value={station.walk_minutes}
                    onChange={(e) => handleUpdateWalkMinutes(index, parseInt(e.target.value) || 0)}
                    className="w-16 px-2 py-1 text-sm border border-gray-300 rounded"
                    min="1"
                  />
                  <span className="text-sm text-gray-500">分</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveStation(index)}
                  className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 自動検索 */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">最寄駅を自動検索</h4>
        <div className="flex flex-wrap gap-2 mb-2">
          <select
            value={searchRadius}
            onChange={(e) => setSearchRadius(parseInt(e.target.value))}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md"
          >
            <option value={500}>500m以内</option>
            <option value={1000}>1km以内</option>
            <option value={2000}>2km以内</option>
            <option value={3000}>3km以内</option>
            <option value={5000}>5km以内</option>
          </select>
          <button
            type="button"
            onClick={handleSearchByAddress}
            disabled={isSearching || !address}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isSearching ? '検索中...' : '住所から検索'}
          </button>
          <button
            type="button"
            onClick={handleSearchByCoordinates}
            disabled={isSearching || !latitude || !longitude}
            className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isSearching ? '検索中...' : '座標から検索'}
          </button>
        </div>
        {!address && !latitude && (
          <p className="text-xs text-gray-500">住所または緯度経度を入力すると検索できます</p>
        )}
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="p-2 bg-red-50 text-red-600 text-sm rounded">
          {error}
        </div>
      )}

      {/* 検索結果 */}
      {searchResults.length > 0 && (
        <div className="border rounded-lg p-3 bg-blue-50">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            検索結果（クリックで追加）
          </h4>
          <div className="max-h-60 overflow-y-auto space-y-1">
            {searchResults.map((station, index) => {
              const isAdded = stations.some(
                s => s.station_name === station.station_name && s.line_name === (station.line_name || '')
              );
              return (
                <button
                  key={`${station.station_id}-${index}`}
                  type="button"
                  onClick={() => handleAddStation(station)}
                  disabled={isAdded}
                  className={`w-full text-left p-2 rounded transition-colors ${
                    isAdded
                      ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      : 'bg-white hover:bg-blue-100'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-medium">{station.station_name}</span>
                      {station.line_name && (
                        <span className="text-sm text-gray-500 ml-2">（{station.line_name}）</span>
                      )}
                    </div>
                    <span className="text-sm text-gray-600">
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
            className="mt-2 text-sm text-gray-500 hover:text-gray-700"
          >
            検索結果を閉じる
          </button>
        </div>
      )}

      {/* 手動追加 */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">手動で追加</h4>
        <div className="flex flex-wrap gap-2">
          <input
            type="text"
            value={manualStation.station_name}
            onChange={(e) => setManualStation({ ...manualStation, station_name: e.target.value })}
            placeholder="駅名"
            className="flex-1 min-w-32 px-3 py-2 text-sm border border-gray-300 rounded-md"
          />
          <input
            type="text"
            value={manualStation.line_name}
            onChange={(e) => setManualStation({ ...manualStation, line_name: e.target.value })}
            placeholder="路線名"
            className="flex-1 min-w-32 px-3 py-2 text-sm border border-gray-300 rounded-md"
          />
          <input
            type="number"
            value={manualStation.walk_minutes}
            onChange={(e) => setManualStation({ ...manualStation, walk_minutes: e.target.value })}
            placeholder="徒歩(分)"
            className="w-24 px-3 py-2 text-sm border border-gray-300 rounded-md"
            min="1"
          />
          <button
            type="button"
            onClick={handleAddManualStation}
            disabled={!manualStation.station_name}
            className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            追加
          </button>
        </div>
      </div>
    </div>
  );
};

export default NearestStationsEditor;
