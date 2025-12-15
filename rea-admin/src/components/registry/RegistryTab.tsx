/**
 * 登記情報タブ
 * 物件に紐づく登記情報の一覧表示・追加・編集・削除
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Registry, registryService } from '../../services/registryService';
import { RegistryCard } from './RegistryCard';
import { RegistryEditModal } from './RegistryEditModal';

interface RegistryTabProps {
  propertyId: number;
}

export const RegistryTab: React.FC<RegistryTabProps> = ({ propertyId }) => {
  const [registries, setRegistries] = useState<Registry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRegistry, setEditingRegistry] = useState<Registry | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Registry | null>(null);

  // 登記一覧取得
  const fetchRegistries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await registryService.getPropertyRegistries(propertyId);
      setRegistries(data);
    } catch (err) {
      console.error('登記一覧取得エラー:', err);
      setError('登記情報の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [propertyId]);

  useEffect(() => {
    if (propertyId) {
      fetchRegistries();
    }
  }, [propertyId, fetchRegistries]);

  // 追加
  const handleAdd = () => {
    setEditingRegistry(null);
    setIsModalOpen(true);
  };

  // 編集
  const handleEdit = (registry: Registry) => {
    setEditingRegistry(registry);
    setIsModalOpen(true);
  };

  // 削除確認
  const handleDeleteConfirm = (registry: Registry) => {
    setDeleteConfirm(registry);
  };

  // 削除実行
  const handleDelete = async () => {
    if (!deleteConfirm) return;

    try {
      await registryService.deleteRegistry(deleteConfirm.id);
      setRegistries(prev => prev.filter(r => r.id !== deleteConfirm.id));
      setDeleteConfirm(null);
    } catch (err) {
      console.error('削除エラー:', err);
      setError('削除に失敗しました');
    }
  };

  // 保存完了
  const handleSave = (saved: Registry) => {
    setRegistries(prev => {
      const exists = prev.find(r => r.id === saved.id);
      if (exists) {
        return prev.map(r => r.id === saved.id ? saved : r);
      }
      return [...prev, saved];
    });
  };

  // 土地と建物で分類
  const landRegistries = registries.filter(r => r.registry_type === '土地');
  const buildingRegistries = registries.filter(r => r.registry_type === '建物');

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">登記情報</h3>
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          登記を追加
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {registries.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <svg width="48" height="48" className="mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="mt-2 text-gray-500">登記情報がありません</p>
          <button
            onClick={handleAdd}
            className="mt-4 text-blue-600 hover:text-blue-800"
          >
            登記情報を追加
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* 土地 */}
          {landRegistries.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-3">
                土地 ({landRegistries.length}筆)
              </h4>
              <div className="space-y-3">
                {landRegistries.map(registry => (
                  <RegistryCard
                    key={registry.id}
                    registry={registry}
                    onEdit={handleEdit}
                    onDelete={handleDeleteConfirm}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 建物 */}
          {buildingRegistries.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-3">
                建物 ({buildingRegistries.length}棟)
              </h4>
              <div className="space-y-3">
                {buildingRegistries.map(registry => (
                  <RegistryCard
                    key={registry.id}
                    registry={registry}
                    onEdit={handleEdit}
                    onDelete={handleDeleteConfirm}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 編集モーダル */}
      <RegistryEditModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        registry={editingRegistry}
        propertyId={propertyId}
      />

      {/* 削除確認ダイアログ */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="fixed inset-0 bg-black bg-opacity-50"
            onClick={() => setDeleteConfirm(null)}
          />
          <div className="relative bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              登記情報を削除しますか？
            </h3>
            <p className="text-gray-500 mb-4">
              {deleteConfirm.registry_type}: {deleteConfirm.location}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
              >
                キャンセル
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-white bg-red-600 rounded hover:bg-red-700"
              >
                削除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
