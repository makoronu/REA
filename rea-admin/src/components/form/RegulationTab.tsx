/**
 * 法令制限タブ
 *
 * 用途地域・都市計画・ハザード情報をMAP表示し、自動取得・手動編集する
 * 重要事項説明書の法令チェック項目も管理
 */
import React, { useState, useCallback, useEffect } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import Select from 'react-select';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';
import { RegulationMap } from '../regulations/RegulationMap';
import { metadataService } from '../../services/metadataService';
import { parseOptions } from '../../utils/options';
import { OptionType } from '../../types/metadata';
import { LEGAL_REGULATION_CATEGORIES } from '../../constants/legalRegulations';

// フォールバック用デフォルト値（DB読み込み失敗時）
const DEFAULT_FIRE_PREVENTION_OPTIONS: OptionType[] = [
  { value: '1', label: '防火地域' },
  { value: '2', label: '準防火地域' },
  { value: '3', label: '指定なし' },
];

// フォールバック用デフォルト値（用途地域マッピング）
const DEFAULT_USE_DISTRICT_MAP: Record<string, string> = {
  '第一種低層住居専用地域': '1',
  '第二種低層住居専用地域': '2',
  '第一種中高層住居専用地域': '3',
  '第二種中高層住居専用地域': '4',
  '第一種住居地域': '5',
  '第二種住居地域': '6',
  '準住居地域': '7',
  '近隣商業地域': '8',
  '商業地域': '9',
  '準工業地域': '10',
  '工業地域': '11',
  '工業専用地域': '12',
  '田園住居地域': '21',
};

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


export const RegulationTab: React.FC = () => {
  const { setValue, watch, control, register } = useFormContext();
  const [isLoading, setIsLoading] = useState(false);
  const [regulationData, setRegulationData] = useState<RegulationData | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [useDistrictOptions, setUseDistrictOptions] = useState<OptionType[]>([]);
  const [cityPlanningOptions, setCityPlanningOptions] = useState<OptionType[]>([]);
  // メタデータ駆動: 防火地域選択肢
  const [firePreventionOptions, setFirePreventionOptions] = useState<OptionType[]>(DEFAULT_FIRE_PREVENTION_OPTIONS);
  // メタデータ駆動: 用途地域名→コードマッピング（API自動取得用）
  const [useDistrictMap, setUseDistrictMap] = useState<Record<string, string>>(DEFAULT_USE_DISTRICT_MAP);

  const lat = watch('latitude');
  const lng = watch('longitude');
  const hasCoordinates = lat && lng && !isNaN(Number(lat)) && !isNaN(Number(lng));

  // メタデータから選択肢を取得
  useEffect(() => {
    const loadOptions = async () => {
      try {
        // テーブルカラムから選択肢を取得
        const columns = await metadataService.getTableColumnsWithLabels('land_info');

        // 用途地域の選択肢（共通パース関数を使用）
        const useDistrictCol = columns.find(c => c.column_name === 'use_district');
        if (useDistrictCol?.options) {
          const opts = parseOptions(useDistrictCol.options);
          setUseDistrictOptions(opts);
          // 用途地域名→コードマッピングを生成（API自動取得用）
          const map: Record<string, string> = {};
          opts.forEach(opt => { map[opt.label] = opt.value; });
          setUseDistrictMap(map);
        }

        // 都市計画の選択肢（共通パース関数を使用）
        const cityPlanningCol = columns.find(c => c.column_name === 'city_planning');
        if (cityPlanningCol?.options) {
          const opts = parseOptions(cityPlanningCol.options);
          setCityPlanningOptions(opts);
        }

        // 防火地域の選択肢（マスタオプションから取得）
        const firePreventionOpts = await metadataService.getOptionsByCategory('fire_prevention');
        if (firePreventionOpts.length > 0) {
          setFirePreventionOptions(firePreventionOpts);
        }
      } catch (error) {
        console.error('メタデータ取得エラー:', error);
      }
    };
    loadOptions();
  }, []);

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
        `${API_BASE_URL}${API_PATHS.REINFOLIB.REGULATIONS}?lat=${lat}&lng=${lng}`
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

    // 用途地域コードを設定（メタデータ駆動マッピング）
    const zoneName = useArea['用途地域'] || '';
    const useDistrictCode = useDistrictMap[zoneName];
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
  }, [regulationData, setValue, useDistrictMap]);

  // 複数選択の値をパース
  const parseMultiValue = (value: any): string[] => {
    if (!value) return [];
    if (Array.isArray(value)) return value.map(String);
    if (typeof value === 'string') {
      try {
        const parsed = JSON.parse(value);
        if (Array.isArray(parsed)) return parsed.map(String);
      } catch {
        return value.split(',').filter(Boolean);
      }
    }
    return [String(value)];
  };

  // 複数選択用のreact-selectスタイル
  const selectStyles = {
    control: (base: any) => ({
      ...base,
      minHeight: '38px',
      borderColor: '#D1D5DB',
      '&:hover': { borderColor: '#9CA3AF' },
    }),
    multiValue: (base: any) => ({
      ...base,
      backgroundColor: '#E5E7EB',
    }),
    multiValueLabel: (base: any) => ({
      ...base,
      color: '#374151',
    }),
  };

  return (
    <div>
      {/* MAP表示（座標がある場合）*/}
      {hasCoordinates && (
        <RegulationMap lat={Number(lat)} lng={Number(lng)} />
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

      {/* 自動取得・登録ボタン */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginTop: '16px',
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

      {/* 手動編集フォーム */}
      <div style={{
        padding: '16px',
        backgroundColor: '#F9FAFB',
        borderRadius: '8px',
        marginBottom: '16px',
        border: '1px solid #E5E7EB',
      }}>
        <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px', color: '#374151' }}>
          法令制限情報（手動編集可）
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {/* 用途地域（複数選択） */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              用途地域
            </label>
            <Controller
              name="use_district"
              control={control}
              render={({ field }) => {
                const currentValues = parseMultiValue(field.value);
                const selectedOptions = useDistrictOptions.filter(opt =>
                  currentValues.includes(opt.value)
                );
                return (
                  <Select
                    isMulti
                    options={useDistrictOptions}
                    value={selectedOptions}
                    onChange={(selected) => {
                      const values = selected ? selected.map((s: OptionType) => s.value) : [];
                      field.onChange(values.length > 0 ? values : null);
                    }}
                    placeholder="選択してください（複数可）"
                    styles={selectStyles}
                    noOptionsMessage={() => '選択肢がありません'}
                  />
                );
              }}
            />
          </div>

          {/* 都市計画（複数選択） */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              都市計画
            </label>
            <Controller
              name="city_planning"
              control={control}
              render={({ field }) => {
                const currentValues = parseMultiValue(field.value);
                const selectedOptions = cityPlanningOptions.filter(opt =>
                  currentValues.includes(opt.value)
                );
                return (
                  <Select
                    isMulti
                    options={cityPlanningOptions}
                    value={selectedOptions}
                    onChange={(selected) => {
                      const values = selected ? selected.map((s: OptionType) => s.value) : [];
                      field.onChange(values.length > 0 ? values : null);
                    }}
                    placeholder="選択してください（複数可）"
                    styles={selectStyles}
                    noOptionsMessage={() => '選択肢がありません'}
                  />
                );
              }}
            />
          </div>

          {/* 建ぺい率 */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              建ぺい率（%）
            </label>
            <input
              type="number"
              step="0.1"
              {...register('building_coverage_ratio')}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #D1D5DB',
                borderRadius: '6px',
                fontSize: '14px',
              }}
              placeholder="例: 60"
            />
          </div>

          {/* 容積率 */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              容積率（%）
            </label>
            <input
              type="number"
              step="0.1"
              {...register('floor_area_ratio')}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #D1D5DB',
                borderRadius: '6px',
                fontSize: '14px',
              }}
              placeholder="例: 200"
            />
          </div>

          {/* 防火地域 */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              防火地域
            </label>
            <Controller
              name="fire_prevention_area"
              control={control}
              render={({ field }) => (
                <Select
                  options={firePreventionOptions}
                  value={firePreventionOptions.find(opt => opt.value === field.value) || null}
                  onChange={(selected) => field.onChange(selected?.value || null)}
                  placeholder="選択してください"
                  isClearable
                  styles={selectStyles}
                />
              )}
            />
          </div>

          {/* 高度地区 */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              高度地区
            </label>
            <input
              type="text"
              {...register('height_district')}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #D1D5DB',
                borderRadius: '6px',
                fontSize: '14px',
              }}
              placeholder="例: 第1種高度地区"
            />
          </div>

          {/* 景観地区 */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 500, color: '#374151', cursor: 'pointer' }}>
              <input
                type="checkbox"
                {...register('landscape_district')}
                style={{ width: '16px', height: '16px' }}
              />
              景観地区
            </label>
          </div>

          {/* 地区計画 */}
          <div>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#374151', marginBottom: '4px' }}>
              地区計画
            </label>
            <input
              type="text"
              {...register('district_plan_name')}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #D1D5DB',
                borderRadius: '6px',
                fontSize: '14px',
              }}
              placeholder="地区計画名を入力"
            />
          </div>
        </div>
      </div>

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
                    <div style={{ fontSize: '12px', fontWeight: 600, color: '#78350F', marginBottom: '8px', borderBottom: '1px solid #FCD34D', paddingBottom: '4px' }}>
                      {category.name}
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px 16px' }}>
                      {category.items.map((item) => (
                        <label
                          key={item}
                          style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '6px',
                            fontSize: '12px',
                            color: '#374151',
                            cursor: 'pointer',
                            padding: '2px 0',
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
    </div>
  );
};

export default RegulationTab;
