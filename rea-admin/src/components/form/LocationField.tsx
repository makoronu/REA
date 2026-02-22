import React, { useState, useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import { geoService } from '../../services/geoService';
import { MESSAGE_TIMEOUT_MS } from '../../constants';

interface LocationFieldProps {
  disabled?: boolean;
  onOpenGeoPanel?: () => void;
}

export const LocationField: React.FC<LocationFieldProps> = ({ disabled = false, onOpenGeoPanel }) => {
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
    let hasError = false;

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
    } catch (err) {
      hasError = true;
      setGeocodeStatus('error');
      setGeocodeMessage('座標の取得に失敗しました');
      console.error('Geocode error:', err);
    } finally {
      setIsGeocoding(false);
      // 成功メッセージのみ自動消去（エラーは手動×で閉じる）
      if (!hasError) {
        setTimeout(() => setGeocodeStatus('idle'), MESSAGE_TIMEOUT_MS);
      }
    }
  };

  return (
    <div style={{ marginTop: '16px', padding: '16px', backgroundColor: '#F8FAFC', borderRadius: '12px' }}>
      {/* ヘッダー */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h4 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#374151' }}>
          位置情報（緯度・経度）
        </h4>
        {hasValidCoords && (
          <span style={{ fontSize: '12px', color: '#10B981' }}>
            ✓ 設定済み
          </span>
        )}
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
          <span style={{ fontSize: '12px', color: '#EF4444', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            ✗ {geocodeMessage}
            <button type="button" onClick={() => setGeocodeStatus('idle')} style={{ cursor: 'pointer', background: 'none', border: 'none', color: '#EF4444', fontWeight: 'bold', padding: '0 2px' }}>×</button>
          </span>
        )}
      </div>

      {/* 周辺情報自動取得ボタン */}
      {onOpenGeoPanel && (
        <div style={{ marginTop: '12px' }}>
          {hasValidCoords ? (
            <button
              type="button"
              onClick={onOpenGeoPanel}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                backgroundColor: '#EFF6FF',
                border: '1px solid #BFDBFE',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500,
                color: '#1D4ED8',
                width: '100%',
                justifyContent: 'center',
              }}
            >
              <span style={{ fontSize: '16px' }}>🗺️</span>
              地図確定＋周辺取得（学区・駅・バス・施設）
            </button>
          ) : (
            <div style={{
              padding: '10px 16px',
              backgroundColor: '#F9FAFB',
              border: '1px dashed #D1D5DB',
              borderRadius: '8px',
              fontSize: '13px',
              color: '#9CA3AF',
              textAlign: 'center',
            }}>
              座標を取得すると、地図確定＋周辺取得（学区・駅・バス・施設）が使えます
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LocationField;
