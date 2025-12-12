import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PropertyFullForm } from '../../components/form/DynamicForm';
import { propertyService } from '../../services/propertyService';
import { Property } from '../../types/property';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005';

export const PropertyEditDynamicPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';

  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState(!isNew);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isSettingSchoolDistricts, setIsSettingSchoolDistricts] = useState(false);
  const [isSettingZoning, setIsSettingZoning] = useState(false);

  // 既存データの取得
  useEffect(() => {
    if (!isNew && id) {
      const fetchProperty = async () => {
        try {
          setIsLoading(true);
          const data = await propertyService.getProperty(parseInt(id));
          setProperty(data);
        } catch (err) {
          setError('物件情報の取得に失敗しました');
          console.error(err);
        } finally {
          setIsLoading(false);
        }
      };
      fetchProperty();
    }
  }, [id, isNew]);

  // 学区自動設定
  const handleSetSchoolDistricts = async () => {
    if (!id || isNew) return;

    setIsSettingSchoolDistricts(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/geo/properties/${id}/set-school-districts`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '学区の取得に失敗しました');
      }

      const result = await response.json();

      // プロパティを更新
      setProperty(prev => prev ? {
        ...prev,
        elementary_school: result.elementary_school,
        elementary_school_minutes: result.elementary_school_minutes,
        junior_high_school: result.junior_high_school,
        junior_high_school_minutes: result.junior_high_school_minutes,
      } : null);

      // 成功メッセージ
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);

      // ページをリロードしてフォームを更新
      window.location.reload();
    } catch (err: any) {
      setError(err.message || '学区の取得に失敗しました');
      setSaveStatus('error');
    } finally {
      setIsSettingSchoolDistricts(false);
    }
  };

  // 用途地域自動設定
  const handleSetZoning = async () => {
    if (!id || isNew) return;

    setIsSettingZoning(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/geo/properties/${id}/set-zoning`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '用途地域の取得に失敗しました');
      }

      const result = await response.json();

      // 成功メッセージ
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);

      // 結果を表示（複数の用途地域がある場合）
      if (result.zones && result.zones.length > 1) {
        alert(`複数の用途地域が検出されました:\n${result.zones.map((z: any) => `${z.zone_name}（建ぺい率${z.building_coverage_ratio}%、容積率${z.floor_area_ratio}%）${z.is_primary ? ' ★主' : ''}`).join('\n')}`);
      }

      // ページをリロードしてフォームを更新
      window.location.reload();
    } catch (err: any) {
      setError(err.message || '用途地域の取得に失敗しました');
      setSaveStatus('error');
    } finally {
      setIsSettingZoning(false);
    }
  };

  // フォーム送信ハンドラー
  const handleSubmit = async (data: any) => {
    setSaveStatus('saving');
    setError(null);

    try {
      if (isNew) {
        // 新規作成
        const created = await propertyService.createProperty(data);
        setSaveStatus('saved');

        // 作成後は編集モードに遷移
        setTimeout(() => {
          navigate(`/properties/${created.id}/edit`);
        }, 500);
      } else {
        // 更新
        await propertyService.updateProperty(parseInt(id!), data);
        setSaveStatus('saved');

        // 成功メッセージを表示
        setTimeout(() => {
          setSaveStatus('idle');
        }, 3000);
      }
    } catch (err: any) {
      setSaveStatus('error');
      setError(err.response?.data?.detail || '保存に失敗しました');
      console.error('Save error:', err);
    }
  };

  // 保存状態の表示
  const renderSaveStatus = () => {
    switch (saveStatus) {
      case 'saving':
        return (
          <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center">
            <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            保存中...
          </div>
        );
      case 'saved':
        return (
          <div className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg flex items-center">
            <svg className="h-5 w-5 mr-2" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M5 13l4 4L19 7" />
            </svg>
            保存しました
          </div>
        );
      case 'error':
        return (
          <div className="fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg">
            <div className="flex items-center">
              <svg className="h-5 w-5 mr-2" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error || '保存に失敗しました'}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // ローディング表示
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isNew ? '物件新規登録' : '物件編集'}
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              全項目を一括で編集できます
            </p>
          </div>

          <div className="flex items-center space-x-4">
            {/* 用途地域自動取得ボタン */}
            {!isNew && property?.latitude && property?.longitude && (
              <button
                onClick={handleSetZoning}
                disabled={isSettingZoning}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-purple-600 rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:border-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSettingZoning ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    取得中...
                  </>
                ) : (
                  '用途地域を自動取得'
                )}
              </button>
            )}
            {/* 学区自動取得ボタン */}
            {!isNew && property?.latitude && property?.longitude && (
              <button
                onClick={handleSetSchoolDistricts}
                disabled={isSettingSchoolDistricts}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:border-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSettingSchoolDistricts ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    取得中...
                  </>
                ) : (
                  '学区を自動取得'
                )}
              </button>
            )}
            {/* 戻るボタン */}
            <button
              onClick={() => navigate('/properties')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              一覧に戻る
            </button>
          </div>
        </div>
      </div>

      {/* エラー表示 */}
      {error && saveStatus !== 'error' && (
        <div className="mb-4 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* 動的フォーム（全テーブル表示） */}
      <div className="bg-white shadow rounded-lg p-6">
        <PropertyFullForm
          key={isNew ? 'new' : `edit-${id}`}  // 新規/編集切り替え時にフォームをリセット
          onSubmit={handleSubmit}
          defaultValues={property || {
            // 新規登録時のデフォルト値
            sales_status: '準備中',
            publication_status: '非公開',
            price_status: '1',  // ENUM値のキー部分のみ
            tax_type: '税込',
            is_residential: true,
            is_commercial: false,
            is_investment: false,
          }}
          showDebug={false}
          autoSave={!isNew}
        />
      </div>

      {/* 新規登録時のみ保存ボタンを表示 */}
      {isNew && (
        <div className="bg-white shadow rounded-lg p-6 mt-6">
          <button
            onClick={() => {
              // フォームデータを取得してonSubmitを呼ぶ
              const form = document.querySelector('form');
              if (form) {
                form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
              }
            }}
            disabled={saveStatus === 'saving'}
            className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {saveStatus === 'saving' ? '登録中...' : '物件を登録'}
          </button>
        </div>
      )}

      {/* 保存状態の表示 */}
      {renderSaveStatus()}
    </div>
  );
};

// デフォルトエクスポート
export default PropertyEditDynamicPage;
