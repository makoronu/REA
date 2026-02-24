import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PropertyFullForm } from '../../components/form/DynamicForm';
import { propertyService } from '../../services/propertyService';
import { Property } from '../../types/property';
import { MESSAGE_TIMEOUT_MS, SALES_STATUS, PUBLICATION_STATUS, TAX_TYPE, PRICE_STATUS } from '../../constants';
import ErrorBanner from '../../components/ErrorBanner';

export const PropertyEditDynamicPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';

  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState(!isNew);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [errorDetail, setErrorDetail] = useState<{ detail: string; traceback?: string; path?: string } | null>(null);
  const [showErrorDetail, setShowErrorDetail] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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

  // 画像保存処理
  const saveImages = async (propertyId: number, images: any[]) => {
    if (!images || images.length === 0) return;

    // 新規画像（Fileオブジェクトを持つもの）
    const newImages = images.filter((img) => img.file instanceof File);
    // 既存画像（idを持ち、Fileオブジェクトを持たないもの）
    const existingImages = images.filter((img) => img.id && !(img.file instanceof File));

    // 新規画像をアップロード
    if (newImages.length > 0) {
      const uploadData = newImages.map((img) => ({
        file: img.file,
        image_type: img.image_type || '0',
        display_order: img.display_order || 1,
        caption: img.caption || '',
        is_public: img.is_public !== false,
      }));
      await propertyService.uploadImages(propertyId, uploadData);
    }

    // 既存画像のメタデータを一括更新
    if (existingImages.length > 0) {
      const updateData = existingImages.map((img) => ({
        id: img.id,
        image_type: img.image_type,
        display_order: img.display_order,
        caption: img.caption,
        is_public: img.is_public,
      }));
      await propertyService.bulkUpdateImages(propertyId, updateData);
    }
  };

  // フォーム送信ハンドラー
  const handleSubmit = async (data: any) => {
    setSaveStatus('saving');
    setError(null);

    // 画像データを分離
    const { property_images, ...propertyData } = data;

    try {
      if (isNew) {
        // 新規作成
        const created = await propertyService.createProperty(propertyData);

        // 画像保存（物件作成後）
        if (property_images && property_images.length > 0) {
          await saveImages(created.id, property_images);
        }

        setSaveStatus('saved');

        // 作成後は編集モードに遷移
        setTimeout(() => {
          navigate(`/properties/${created.id}/edit`);
        }, 500);
      } else {
        // 更新（APIレスポンスでpropertyを更新、連動ロジックの反映）
        const updated = await propertyService.updateProperty(parseInt(id!), propertyData);

        // 画像保存
        if (property_images) {
          await saveImages(parseInt(id!), property_images);
        }

        setProperty(updated);
        setSaveStatus('saved');

        // 成功メッセージを表示
        setTimeout(() => {
          setSaveStatus('idle');
        }, MESSAGE_TIMEOUT_MS);
      }
    } catch (err: any) {
      setSaveStatus('error');
      console.error('Save error:', err);

      // エラーレスポンスの解析
      const responseData = err.response?.data;
      const detail = responseData?.detail;

      // 公開バリデーションエラー（グループ付き）の場合は再スロー
      if (detail && typeof detail === 'object' && detail.groups) {
        // DynamicFormでキャッチして表示するために再スロー
        throw {
          type: 'publication_validation',
          message: detail.message,
          groups: detail.groups,
        };
      }

      // エラー詳細を保存（デバッグ用）
      if (responseData) {
        setErrorDetail({
          detail: typeof detail === 'string' ? detail : (detail?.message || JSON.stringify(detail)),
          traceback: responseData.traceback,
          path: responseData.path,
        });
        setShowErrorDetail(true);
      }

      // 通常のエラー
      const errorMessage = typeof detail === 'string'
        ? detail
        : detail?.message || '保存に失敗しました';
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      {/* ヘッダー */}
      <div className="mb-4">
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

      {/* エラー詳細モーダル（デバッグ用） */}
      {showErrorDetail && errorDetail && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden">
            <div className="bg-red-600 text-white px-4 py-3 flex justify-between items-center">
              <h3 className="font-bold flex items-center gap-2">
                <svg className="h-5 w-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                保存エラー
              </h3>
              <button
                onClick={() => setShowErrorDetail(false)}
                className="text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {/* エラーメッセージ */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">エラー内容</label>
                <div className="bg-red-50 border border-red-200 rounded p-3 text-red-800 text-sm font-mono whitespace-pre-wrap select-all">
                  {errorDetail.detail}
                </div>
              </div>

              {/* パス */}
              {errorDetail.path && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">API Path</label>
                  <div className="bg-gray-50 border border-gray-200 rounded p-2 text-gray-800 text-sm font-mono select-all">
                    {errorDetail.path}
                  </div>
                </div>
              )}

              {/* スタックトレース */}
              {errorDetail.traceback && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">スタックトレース</label>
                  <div className="bg-gray-900 text-green-400 rounded p-3 text-xs font-mono whitespace-pre-wrap overflow-x-auto select-all max-h-64 overflow-y-auto">
                    {errorDetail.traceback}
                  </div>
                </div>
              )}
            </div>
            <div className="bg-gray-50 px-4 py-3 flex justify-end gap-2">
              <button
                onClick={() => {
                  const text = `エラー: ${errorDetail.detail}\n\nPath: ${errorDetail.path || 'N/A'}\n\nTraceback:\n${errorDetail.traceback || 'N/A'}`;
                  navigator.clipboard.writeText(text);
                  setSuccessMessage('クリップボードにコピーしました');
                }}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
              >
                📋 コピー
              </button>
              <button
                onClick={() => setShowErrorDetail(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
              >
                閉じる
              </button>
            </div>
          </div>
        </div>
      )}

      {/* エラー/成功表示 */}
      {error && saveStatus !== 'error' && (
        <ErrorBanner type="error" message={error} onClose={() => setError(null)} />
      )}
      {successMessage && (
        <ErrorBanner type="success" message={successMessage} onClose={() => setSuccessMessage(null)} />
      )}

      {/* 動的フォーム（全タブ統合済み） */}
      <div className="bg-white shadow rounded-lg p-3">
        <PropertyFullForm
          key={isNew ? 'new' : `edit-${id}-${property ? 'loaded' : 'loading'}`}
          onSubmit={handleSubmit}
          defaultValues={property || {
            sales_status: SALES_STATUS.PREPARING,
            publication_status: PUBLICATION_STATUS.PRIVATE,
            price_status: PRICE_STATUS.FIXED,
            tax_type: TAX_TYPE.TAX_INCLUDED,
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
