import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PropertyFullForm } from '../../components/form/DynamicForm';
import { propertyService } from '../../services/propertyService';
import { Property } from '../../types/property';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';

export const PropertyEditDynamicPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';

  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState(!isNew);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isSyncingToZoho, setIsSyncingToZoho] = useState(false);

  // 既存データの取得（関連テーブル含む）
  useEffect(() => {
    if (!isNew && id) {
      const fetchProperty = async () => {
        try {
          setIsLoading(true);
          // getPropertyFull: properties + building_info + land_info + amenities を全て取得
          const data = await propertyService.getPropertyFull(parseInt(id));
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

  // ZOHOに同期
  const handleSyncToZoho = async () => {
    if (!id || isNew) return;

    setIsSyncingToZoho(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.ZOHO.sync(parseInt(id))}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'ZOHOへの同期に失敗しました');
      }

      const result = await response.json();

      if (result.success > 0) {
        // 成功メッセージ
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 3000);

        if (result.created > 0) {
          alert('ZOHOに新規作成しました');
          // ページをリロードしてzoho_idを反映
          window.location.reload();
        } else {
          alert('ZOHOに同期しました');
        }
      } else {
        throw new Error(result.errors?.[0]?.message || 'ZOHOへの同期に失敗しました');
      }
    } catch (err: any) {
      setError(err.message || 'ZOHOへの同期に失敗しました');
      setSaveStatus('error');
    } finally {
      setIsSyncingToZoho(false);
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
      console.error('Save error:', err);

      // エラーレスポンスの解析
      const errorDetail = err.response?.data?.detail;

      // 公開バリデーションエラー（グループ付き）の場合は再スロー
      if (errorDetail && typeof errorDetail === 'object' && errorDetail.groups) {
        // DynamicFormでキャッチして表示するために再スロー
        throw {
          type: 'publication_validation',
          message: errorDetail.message,
          groups: errorDetail.groups,
        };
      }

      // 通常のエラー
      const errorMessage = typeof errorDetail === 'string'
        ? errorDetail
        : errorDetail?.message || '保存に失敗しました';
      setError(errorMessage);
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
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isNew ? '物件新規登録' : '物件編集'}
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              全項目を一括で編集できます
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2" style={{ flexShrink: 0 }}>
            {/* ZOHOに同期ボタン */}
            {!isNew && (
              <button
                onClick={handleSyncToZoho}
                disabled={isSyncingToZoho}
                className="px-4 py-2 text-sm font-medium text-white bg-orange-600 border border-orange-600 rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:border-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSyncingToZoho ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    同期中...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    ZOHOに同期
                  </>
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

      {/* 動的フォーム（全タブ統合済み） */}
      <div className="bg-white shadow rounded-lg p-6">
        <PropertyFullForm
          key={isNew ? 'new' : `edit-${id}-${property ? 'loaded' : 'loading'}`}
          onSubmit={handleSubmit}
          defaultValues={property || {
            sales_status: '準備中',
            publication_status: '非公開',
            price_status: '1',
            tax_type: '税込',
            is_residential: true,
            is_commercial: false,
            is_investment: false,
          }}
          showDebug={false}
          autoSave={false}
        />
      </div>

      {/* 保存状態の表示 */}
      {renderSaveStatus()}
    </div>
  );
};

// デフォルトエクスポート
export default PropertyEditDynamicPage;
