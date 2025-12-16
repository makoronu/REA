/**
 * 法令制限タブ
 *
 * 用途地域・都市計画・ハザード情報をMAP表示し、自動取得・登録する
 */
import React, { useState, useCallback } from 'react';
import { useFormContext } from 'react-hook-form';
import { API_URL } from '../../config';
import { RegulationMap } from '../regulations/RegulationMap';

interface RegulationData {
  use_area?: {
    '用途地域'?: string;
    '建ぺい率'?: string;
    '容積率'?: string;
    '都道府県'?: string;
    '市区町村'?: string;
  };
  fire_prevention?: {
    '防火地域区分'?: string;
  };
  flood?: Record<string, string>;
  landslide?: Record<string, string>;
  tsunami?: Record<string, string>;
  storm_surge?: Record<string, string>;
  location_optimization?: Record<string, string>;
  district_plan?: Record<string, string>;
  planned_road?: Record<string, string>;
}

// 用途地域コードマッピング
const USE_DISTRICT_MAP: Record<string, number> = {
  '第一種低層住居専用地域': 1,
  '第二種低層住居専用地域': 2,
  '第一種中高層住居専用地域': 3,
  '第二種中高層住居専用地域': 4,
  '第一種住居地域': 5,
  '第二種住居地域': 6,
  '準住居地域': 7,
  '近隣商業地域': 8,
  '商業地域': 9,
  '準工業地域': 10,
  '工業地域': 11,
  '工業専用地域': 12,
  '田園住居地域': 21,
};

export const RegulationTab: React.FC = () => {
  const { setValue, watch } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [regulationData, setRegulationData] = useState<RegulationData | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const lat = watch('latitude');
  const lng = watch('longitude');
  const hasCoordinates = lat && lng && !isNaN(Number(lat)) && !isNaN(Number(lng));

  // 現在の値を取得
  const currentUseDistrict = watch('use_district');
  const currentBuildingCoverage = watch('building_coverage_ratio');
  const currentFloorArea = watch('floor_area_ratio');
  const currentCityPlanning = watch('city_planning');

  // 法令制限を自動取得
  const handleFetchRegulations = useCallback(async () => {
    if (!hasCoordinates) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/reinfolib/regulations?lat=${lat}&lng=${lng}`
      );

      if (!response.ok) {
        throw new Error('法令制限情報の取得に失敗しました');
      }

      const data = await response.json();
      setRegulationData(data.regulations);
      setMessage({ type: 'success', text: '法令制限情報を取得しました。下の「登録」ボタンで保存できます。' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || '取得に失敗しました' });
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, hasCoordinates]);

  // 取得したデータをフォームに登録
  const handleRegister = useCallback(() => {
    if (!regulationData?.use_area) {
      setMessage({ type: 'error', text: '先に「自動取得」で情報を取得してください' });
      return;
    }

    const useArea = regulationData.use_area;

    // 用途地域コードを設定
    const zoneName = useArea['用途地域'] || '';
    const useDistrictCode = USE_DISTRICT_MAP[zoneName];
    if (useDistrictCode) {
      setValue('use_district', useDistrictCode, { shouldDirty: true });
    }

    // 建ぺい率（%を除去して数値に）
    const coverageStr = useArea['建ぺい率'] || '';
    const coverage = parseFloat(coverageStr.replace('%', ''));
    if (!isNaN(coverage)) {
      setValue('building_coverage_ratio', coverage, { shouldDirty: true });
    }

    // 容積率（%を除去して数値に）
    const floorStr = useArea['容積率'] || '';
    const floor = parseFloat(floorStr.replace('%', ''));
    if (!isNaN(floor)) {
      setValue('floor_area_ratio', floor, { shouldDirty: true });
    }

    setMessage({ type: 'success', text: '用途地域・建ぺい率・容積率を登録しました' });
    setTimeout(() => setMessage(null), 3000);
  }, [regulationData, setValue]);

  // 用途地域名を取得
  const getUseDistrictName = (code: number): string => {
    const entry = Object.entries(USE_DISTRICT_MAP).find(([_, c]) => c === code);
    return entry ? entry[0] : '未設定';
  };

  // 都市計画名を取得
  const getCityPlanningName = (code: number): string => {
    const map: Record<number, string> = {
      1: '市街化区域',
      2: '市街化調整区域',
      3: '非線引き都市計画区域',
      4: '都市計画区域外',
    };
    return map[code] || '未設定';
  };

  return (
    <div>
      {/* 現在の登録値 */}
      <div style={{
        padding: '16px',
        backgroundColor: '#F9FAFB',
        borderRadius: '8px',
        marginBottom: '16px',
      }}>
        <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#374151' }}>
          現在の登録値
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13px' }}>
          <div>
            <span style={{ color: '#6B7280' }}>用途地域: </span>
            <strong>{currentUseDistrict ? getUseDistrictName(currentUseDistrict) : '未設定'}</strong>
          </div>
          <div>
            <span style={{ color: '#6B7280' }}>都市計画: </span>
            <strong>{currentCityPlanning ? getCityPlanningName(currentCityPlanning) : '未設定'}</strong>
          </div>
          <div>
            <span style={{ color: '#6B7280' }}>建ぺい率: </span>
            <strong>{currentBuildingCoverage ? `${currentBuildingCoverage}%` : '未設定'}</strong>
          </div>
          <div>
            <span style={{ color: '#6B7280' }}>容積率: </span>
            <strong>{currentFloorArea ? `${currentFloorArea}%` : '未設定'}</strong>
          </div>
        </div>
      </div>

      {/* 自動取得・登録ボタン */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '16px',
      }}>
        <button
          type="button"
          onClick={handleFetchRegulations}
          disabled={!hasCoordinates || isLoading}
          style={{
            padding: '10px 20px',
            fontSize: '14px',
            fontWeight: 600,
            backgroundColor: hasCoordinates ? '#3B82F6' : '#D1D5DB',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: hasCoordinates && !isLoading ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          {isLoading ? (
            <>
              <span style={{ animation: 'spin 1s linear infinite' }}>⏳</span>
              取得中...
            </>
          ) : (
            <>🔍 法令制限を自動取得</>
          )}
        </button>

        {regulationData?.use_area && (
          <button
            type="button"
            onClick={handleRegister}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: 600,
              backgroundColor: '#10B981',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            ✅ 登録
          </button>
        )}
      </div>

      {/* メッセージ */}
      {message && (
        <div style={{
          padding: '12px 16px',
          marginBottom: '16px',
          borderRadius: '8px',
          backgroundColor: message.type === 'success' ? '#D1FAE5' : '#FEE2E2',
          color: message.type === 'success' ? '#065F46' : '#991B1B',
          fontSize: '13px',
        }}>
          {message.text}
        </div>
      )}

      {/* 取得結果表示 */}
      {regulationData?.use_area && (
        <div style={{
          padding: '16px',
          backgroundColor: '#EFF6FF',
          borderRadius: '8px',
          marginBottom: '16px',
          border: '1px solid #BFDBFE',
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#1E40AF' }}>
            取得結果（登録前プレビュー）
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '13px' }}>
            <div>用途地域: <strong>{regulationData.use_area['用途地域'] || '-'}</strong></div>
            <div>建ぺい率: <strong>{regulationData.use_area['建ぺい率'] || '-'}</strong></div>
            <div>容積率: <strong>{regulationData.use_area['容積率'] || '-'}</strong></div>
            <div>市区町村: <strong>{regulationData.use_area['市区町村'] || '-'}</strong></div>
          </div>

          {/* ハザード情報 */}
          {(regulationData.flood || regulationData.landslide || regulationData.tsunami || regulationData.storm_surge) && (
            <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #BFDBFE' }}>
              <h5 style={{ fontSize: '13px', fontWeight: 600, color: '#DC2626', marginBottom: '8px' }}>
                ⚠️ ハザード情報
              </h5>
              <div style={{ fontSize: '12px', color: '#991B1B' }}>
                {regulationData.flood && Object.keys(regulationData.flood).length > 0 && (
                  <div>洪水: {Object.values(regulationData.flood).join(', ')}</div>
                )}
                {regulationData.landslide && Object.keys(regulationData.landslide).length > 0 && (
                  <div>土砂災害: {Object.values(regulationData.landslide).join(', ')}</div>
                )}
                {regulationData.tsunami && Object.keys(regulationData.tsunami).length > 0 && (
                  <div>津波: {Object.values(regulationData.tsunami).join(', ')}</div>
                )}
                {regulationData.storm_surge && Object.keys(regulationData.storm_surge).length > 0 && (
                  <div>高潮: {Object.values(regulationData.storm_surge).join(', ')}</div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 緯度経度がない場合 */}
      {!hasCoordinates && (
        <div style={{
          padding: '40px 20px',
          backgroundColor: '#F9FAFB',
          borderRadius: '8px',
          border: '2px dashed #D1D5DB',
          textAlign: 'center',
          marginBottom: '16px',
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>📍</div>
          <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
            法令制限情報を取得するには
          </div>
          <div style={{ fontSize: '13px', color: '#9CA3AF' }}>
            「所在地・周辺情報」タブで緯度・経度を入力してください
          </div>
        </div>
      )}

      {/* MAP表示 */}
      {hasCoordinates && (
        <RegulationMap lat={Number(lat)} lng={Number(lng)} />
      )}
    </div>
  );
};

export default RegulationTab;
