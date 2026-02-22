/**
 * RegulationPanel: 法令制限自動取得パネル（入力補助ツール）
 *
 * GeoPanel同様の入力補助パターン:
 * 1. reinfolib APIで法令制限+ハザード情報を取得
 * 2. 取得結果を画面に表示（ユーザー確認）
 * 3. 「フォームに反映して閉じる」で一括setValue
 *
 * データ格納はしない。入力補助のみ。
 */
import React, { useState, useCallback, useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import { api } from '../../services/api';
import { API_PATHS } from '../../constants/apiPaths';
import { RegulationMap } from '../regulations/RegulationMap';

// API返却の型定義
interface RegulationCodes {
  use_district?: number;
  building_coverage_ratio?: number;
  floor_area_ratio?: number;
  fire_prevention_area?: number;
  district_plan_name?: string;
  city_planning?: number;
}

interface RegulationResponse {
  regulations: Record<string, Record<string, string> | null>;
  codes: RegulationCodes;
}

// 結果表示用の行データ
interface ResultRow {
  label: string;
  value: string;
  willApply: boolean;
}

interface RegulationPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

/** regulations生データ → 表示用行リストに変換 */
function buildResultRows(
  regulations: Record<string, Record<string, string> | null>,
  codes: RegulationCodes
): ResultRow[] {
  const rows: ResultRow[] = [];

  // 用途地域
  const useArea = regulations.use_area;
  if (useArea) {
    if (useArea['用途地域']) {
      rows.push({ label: '用途地域', value: useArea['用途地域'], willApply: codes.use_district !== undefined });
    }
    if (useArea['建ぺい率']) {
      rows.push({ label: '建ぺい率', value: useArea['建ぺい率'], willApply: codes.building_coverage_ratio !== undefined });
    }
    if (useArea['容積率']) {
      rows.push({ label: '容積率', value: useArea['容積率'], willApply: codes.floor_area_ratio !== undefined });
    }
  }

  // 都市計画
  const cityPlanning = regulations.city_planning;
  if (cityPlanning?.['区域区分']) {
    rows.push({ label: '都市計画', value: cityPlanning['区域区分'], willApply: codes.city_planning !== undefined });
  }

  // 防火地域
  const firePrevention = regulations.fire_prevention;
  if (firePrevention?.['防火地域区分']) {
    rows.push({ label: '防火地域', value: firePrevention['防火地域区分'], willApply: codes.fire_prevention_area !== undefined });
  }

  // 地区計画
  const districtPlan = regulations.district_plan;
  if (districtPlan?.['地区計画名']) {
    rows.push({ label: '地区計画', value: districtPlan['地区計画名'], willApply: codes.district_plan_name !== undefined });
  }

  // 立地適正化計画
  const locationOpt = regulations.location_optimization;
  if (locationOpt && Object.keys(locationOpt).length > 0) {
    const text = Object.entries(locationOpt).map(([k, v]) => `${k}: ${v}`).join('、');
    rows.push({ label: '立地適正化計画', value: text, willApply: false });
  }

  // 都市計画道路
  const plannedRoad = regulations.planned_road;
  if (plannedRoad && Object.keys(plannedRoad).length > 0) {
    const text = Object.entries(plannedRoad).map(([k, v]) => `${k}: ${v}`).join('、');
    rows.push({ label: '都市計画道路', value: text, willApply: false });
  }

  // ハザード情報
  const hazardMap: Record<string, string> = {
    flood: '洪水浸水想定',
    landslide: '土砂災害警戒',
    tsunami: '津波浸水想定',
    storm_surge: '高潮浸水想定',
  };
  for (const [key, label] of Object.entries(hazardMap)) {
    const data = regulations[key];
    if (data && Object.keys(data).length > 0) {
      const text = Object.entries(data).map(([k, v]) => `${k}: ${v}`).join('、');
      rows.push({ label, value: text, willApply: false });
    } else {
      rows.push({ label, value: '該当なし', willApply: false });
    }
  }

  return rows;
}

export const RegulationPanel: React.FC<RegulationPanelProps> = ({ isOpen, onClose }) => {
  const { setValue, watch } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RegulationResponse | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // パネル再オープン時に前回結果をリセット（座標変更後の古い結果表示を防止）
  useEffect(() => {
    if (isOpen) {
      setResults(null);
      setMessage(null);
    }
  }, [isOpen]);

  const lat = watch('latitude');
  const lng = watch('longitude');
  const hasCoordinates = lat && lng && !isNaN(Number(lat)) && !isNaN(Number(lng));

  // 法令制限を取得 → ローカルstateに保存（フォームには書き込まない）
  const handleFetch = useCallback(async () => {
    if (!hasCoordinates) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);
    setResults(null);

    try {
      const response = await api.get(
        `${API_PATHS.REINFOLIB.REGULATIONS}?lat=${String(lat)}&lng=${String(lng)}`
      );

      const regulations = response.data?.regulations || {};
      const codes: RegulationCodes = response.data?.codes || {};
      setResults({ regulations, codes });

      const appliedCount = Object.keys(codes).length;
      setMessage({
        type: 'success',
        text: `法令制限情報を取得しました（自動反映対象: ${appliedCount}項目）`,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : '取得に失敗しました';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, hasCoordinates]);

  // フォームに反映して閉じる（GeoPanel同様の通常関数パターン）
  const handleApply = () => {
    if (!results) return;
    const codes = results.codes;

    if (codes.use_district != null) {
      setValue('use_district', [codes.use_district], { shouldDirty: true });
    }
    if (codes.building_coverage_ratio != null) {
      setValue('building_coverage_ratio', codes.building_coverage_ratio, { shouldDirty: true });
    }
    if (codes.floor_area_ratio != null) {
      setValue('floor_area_ratio', codes.floor_area_ratio, { shouldDirty: true });
    }
    if (codes.fire_prevention_area != null) {
      setValue('fire_prevention_area', codes.fire_prevention_area, { shouldDirty: true });
    }
    if (codes.district_plan_name != null) {
      setValue('district_plan_name', codes.district_plan_name, { shouldDirty: true });
    }
    if (codes.city_planning != null) {
      setValue('city_planning', [codes.city_planning], { shouldDirty: true });
    }

    onClose();
  };

  if (!isOpen) return null;

  const resultRows = results ? buildResultRows(results.regulations, results.codes) : [];

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
        maxWidth: '900px',
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
            ⚖️ 法令制限を自動取得
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

        {/* 地図 */}
        {hasCoordinates ? (
          <div style={{ marginBottom: '16px' }}>
            <RegulationMap lat={Number(lat)} lng={Number(lng)} />
          </div>
        ) : (
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

        {/* 取得ボタン */}
        <div style={{ marginBottom: '16px' }}>
          <button
            type="button"
            onClick={() => { void handleFetch(); }}
            disabled={!hasCoordinates || isLoading}
            style={{
              width: '100%',
              padding: '14px 20px',
              fontSize: '15px',
              fontWeight: 600,
              backgroundColor: hasCoordinates && !isLoading ? '#3B82F6' : '#D1D5DB',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: hasCoordinates && !isLoading ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {isLoading ? (
              <>
                <span style={{
                  display: 'inline-block', width: '18px', height: '18px',
                  border: '2px solid #fff', borderTopColor: 'transparent',
                  borderRadius: '50%', animation: 'spin 1s linear infinite',
                }} />
                取得中...
              </>
            ) : (
              <>🔍 この座標で法令制限を自動取得</>
            )}
          </button>
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
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <span>{message.text}</span>
            <button type="button" onClick={() => setMessage(null)} style={{
              cursor: 'pointer', background: 'none', border: 'none',
              color: 'inherit', fontWeight: 'bold', padding: '0 4px', fontSize: '16px',
            }}>×</button>
          </div>
        )}

        {/* 取得結果テーブル */}
        {resultRows.length > 0 && (
          <div style={{
            marginBottom: '16px',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            overflow: 'hidden',
          }}>
            <div style={{
              padding: '10px 16px',
              backgroundColor: '#F3F4F6',
              fontWeight: 600,
              fontSize: '13px',
              color: '#374151',
              display: 'flex',
              justifyContent: 'space-between',
            }}>
              <span>取得結果</span>
              <span style={{ fontSize: '11px', color: '#9CA3AF' }}>
                ● 反映対象 / ○ 情報表示のみ
              </span>
            </div>
            {resultRows.map((row) => (
              <div key={row.label} style={{
                display: 'flex',
                alignItems: 'center',
                padding: '10px 16px',
                borderTop: '1px solid #F3F4F6',
                fontSize: '13px',
                gap: '8px',
              }}>
                <span style={{
                  width: '16px',
                  textAlign: 'center',
                  color: row.willApply ? '#059669' : '#D1D5DB',
                  fontSize: '10px',
                }}>
                  {row.willApply ? '●' : '○'}
                </span>
                <span style={{
                  width: '120px',
                  flexShrink: 0,
                  fontWeight: 500,
                  color: '#374151',
                }}>
                  {row.label}
                </span>
                <span style={{
                  color: row.value === '該当なし' ? '#9CA3AF' : '#111827',
                  flex: 1,
                }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* フッター */}
        <div style={{
          display: 'flex', justifyContent: 'flex-end', gap: '12px',
          paddingTop: '16px', borderTop: '1px solid #E5E7EB',
        }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '10px 24px',
              backgroundColor: '#F3F4F6',
              color: '#374151',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 500,
              fontSize: '14px',
            }}
          >
            キャンセル
          </button>
          <button
            type="button"
            onClick={handleApply}
            disabled={!results}
            style={{
              padding: '10px 32px',
              backgroundColor: results ? '#3B82F6' : '#D1D5DB',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: results ? 'pointer' : 'not-allowed',
              fontWeight: 500,
              fontSize: '14px',
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
