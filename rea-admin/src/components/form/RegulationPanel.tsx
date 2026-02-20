/**
 * RegulationPanel: 法令制限自動取得ポップアップ
 *
 * 地図表示 + reinfolib API自動取得 + 重要事項説明書チェックリスト
 * フォームフィールド（用途地域、建ぺい率等）はland_infoタブのFieldGroupで表示
 * このパネルは自動取得とチェックリストのみ担当
 */
import React, { useState, useCallback } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import { api } from '../../services/api';
import { API_PATHS } from '../../constants/apiPaths';
import { RegulationMap } from '../regulations/RegulationMap';
import { LEGAL_REGULATION_CATEGORIES } from '../../constants/legalRegulations';
import { MESSAGE_TIMEOUT_MS } from '../../constants';

// API返却の型定義
interface RegulationCodes {
  use_district?: string;
  building_coverage_ratio?: number;
  floor_area_ratio?: number;
  fire_prevention_area?: string;
  district_plan_name?: string;
  city_planning?: string;
}

interface RegulationPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RegulationPanel: React.FC<RegulationPanelProps> = ({ isOpen, onClose }) => {
  const { setValue, watch, control } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const lat = watch('latitude');
  const lng = watch('longitude');
  const hasCoordinates = lat && lng && !isNaN(Number(lat)) && !isNaN(Number(lng));

  // 法令制限を自動取得 → フォームに代入
  const handleFetchRegulations = useCallback(async () => {
    if (!hasCoordinates) {
      setMessage({ type: 'error', text: '緯度・経度を先に入力してください' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await api.get(
        `${API_PATHS.REINFOLIB.REGULATIONS}?lat=${String(lat)}&lng=${String(lng)}`
      );

      const codes: RegulationCodes = response.data?.codes || {};

      const updated: string[] = [];

      if (codes.use_district) {
        setValue('use_district', [codes.use_district], { shouldDirty: true });
        updated.push('用途地域');
      }
      if (codes.building_coverage_ratio !== undefined) {
        setValue('building_coverage_ratio', codes.building_coverage_ratio, { shouldDirty: true });
        updated.push('建ぺい率');
      }
      if (codes.floor_area_ratio !== undefined) {
        setValue('floor_area_ratio', codes.floor_area_ratio, { shouldDirty: true });
        updated.push('容積率');
      }
      if (codes.fire_prevention_area) {
        setValue('fire_prevention_area', codes.fire_prevention_area, { shouldDirty: true });
        updated.push('防火地域');
      }
      if (codes.district_plan_name) {
        setValue('district_plan_name', codes.district_plan_name, { shouldDirty: true });
        updated.push('地区計画');
      }
      if (codes.city_planning) {
        setValue('city_planning', [codes.city_planning], { shouldDirty: true });
        updated.push('都市計画');
      }

      if (updated.length > 0) {
        setMessage({ type: 'success', text: `${updated.join('・')}を設定しました` });
      } else {
        setMessage({ type: 'success', text: '法令制限情報を取得しました（該当データなし）' });
      }
      setTimeout(() => setMessage(null), MESSAGE_TIMEOUT_MS);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : '取得に失敗しました';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, hasCoordinates, setValue]);

  if (!isOpen) return null;

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

        {/* 自動取得ボタン */}
        <div style={{ marginBottom: '16px' }}>
          <button
            type="button"
            onClick={() => { void handleFetchRegulations(); }}
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

        {/* 取得結果の反映先ガイド */}
        {message?.type === 'success' && (
          <div style={{
            padding: '10px 14px', marginBottom: '16px', borderRadius: '8px',
            backgroundColor: '#EFF6FF', fontSize: '12px', color: '#1E40AF',
          }}>
            取得した値は「土地情報」タブのフィールドに反映されています。閉じてご確認ください。
          </div>
        )}

        {/* 法令制限チェックリスト */}
        <div style={{
          padding: '16px',
          backgroundColor: '#FFFBEB',
          borderRadius: '8px',
          marginBottom: '16px',
          border: '1px solid #FCD34D',
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: '#92400E' }}>
            重要事項説明書 法令制限（該当するものをチェック）
          </h4>
          <Controller
            name="legal_regulations_checked"
            control={control}
            defaultValue={[]}
            render={({ field }) => {
              const checkedItems: string[] = Array.isArray(field.value) ? field.value : [];
              const toggleItem = (item: string) => {
                const newValue = checkedItems.includes(item)
                  ? checkedItems.filter(i => i !== item)
                  : [...checkedItems, item];
                field.onChange(newValue);
              };
              return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {LEGAL_REGULATION_CATEGORIES.map((category) => (
                    <div key={category.name}>
                      <div style={{
                        fontSize: '12px', fontWeight: 600, color: '#78350F',
                        marginBottom: '8px', borderBottom: '1px solid #FCD34D', paddingBottom: '4px',
                      }}>
                        {category.name}
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px 16px' }}>
                        {category.items.map((item) => (
                          <label
                            key={item}
                            style={{
                              display: 'flex', alignItems: 'flex-start', gap: '6px',
                              fontSize: '12px', color: '#374151', cursor: 'pointer', padding: '2px 0',
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={checkedItems.includes(item)}
                              onChange={() => toggleItem(item)}
                              style={{ width: '14px', height: '14px', marginTop: '1px', flexShrink: 0 }}
                            />
                            <span style={{ lineHeight: '1.3' }}>{item}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              );
            }}
          />
        </div>

        {/* フッター */}
        <div style={{
          display: 'flex', justifyContent: 'flex-end',
          paddingTop: '16px', borderTop: '1px solid #E5E7EB',
        }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '10px 32px',
              backgroundColor: '#3B82F6',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 500,
              fontSize: '14px',
            }}
          >
            閉じる
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
