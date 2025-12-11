/**
 * SelectableListModal - 選択肢リストをモーダル表示する共通コンポーネント
 *
 * 用途:
 * - 周辺施設選択
 * - 最寄駅選択
 * - バス停選択
 * - 学区選択
 *
 * 特徴:
 * - カテゴリ別アコーディオン表示
 * - 検索バー
 * - 選択済みアイテムの横に[×]ボタン（その場で削除可能）
 */

import React, { useState, useMemo } from 'react';

// =============================================================================
// 型定義
// =============================================================================

export interface SelectableItem {
  id: string | number;
  name: string;
  subText?: string;  // 例: "徒歩5分 (400m)"
  category?: string; // カテゴリコード
}

export interface Category {
  code: string;
  name: string;
  icon?: string;
  items: SelectableItem[];
}

interface SelectableListModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  categories: Category[];
  selectedItems: SelectableItem[];
  onAdd: (item: SelectableItem) => void;
  onRemove: (item: SelectableItem) => void;
  searchable?: boolean;
  maxItems?: number;
}

// =============================================================================
// コンポーネント
// =============================================================================

export const SelectableListModal: React.FC<SelectableListModalProps> = ({
  isOpen,
  onClose,
  title,
  categories,
  selectedItems,
  onAdd,
  onRemove,
  searchable = true,
  maxItems,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  // 検索フィルター
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return categories;

    const query = searchQuery.toLowerCase();
    return categories
      .map((cat) => ({
        ...cat,
        items: cat.items.filter(
          (item) =>
            item.name.toLowerCase().includes(query) ||
            (item.subText && item.subText.toLowerCase().includes(query))
        ),
      }))
      .filter((cat) => cat.items.length > 0);
  }, [categories, searchQuery]);

  // アコーディオン開閉
  const toggleCategory = (code: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(code)) {
        next.delete(code);
      } else {
        next.add(code);
      }
      return next;
    });
  };

  // 全て展開
  const expandAll = () => {
    setExpandedCategories(new Set(categories.map((c) => c.code)));
  };

  // 選択済みかどうか
  const isSelected = (item: SelectableItem) => {
    return selectedItems.some((s) => s.id === item.id);
  };

  // 最大件数チェック
  const isMaxReached = maxItems ? selectedItems.length >= maxItems : false;

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          width: '90%',
          maxWidth: '600px',
          maxHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* ヘッダー */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '16px 20px',
            borderBottom: '1px solid #E5E7EB',
          }}
        >
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#1F2937' }}>
            {title}
          </h3>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#9CA3AF',
              padding: '4px',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>

        {/* 検索バー */}
        {searchable && (
          <div style={{ padding: '12px 20px', borderBottom: '1px solid #E5E7EB' }}>
            <input
              type="text"
              placeholder="検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
              }}
            />
          </div>
        )}

        {/* 選択済みアイテム表示 */}
        {selectedItems.length > 0 && (
          <div
            style={{
              padding: '12px 20px',
              borderBottom: '1px solid #E5E7EB',
              backgroundColor: '#F9FAFB',
            }}
          >
            <div
              style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '8px',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>選択済み ({selectedItems.length}{maxItems ? `/${maxItems}` : ''})</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {selectedItems.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 10px',
                    backgroundColor: '#3B82F6',
                    color: '#fff',
                    borderRadius: '6px',
                    fontSize: '13px',
                  }}
                >
                  <span>{item.name}</span>
                  <button
                    onClick={() => onRemove(item)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#fff',
                      cursor: 'pointer',
                      padding: 0,
                      fontSize: '16px',
                      lineHeight: 1,
                      opacity: 0.8,
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* カテゴリ別リスト */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
          {filteredCategories.length === 0 ? (
            <div style={{ padding: '40px 20px', textAlign: 'center', color: '#9CA3AF' }}>
              該当する項目がありません
            </div>
          ) : (
            filteredCategories.map((category) => {
              const isExpanded = expandedCategories.has(category.code);
              return (
                <div key={category.code}>
                  {/* カテゴリヘッダー */}
                  <button
                    onClick={() => toggleCategory(category.code)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px 20px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textAlign: 'left',
                      borderBottom: '1px solid #F3F4F6',
                    }}
                  >
                    <span style={{ fontSize: '14px', fontWeight: 500, color: '#374151' }}>
                      {category.icon && <span style={{ marginRight: '8px' }}>{category.icon}</span>}
                      {category.name}
                      <span style={{ color: '#9CA3AF', fontWeight: 400, marginLeft: '8px' }}>
                        ({category.items.length}件)
                      </span>
                    </span>
                    <span
                      style={{
                        color: '#9CA3AF',
                        transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                        transition: 'transform 0.2s',
                      }}
                    >
                      ▶
                    </span>
                  </button>

                  {/* アイテムリスト */}
                  {isExpanded && (
                    <div style={{ padding: '4px 20px 8px 20px' }}>
                      {category.items.map((item) => {
                        const selected = isSelected(item);
                        return (
                          <button
                            key={item.id}
                            onClick={() => !selected && !isMaxReached && onAdd(item)}
                            disabled={selected || isMaxReached}
                            style={{
                              width: '100%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              padding: '10px 12px',
                              marginBottom: '4px',
                              backgroundColor: selected ? '#EFF6FF' : '#F9FAFB',
                              border: selected ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                              borderRadius: '8px',
                              cursor: selected || isMaxReached ? 'not-allowed' : 'pointer',
                              opacity: selected ? 0.7 : isMaxReached ? 0.5 : 1,
                              textAlign: 'left',
                              transition: 'all 0.15s ease',
                            }}
                          >
                            <div>
                              <div style={{ fontSize: '14px', color: '#1F2937' }}>
                                {item.name}
                                {selected && (
                                  <span
                                    style={{
                                      marginLeft: '8px',
                                      fontSize: '11px',
                                      backgroundColor: '#3B82F6',
                                      color: '#fff',
                                      padding: '2px 6px',
                                      borderRadius: '4px',
                                    }}
                                  >
                                    選択済
                                  </span>
                                )}
                              </div>
                              {item.subText && (
                                <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                                  {item.subText}
                                </div>
                              )}
                            </div>
                            {!selected && !isMaxReached && (
                              <span style={{ color: '#3B82F6', fontSize: '13px' }}>+ 追加</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* フッター */}
        <div
          style={{
            padding: '12px 20px',
            borderTop: '1px solid #E5E7EB',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <button
            onClick={expandAll}
            style={{
              background: 'none',
              border: 'none',
              color: '#6B7280',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            すべて展開
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '10px 24px',
              backgroundColor: '#3B82F6',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
          >
            完了
          </button>
        </div>
      </div>
    </div>
  );
};

// =============================================================================
// 選択済みリスト表示コンポーネント（モーダル外で使用）
// =============================================================================

interface SelectedItemsListProps {
  items: SelectableItem[];
  onRemove: (item: SelectableItem) => void;
  onOpenModal: () => void;
  addButtonLabel?: string;
  emptyMessage?: string;
}

export const SelectedItemsList: React.FC<SelectedItemsListProps> = ({
  items,
  onRemove,
  onOpenModal,
  addButtonLabel = '+ 追加',
  emptyMessage = '未設定',
}) => {
  return (
    <div>
      {items.length === 0 ? (
        <div style={{ color: '#9CA3AF', fontSize: '14px', marginBottom: '8px' }}>
          {emptyMessage}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '8px' }}>
          {items.map((item) => (
            <div
              key={item.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                backgroundColor: '#F9FAFB',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
              }}
            >
              <div>
                <div style={{ fontSize: '14px', color: '#1F2937' }}>{item.name}</div>
                {item.subText && (
                  <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                    {item.subText}
                  </div>
                )}
              </div>
              <button
                onClick={() => onRemove(item)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#EF4444',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  fontSize: '13px',
                  borderRadius: '4px',
                  transition: 'background-color 0.15s',
                }}
              >
                削除
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={onOpenModal}
        style={{
          padding: '8px 16px',
          backgroundColor: '#fff',
          border: '1px dashed #D1D5DB',
          borderRadius: '8px',
          color: '#6B7280',
          fontSize: '14px',
          cursor: 'pointer',
          transition: 'all 0.15s',
          width: '100%',
        }}
      >
        {addButtonLabel}
      </button>
    </div>
  );
};

export default SelectableListModal;
