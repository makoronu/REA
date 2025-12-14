/**
 * ZOHO CRMインポートページ
 *
 * 機能:
 * - 接続状態確認
 * - OAuth認証
 * - 物件一覧表示
 * - 選択した物件をインポート
 */
import { useState, useEffect } from 'react';
import { zohoService, ZohoStatus, ZohoProperty, ZohoImportResult } from '../../services/zohoService';

export default function ZohoImportPage() {
  // 状態
  const [status, setStatus] = useState<ZohoStatus | null>(null);
  const [properties, setProperties] = useState<ZohoProperty[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [loadingProperties, setLoadingProperties] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<ZohoImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // オプション
  const [updateExisting, setUpdateExisting] = useState(true);
  const [autoGeocode, setAutoGeocode] = useState(true);

  // 初回読み込み
  useEffect(() => {
    loadStatus();
  }, []);

  // 接続状態を取得
  const loadStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const s = await zohoService.getStatus();
      setStatus(s);
      // 接続済みなら物件一覧を取得
      if (s.connected) {
        await loadProperties();
      }
    } catch (e: any) {
      setError(e.message || '接続状態の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // 物件一覧を取得
  const loadProperties = async () => {
    setLoadingProperties(true);
    setError(null);
    try {
      const result = await zohoService.getProperties(1, 100);
      setProperties(result.data || []);
    } catch (e: any) {
      setError(e.message || '物件一覧の取得に失敗しました');
    } finally {
      setLoadingProperties(false);
    }
  };

  // OAuth認証を開始
  const startAuth = async () => {
    try {
      const authUrl = await zohoService.getAuthUrl();
      window.location.href = authUrl;
    } catch (e: any) {
      setError(e.message || '認証URLの取得に失敗しました');
    }
  };

  // 選択切り替え
  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // 全選択/全解除
  const toggleAll = () => {
    if (selectedIds.size === properties.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(properties.map(p => p.id)));
    }
  };

  // インポート実行
  const handleImport = async () => {
    if (selectedIds.size === 0) {
      setError('インポートする物件を選択してください');
      return;
    }

    setImporting(true);
    setError(null);
    setImportResult(null);

    try {
      const result = await zohoService.importProperties({
        zoho_ids: Array.from(selectedIds),
        update_existing: updateExisting,
        auto_geocode: autoGeocode
      });
      setImportResult(result);
      // 成功した物件を選択から外す
      if (result.success > 0) {
        setSelectedIds(new Set());
      }
    } catch (e: any) {
      setError(e.message || 'インポートに失敗しました');
    } finally {
      setImporting(false);
    }
  };

  // 物件表示名を取得
  const getPropertyName = (p: ZohoProperty) => {
    return p.Name || p.name || p.物件名 || `ID: ${p.id}`;
  };

  // 物件価格を取得
  const getPropertyPrice = (p: ZohoProperty) => {
    const price = p.Price || p.price || p.価格 || p.販売価格;
    if (!price) return '-';
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      maximumFractionDigits: 0
    }).format(price);
  };

  // 物件住所を取得
  const getPropertyAddress = (p: ZohoProperty) => {
    return p.Address || p.address || p.住所 || p.所在地 || '-';
  };

  // ローディング中
  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">ZOHO CRM インポート</h1>
        <div className="flex items-center gap-2 text-gray-500">
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          読み込み中...
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold mb-4">ZOHO CRM インポート</h1>

      {/* エラー表示 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* 接続状態 */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-medium">接続状態:</span>
            {status?.connected ? (
              <span className="flex items-center gap-1 text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                接続済み
              </span>
            ) : status?.has_refresh_token ? (
              <span className="flex items-center gap-1 text-yellow-600">
                <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                トークンあり（未接続）
              </span>
            ) : status?.configured ? (
              <span className="flex items-center gap-1 text-red-600">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                未認証
              </span>
            ) : (
              <span className="flex items-center gap-1 text-gray-600">
                <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                未設定
              </span>
            )}
          </div>

          <div className="flex gap-2">
            {!status?.connected && status?.configured && (
              <button
                onClick={startAuth}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                ZOHO認証
              </button>
            )}
            <button
              onClick={loadStatus}
              className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition"
            >
              再接続
            </button>
          </div>
        </div>

        {status?.error && (
          <p className="mt-2 text-sm text-red-600">{status.error}</p>
        )}

        {status?.module_name && (
          <p className="mt-2 text-sm text-gray-500">
            モジュール: {status.module_name}
            {status.module_exists === false && ' (見つかりません)'}
          </p>
        )}
      </div>

      {/* 接続済みの場合のみ表示 */}
      {status?.connected && (
        <>
          {/* 物件一覧 */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-medium">物件一覧 ({properties.length}件)</h2>
              <div className="flex gap-2">
                <button
                  onClick={toggleAll}
                  className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
                >
                  {selectedIds.size === properties.length ? '全解除' : '全選択'}
                </button>
                <button
                  onClick={loadProperties}
                  disabled={loadingProperties}
                  className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                >
                  {loadingProperties ? '読込中...' : '更新'}
                </button>
              </div>
            </div>

            {loadingProperties ? (
              <div className="p-8 text-center text-gray-500">読み込み中...</div>
            ) : properties.length === 0 ? (
              <div className="p-8 text-center text-gray-500">物件がありません</div>
            ) : (
              <div className="border rounded-lg divide-y max-h-96 overflow-y-auto">
                {properties.map(p => (
                  <label
                    key={p.id}
                    className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.has(p.id)}
                      onChange={() => toggleSelect(p.id)}
                      className="w-5 h-5 rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{getPropertyName(p)}</div>
                      <div className="text-sm text-gray-500 truncate">{getPropertyAddress(p)}</div>
                    </div>
                    <div className="text-right text-sm font-medium">
                      {getPropertyPrice(p)}
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* オプション */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium mb-2">オプション</h3>
            <div className="flex flex-wrap gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={updateExisting}
                  onChange={e => setUpdateExisting(e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span>既存物件を更新する</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoGeocode}
                  onChange={e => setAutoGeocode(e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span>位置情報を自動取得</span>
              </label>
            </div>
          </div>

          {/* インポートボタン */}
          <div className="flex items-center gap-4">
            <button
              onClick={handleImport}
              disabled={importing || selectedIds.size === 0}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {importing ? 'インポート中...' : `${selectedIds.size}件をインポート`}
            </button>

            {selectedIds.size > 0 && (
              <span className="text-gray-500">{selectedIds.size}件選択中</span>
            )}
          </div>

          {/* インポート結果 */}
          {importResult && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-2">インポート結果</h3>
              <div className="flex gap-4 text-sm">
                <span className="text-green-600">成功: {importResult.success}件</span>
                <span className="text-red-600">失敗: {importResult.failed}件</span>
                <span className="text-yellow-600">スキップ: {importResult.skipped}件</span>
              </div>
              {importResult.errors.length > 0 && (
                <div className="mt-2">
                  {importResult.errors.map((e, i) => (
                    <p key={i} className="text-sm text-red-600">{e.message}</p>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* 未設定の場合 */}
      {!status?.configured && (
        <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="font-medium text-yellow-800 mb-2">設定が必要です</h3>
          <p className="text-yellow-700 text-sm mb-4">
            ZOHO CRM連携を使用するには、<code className="bg-yellow-100 px-1 rounded">.env</code>ファイルに以下を設定してください：
          </p>
          <pre className="bg-yellow-100 p-3 rounded text-sm overflow-x-auto">
{`ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REDIRECT_URI=http://localhost:8005/api/v1/zoho/callback`}
          </pre>
        </div>
      )}
    </div>
  );
}
