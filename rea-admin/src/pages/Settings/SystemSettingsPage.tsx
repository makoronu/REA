import React, { useState, useEffect } from 'react';
import { API_PATHS } from '../../constants/apiPaths';
import ErrorBanner from '../../components/ErrorBanner';
import { api } from '../../services/api';

interface Setting {
  key: string;
  value: string | null;
  description: string | null;
  is_set: boolean;
  updated_at: string | null;
}

interface EditingState {
  [key: string]: string;
}

export const SystemSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [editing, setEditing] = useState<EditingState>({});
  const [saving, setSaving] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setIsLoading(true);
      const response = await api.get(API_PATHS.SETTINGS.LIST);
      setSettings(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || (err instanceof Error ? err.message : '不明なエラー'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (key: string) => {
    const value = editing[key];
    if (value === undefined || value === '') {
      setError('値を入力してください');
      return;
    }

    setSaving(key);
    setError(null);

    try {
      await api.put(API_PATHS.SETTINGS.detail(key), { value });

      setSuccessMessage('設定を保存しました');

      // 編集状態をクリアして再取得
      setEditing(prev => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
      fetchSettings();
    } catch (err: any) {
      setError(err.response?.data?.detail || (err instanceof Error ? err.message : '不明なエラー'));
    } finally {
      setSaving(null);
    }
  };

  const handleCancel = (key: string) => {
    setEditing(prev => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  };

  const handleEdit = (key: string) => {
    setEditing(prev => ({ ...prev, [key]: '' }));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">システム設定</h1>
        <p className="mt-1 text-sm text-gray-600">
          外部APIキーなどのシステム設定を管理します
        </p>
      </div>

      {/* エラー/成功メッセージ */}
      {error && (
        <ErrorBanner type="error" message={error} onClose={() => setError(null)} />
      )}
      {successMessage && (
        <ErrorBanner type="success" message={successMessage} onClose={() => setSuccessMessage(null)} />
      )}

      {/* 設定カード一覧 */}
      <div className="space-y-4">
        {settings.map(setting => (
          <div
            key={setting.key}
            className="bg-white rounded-lg shadow-md p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{setting.key}</h3>
                <p className="text-sm text-gray-500">{setting.description}</p>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                setting.is_set ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
              }`}>
                {setting.is_set ? '設定済み' : '未設定'}
              </span>
            </div>

            {/* 現在値表示 */}
            {setting.is_set && !editing[setting.key] && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">現在値（マスク表示）</label>
                <div className="flex items-center gap-2">
                  <code className="bg-gray-100 px-3 py-2 rounded text-sm font-mono flex-1">
                    {setting.value}
                  </code>
                </div>
                {setting.updated_at && (
                  <p className="text-xs text-gray-400 mt-1">
                    最終更新: {new Date(setting.updated_at).toLocaleString('ja-JP')}
                  </p>
                )}
              </div>
            )}

            {/* 編集フォーム */}
            {editing[setting.key] !== undefined ? (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    新しい値
                  </label>
                  <input
                    type="password"
                    value={editing[setting.key]}
                    onChange={(e) => setEditing(prev => ({ ...prev, [setting.key]: e.target.value }))}
                    placeholder="APIキーを入力"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSave(setting.key)}
                    disabled={saving === setting.key}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {saving === setting.key ? (
                      <>
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        保存中...
                      </>
                    ) : (
                      '保存'
                    )}
                  </button>
                  <button
                    onClick={() => handleCancel(setting.key)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                  >
                    キャンセル
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => handleEdit(setting.key)}
                className="px-4 py-2 border border-blue-300 text-blue-600 rounded-md hover:bg-blue-50"
              >
                {setting.is_set ? '値を変更' : '値を設定'}
              </button>
            )}
          </div>
        ))}
      </div>

      {settings.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          設定項目がありません
        </div>
      )}
    </div>
  );
};

export default SystemSettingsPage;
