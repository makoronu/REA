/**
 * 法令制限・ハザード情報パネル
 *
 * 物件の緯度経度から法令制限・ハザード情報を取得・表示
 */
import React, { useState, useEffect, useCallback } from 'react';
import { reinfLibService, AllRegulations } from '../../services/reinfLibService';

interface RegulationPanelProps {
  lat: number | null;
  lng: number | null;
  onDataLoaded?: (data: AllRegulations) => void;
}

// 規制項目の表示設定
const REGULATION_SECTIONS = [
  {
    key: 'use_area' as const,
    title: '用途地域',
    color: 'blue',
    fields: ['用途地域', '建ぺい率', '容積率', '都道府県', '市区町村']
  },
  {
    key: 'fire_prevention' as const,
    title: '防火地域',
    color: 'orange',
    fields: ['防火地域区分']
  },
  {
    key: 'flood' as const,
    title: '洪水浸水想定',
    color: 'cyan',
    fields: ['浸水深', '浸水ランク', '河川名']
  },
  {
    key: 'landslide' as const,
    title: '土砂災害警戒区域',
    color: 'yellow',
    fields: ['区域種別', '現象種別']
  },
  {
    key: 'tsunami' as const,
    title: '津波浸水想定',
    color: 'purple',
    fields: ['浸水深', '浸水ランク']
  },
  {
    key: 'storm_surge' as const,
    title: '高潮浸水想定',
    color: 'teal',
    fields: ['浸水深', '浸水ランク']
  },
  {
    key: 'location_optimization' as const,
    title: '立地適正化計画',
    color: 'green',
    fields: ['区域種別']
  },
  {
    key: 'district_plan' as const,
    title: '地区計画',
    color: 'indigo',
    fields: ['地区計画名']
  },
  {
    key: 'planned_road' as const,
    title: '都市計画道路',
    color: 'red',
    fields: ['道路名', '幅員']
  }
];

export const RegulationPanel: React.FC<RegulationPanelProps> = ({
  lat,
  lng,
  onDataLoaded
}) => {
  const [regulations, setRegulations] = useState<AllRegulations | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRegulations = useCallback(async () => {
    if (!lat || !lng) return;

    setLoading(true);
    setError(null);

    try {
      const response = await reinfLibService.getRegulations(lat, lng);
      setRegulations(response.regulations);
      if (onDataLoaded) {
        onDataLoaded(response.regulations);
      }
    } catch (err) {
      setError('法令制限情報の取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [lat, lng, onDataLoaded]);

  useEffect(() => {
    fetchRegulations();
  }, [fetchRegulations]);

  if (!lat || !lng) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg text-gray-500 text-sm">
        緯度・経度を入力すると、法令制限情報を自動取得します
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
        <p className="text-sm text-gray-500 mt-2">法令制限情報を取得中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 rounded-lg">
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={fetchRegulations}
          className="mt-2 text-sm text-blue-600 hover:underline"
        >
          再取得
        </button>
      </div>
    );
  }

  if (!regulations) {
    return null;
  }

  // ハザードリスクがあるか判定（空オブジェクトもfalse扱い）
  const hasData = (data: RegulationData | null) => data && Object.keys(data).length > 0;
  const hasHazardRisk = hasData(regulations.flood) || hasData(regulations.landslide) ||
    hasData(regulations.tsunami) || hasData(regulations.storm_surge);

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">法令制限・ハザード情報</h3>
        <button
          onClick={fetchRegulations}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          更新
        </button>
      </div>

      {/* リスク警告 */}
      {hasHazardRisk && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-amber-800 font-medium">ハザードリスクあり</span>
          </div>
          <p className="mt-1 text-sm text-amber-700">
            この物件は災害リスクエリアに含まれている可能性があります。詳細は下記をご確認ください。
          </p>
        </div>
      )}

      {/* 規制情報カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {REGULATION_SECTIONS.map(section => {
          const data = regulations[section.key];
          const hasData = data && Object.keys(data).length > 0;

          return (
            <div
              key={section.key}
              className={`p-3 rounded-lg border ${
                hasData
                  ? 'bg-white border-gray-200'
                  : 'bg-gray-50 border-gray-100'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    hasData ? `bg-${section.color}-500` : 'bg-gray-300'
                  }`}
                  style={{
                    backgroundColor: hasData
                      ? getColorHex(section.color)
                      : '#d1d5db'
                  }}
                />
                <span className="font-medium text-sm text-gray-700">
                  {section.title}
                </span>
              </div>

              {hasData ? (
                <dl className="space-y-1">
                  {section.fields.map(field => {
                    const value = data[field];
                    if (!value) return null;
                    return (
                      <div key={field} className="flex text-sm">
                        <dt className="text-gray-500 w-20 flex-shrink-0">{field}</dt>
                        <dd className="text-gray-900">{value}</dd>
                      </div>
                    );
                  })}
                </dl>
              ) : (
                <p className="text-sm text-gray-400">該当なし</p>
              )}
            </div>
          );
        })}
      </div>

      {/* 免責事項 */}
      <p className="text-xs text-gray-400">
        ※ 参考情報です。正確な内容は各市区町村の都市計画課等でご確認ください。
      </p>
    </div>
  );
};

// カラー名からHEXカラーを取得
function getColorHex(color: string): string {
  const colors: Record<string, string> = {
    blue: '#3b82f6',
    orange: '#f97316',
    cyan: '#06b6d4',
    yellow: '#eab308',
    purple: '#a855f7',
    teal: '#14b8a6',
    green: '#22c55e',
    indigo: '#6366f1',
    red: '#ef4444'
  };
  return colors[color] || '#6b7280';
}

export default RegulationPanel;
