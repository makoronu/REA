/**
 * 登記情報編集モーダル
 * メタデータ駆動: column_labelsからフォームを自動生成
 */
import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Registry, RegistryMetadata, RegistryMetadataColumn, registryService } from '../../services/registryService';

interface RegistryEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (registry: Registry) => void;
  registry?: Registry | null;
  propertyId: number;
}

export const RegistryEditModal: React.FC<RegistryEditModalProps> = ({
  isOpen,
  onClose,
  onSave,
  registry,
  propertyId
}) => {
  const [formData, setFormData] = useState<Partial<Registry>>({
    registry_type: '土地'
  });
  const [metadata, setMetadata] = useState<RegistryMetadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['基本情報']));

  // メタデータ取得
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setLoading(true);
        const data = await registryService.getMetadata();
        setMetadata(data);
      } catch (err) {
        console.error('メタデータ取得エラー:', err);
        setError('メタデータの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    if (isOpen) {
      fetchMetadata();
    }
  }, [isOpen]);

  // 編集時は既存データをセット
  useEffect(() => {
    if (registry) {
      setFormData({ ...registry });
      // 編集時は関連グループを開く
      const groupsToOpen = new Set(['基本情報']);
      if (registry.registry_type === '土地') {
        groupsToOpen.add('表題部（土地）');
      } else {
        groupsToOpen.add('表題部（建物）');
      }
      if (registry.owner_name) groupsToOpen.add('甲区（所有権）');
      if (registry.mortgage_holder) groupsToOpen.add('乙区（抵当権）');
      setExpandedGroups(groupsToOpen);
    } else {
      setFormData({ registry_type: '土地' });
      setExpandedGroups(new Set(['基本情報', '表題部（土地）']));
    }
  }, [registry, isOpen]);

  const handleChange = (name: string, value: string | number | null) => {
    setFormData(prev => ({ ...prev, [name]: value }));

    // registry_typeが変わったら関連グループを開く
    if (name === 'registry_type') {
      const newGroups = new Set(['基本情報']);
      if (value === '土地') {
        newGroups.add('表題部（土地）');
      } else {
        newGroups.add('表題部（建物）');
      }
      setExpandedGroups(newGroups);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.registry_type) {
      setError('登記種別を選択してください');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      let result: Registry;
      if (registry?.id) {
        result = await registryService.updateRegistry(registry.id, formData);
      } else {
        result = await registryService.createRegistry(propertyId, formData);
      }
      onSave(result);
      onClose();
    } catch (err: unknown) {
      console.error('保存エラー:', err);
      const errorMessage = err instanceof Error ? err.message : '保存に失敗しました';
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(group)) {
        next.delete(group);
      } else {
        next.add(group);
      }
      return next;
    });
  };

  // グループの表示判定
  const shouldShowGroup = (group: string): boolean => {
    const type = formData.registry_type;
    if (group === '表題部（土地）') return type === '土地';
    if (group === '表題部（建物）') return type === '建物';
    if (group === '表題部') return true; // 共通の表題部
    return true;
  };

  // フィールドのレンダリング
  const renderField = (col: RegistryMetadataColumn) => {
    const rawValue = formData[col.name as keyof Registry];
    // 文字列・数値・nullに変換（オブジェクト型は除外）
    const value = typeof rawValue === 'object' ? '' : rawValue;
    const commonClasses = "w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";

    switch (col.type) {
      case 'number':
        return (
          <input
            type="number"
            value={value ?? ''}
            onChange={(e) => handleChange(col.name, e.target.value ? parseFloat(e.target.value) : null)}
            className={commonClasses}
            step="0.01"
          />
        );

      case 'date':
        return (
          <input
            type="date"
            value={String(value ?? '')}
            onChange={(e) => handleChange(col.name, e.target.value || null)}
            className={commonClasses}
          />
        );

      case 'textarea':
        return (
          <textarea
            value={String(value ?? '')}
            onChange={(e) => handleChange(col.name, e.target.value || null)}
            className={`${commonClasses} h-24`}
          />
        );

      case 'select':
        if (col.name === 'registry_type') {
          return (
            <select
              value={String(value ?? '土地')}
              onChange={(e) => handleChange(col.name, e.target.value)}
              className={commonClasses}
            >
              <option value="土地">土地</option>
              <option value="建物">建物</option>
            </select>
          );
        }
        return (
          <input
            type="text"
            value={String(value ?? '')}
            onChange={(e) => handleChange(col.name, e.target.value || null)}
            className={commonClasses}
          />
        );

      default:
        return (
          <input
            type="text"
            value={String(value ?? '')}
            onChange={(e) => handleChange(col.name, e.target.value || null)}
            className={commonClasses}
          />
        );
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, overflowY: 'auto' }}>
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* オーバーレイ */}
        <div
          style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={onClose}
        />

        {/* モーダル本体 */}
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
          {/* ヘッダー */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {registry ? '登記情報を編集' : '登記情報を追加'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* コンテンツ */}
          <div className="px-6 py-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : error ? (
              <div className="bg-red-50 text-red-600 px-4 py-3 rounded mb-4">
                {error}
              </div>
            ) : metadata ? (
              <form onSubmit={handleSubmit}>
                {Object.entries(metadata.groups)
                  .filter(([group]) => shouldShowGroup(group))
                  .map(([group, columns]) => (
                    <div key={group} className="mb-4">
                      {/* グループヘッダー */}
                      <button
                        type="button"
                        onClick={() => toggleGroup(group)}
                        className="w-full flex items-center justify-between py-2 text-left"
                      >
                        <span className="font-medium text-gray-700">{group}</span>
                        <svg
                          width="20"
                          height="20"
                          className={`text-gray-400 transition-transform ${
                            expandedGroups.has(group) ? 'rotate-180' : ''
                          }`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>

                      {/* グループコンテンツ */}
                      {expandedGroups.has(group) && (
                        <div className="pl-4 border-l-2 border-gray-200 space-y-4 mt-2">
                          {columns.map(col => (
                            <div key={col.name}>
                              <label className="block text-sm text-gray-600 mb-1">
                                {col.label}
                                {col.required && <span className="text-red-500 ml-1">*</span>}
                              </label>
                              {renderField(col)}
                              {col.description && (
                                <p className="text-xs text-gray-400 mt-1">{col.description}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
              </form>
            ) : null}
          </div>

          {/* フッター */}
          <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              onClick={handleSubmit}
              disabled={saving}
              className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
