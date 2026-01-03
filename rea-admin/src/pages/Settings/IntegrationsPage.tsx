import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';

interface Integration {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
  sync_endpoint: string | null;
  icon_class: string | null;
}

interface SyncSummary {
  total_properties: number;
  integrations: {
    code: string;
    name: string;
    is_active: boolean;
    has_endpoint: boolean;
    synced_count: number;
    unsynced_count: number;
  }[];
}

interface SyncStatus {
  property_id: number;
  property_name: string | null;
  integrations: {
    [code: string]: {
      synced: boolean;
      external_id: string | null;
      synced_at: string | null;
      status: string | null;
    };
  };
}

export const IntegrationsPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [summary, setSummary] = useState<SyncSummary | null>(null);
  const [syncStatuses, setSyncStatuses] = useState<SyncStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState<string | null>(null);
  const [selectedProperties, setSelectedProperties] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // データ取得
  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [integrationsRes, summaryRes, statusRes] = await Promise.all([
        fetch(`${API_BASE_URL}${API_PATHS.INTEGRATIONS.LIST}`),
        fetch(`${API_BASE_URL}${API_PATHS.INTEGRATIONS.SYNC_SUMMARY}`),
        fetch(`${API_BASE_URL}${API_PATHS.INTEGRATIONS.SYNC_STATUS}?limit=50`)
      ]);

      if (!integrationsRes.ok || !summaryRes.ok || !statusRes.ok) {
        throw new Error('データの取得に失敗しました');
      }

      const [integrationsData, summaryData, statusData] = await Promise.all([
        integrationsRes.json(),
        summaryRes.json(),
        statusRes.json()
      ]);

      setIntegrations(integrationsData);
      setSummary(summaryData);
      setSyncStatuses(statusData.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // 連携先の有効/無効切り替え
  const handleToggleActive = async (code: string, currentActive: boolean) => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.INTEGRATIONS.detail(code)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentActive })
      });

      if (!response.ok) {
        throw new Error('更新に失敗しました');
      }

      // 再取得
      fetchData();
      setSuccessMessage(`${code}の設定を更新しました`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err.message);
    }
  };

  // 一括同期
  const handleBulkSync = async (integrationCode: string) => {
    if (selectedProperties.length === 0) {
      setError('同期する物件を選択してください');
      return;
    }

    setIsSyncing(integrationCode);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.INTEGRATIONS.BULK_SYNC}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          property_ids: selectedProperties,
          integration_code: integrationCode
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '同期に失敗しました');
      }

      const result = await response.json();
      setSuccessMessage(`同期完了: 成功 ${result.success}件, 失敗 ${result.failed}件`);
      setTimeout(() => setSuccessMessage(null), 5000);

      // 状態を再取得
      fetchData();
      setSelectedProperties([]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSyncing(null);
    }
  };

  // 全選択/解除
  const handleSelectAll = () => {
    if (selectedProperties.length === syncStatuses.length) {
      setSelectedProperties([]);
    } else {
      setSelectedProperties(syncStatuses.map(s => s.property_id));
    }
  };

  // 未同期のみ選択
  const handleSelectUnsynced = (integrationCode: string) => {
    const unsyncedIds = syncStatuses
      .filter(s => !s.integrations[integrationCode]?.synced)
      .map(s => s.property_id);
    setSelectedProperties(unsyncedIds);
  };

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
        <h1 className="text-2xl font-bold text-gray-900">外部連携管理</h1>
        <p className="mt-1 text-sm text-gray-600">
          外部サービスとの連携設定と同期状態を管理します
        </p>
      </div>

      {/* エラー/成功メッセージ */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-700 hover:text-red-900">
            <svg className="h-5 w-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {successMessage && (
        <div className="mb-4 bg-green-50 border border-green-400 text-green-700 px-4 py-3 rounded">
          {successMessage}
        </div>
      )}

      {/* 連携先カード一覧 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {integrations.map(integration => {
          const summaryItem = summary?.integrations.find(i => i.code === integration.code);
          return (
            <div
              key={integration.code}
              className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${
                integration.is_active ? 'border-green-500' : 'border-gray-300'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{integration.name}</h3>
                  <p className="text-sm text-gray-500">{integration.description}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={integration.is_active}
                    onChange={() => handleToggleActive(integration.code, integration.is_active)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {integration.is_active && summaryItem && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">同期済み</span>
                    <span className="font-medium text-green-600">{summaryItem.synced_count}件</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">未同期</span>
                    <span className="font-medium text-orange-600">{summaryItem.unsynced_count}件</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{
                        width: `${summary?.total_properties ? (summaryItem.synced_count / summary.total_properties) * 100 : 0}%`
                      }}
                    ></div>
                  </div>
                </div>
              )}

              {!integration.sync_endpoint && (
                <div className="mt-4 text-sm text-gray-400 italic">
                  同期機能は未実装です
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 物件同期状態テーブル */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">物件同期状態</h2>
          <div className="flex gap-2">
            <button
              onClick={handleSelectAll}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              {selectedProperties.length === syncStatuses.length ? '全解除' : '全選択'}
            </button>
            {integrations.filter(i => i.is_active && i.sync_endpoint).map(integration => (
              <React.Fragment key={integration.code}>
                <button
                  onClick={() => handleSelectUnsynced(integration.code)}
                  className="px-3 py-1 text-sm border border-orange-300 text-orange-600 rounded hover:bg-orange-50"
                >
                  {integration.name}未同期を選択
                </button>
                <button
                  onClick={() => handleBulkSync(integration.code)}
                  disabled={selectedProperties.length === 0 || isSyncing !== null}
                  className="px-4 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isSyncing === integration.code ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      同期中...
                    </>
                  ) : (
                    `${integration.name}に一括同期 (${selectedProperties.length}件)`
                  )}
                </button>
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={selectedProperties.length === syncStatuses.length && syncStatuses.length > 0}
                    onChange={handleSelectAll}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  物件ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  物件名
                </th>
                {integrations.filter(i => i.is_active).map(integration => (
                  <th key={integration.code} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {integration.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {syncStatuses.map(status => (
                <tr key={status.property_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedProperties.includes(status.property_id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedProperties([...selectedProperties, status.property_id]);
                        } else {
                          setSelectedProperties(selectedProperties.filter(id => id !== status.property_id));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {status.property_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {status.property_name || '-'}
                  </td>
                  {integrations.filter(i => i.is_active).map(integration => {
                    const syncInfo = status.integrations[integration.code];
                    return (
                      <td key={integration.code} className="px-6 py-4 whitespace-nowrap text-sm">
                        {syncInfo?.synced ? (
                          <div className="flex items-center">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <svg className="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                              同期済み
                            </span>
                            {syncInfo.synced_at && (
                              <span className="ml-2 text-xs text-gray-400">
                                {new Date(syncInfo.synced_at).toLocaleDateString('ja-JP')}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                            未同期
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {syncStatuses.length === 0 && (
          <div className="px-6 py-8 text-center text-gray-500">
            物件データがありません
          </div>
        )}
      </div>
    </div>
  );
};

export default IntegrationsPage;
