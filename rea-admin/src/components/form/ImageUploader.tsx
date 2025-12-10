import React, { useState, useRef, useCallback } from 'react';

// 画像種別（使用頻度順に並び替え）
const IMAGE_TYPES = [
  { value: '0', label: '未分類', icon: '📁' },
  { value: '2', label: '外観', icon: '🏠' },
  { value: '5', label: '室内', icon: '🛋️' },
  { value: '1', label: '間取', icon: '📐' },
  { value: '11', label: 'リビング/ダイニング', icon: '🛋️' },
  { value: '12', label: 'キッチン', icon: '🍳' },
  { value: '15', label: '浴室', icon: '🛁' },
  { value: '16', label: 'トイレ', icon: '🚽' },
  { value: '17', label: '洗面', icon: '🪥' },
  { value: '13', label: '寝室', icon: '🛏️' },
  { value: '23', label: '洋室', icon: '🛏️' },
  { value: '24', label: '和室', icon: '🎋' },
  { value: '14', label: '子供部屋', icon: '🧸' },
  { value: '10', label: '玄関', icon: '🚪' },
  { value: '18', label: '収納', icon: '🗄️' },
  { value: '20', label: 'バルコニー', icon: '🌿' },
  { value: '22', label: '駐車場', icon: '🚗' },
  { value: '21', label: 'エントランス', icon: '🏛️' },
  { value: '19', label: '設備', icon: '⚙️' },
  { value: '4', label: '周辺', icon: '🏪' },
  { value: '3', label: '地図', icon: '🗺️' },
  { value: '25', label: '省エネ性能ラベル', icon: '🌱' },
  { value: '9', label: 'その他', icon: '📷' },
];

interface PropertyImage {
  id?: number;
  image_type: string;
  file_path?: string;
  file_url?: string;
  display_order: number;
  caption: string;
  is_public: boolean;
  file?: File;
  preview?: string;
}

interface ImageUploaderProps {
  value: PropertyImage[];
  onChange: (images: PropertyImage[]) => void;
  disabled?: boolean;
  propertyId?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  value = [],
  onChange,
  disabled = false,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length > 0) {
      addImages(files);
    }
  }, [value]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      addImages(Array.from(files));
    }
    e.target.value = '';
  };

  // 一括アップロード：すべて「未分類」で追加
  const addImages = (files: File[]) => {
    const newImages: PropertyImage[] = files.map((file, index) => ({
      image_type: '0', // 未分類
      display_order: value.length + index + 1,
      caption: '',
      is_public: true,
      file,
      preview: URL.createObjectURL(file)
    }));
    onChange([...value, ...newImages]);
  };

  const removeImage = (index: number) => {
    const newImages = [...value];
    const removed = newImages.splice(index, 1)[0];
    if (removed.preview) {
      URL.revokeObjectURL(removed.preview);
    }
    newImages.forEach((img, i) => {
      img.display_order = i + 1;
    });
    onChange(newImages);
  };

  // 即時反映（確定ボタン不要）
  const updateImage = (index: number, updates: Partial<PropertyImage>) => {
    const newImages = [...value];
    newImages[index] = { ...newImages[index], ...updates };
    onChange(newImages);
  };

  const moveImage = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === value.length - 1)
    ) {
      return;
    }
    const newImages = [...value];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newImages[index], newImages[targetIndex]] = [newImages[targetIndex], newImages[index]];
    newImages.forEach((img, i) => {
      img.display_order = i + 1;
    });
    onChange(newImages);
  };

  const getImageTypeLabel = (typeValue: string) => {
    return IMAGE_TYPES.find(t => t.value === typeValue)?.label || '未分類';
  };

  const getImageTypeIcon = (typeValue: string) => {
    return IMAGE_TYPES.find(t => t.value === typeValue)?.icon || '📁';
  };

  // 未分類の画像数
  const unclassifiedCount = value.filter(img => img.image_type === '0' || !img.image_type).length;

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '14px', color: '#374151' }}>
            合計: <strong style={{ color: '#2563eb' }}>{value.length}</strong>件
          </span>
          {unclassifiedCount > 0 && (
            <span style={{ fontSize: '12px', color: '#f59e0b', background: '#fef3c7', padding: '2px 8px', borderRadius: '4px' }}>
              未分類: {unclassifiedCount}件
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            onClick={() => setViewMode('grid')}
            style={{
              padding: '4px 8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              background: viewMode === 'grid' ? '#2563eb' : '#fff',
              color: viewMode === 'grid' ? '#fff' : '#374151',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            グリッド
          </button>
          <button
            type="button"
            onClick={() => setViewMode('list')}
            style={{
              padding: '4px 8px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              background: viewMode === 'list' ? '#2563eb' : '#fff',
              color: viewMode === 'list' ? '#fff' : '#374151',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            リスト
          </button>
          {value.length > 0 && !disabled && (
            <button
              type="button"
              onClick={() => {
                value.forEach(img => {
                  if (img.preview) URL.revokeObjectURL(img.preview);
                });
                onChange([]);
              }}
              style={{
                padding: '4px 8px',
                border: '1px solid #fca5a5',
                borderRadius: '4px',
                background: '#fff',
                color: '#dc2626',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              全削除
            </button>
          )}
        </div>
      </div>

      {/* ドラッグ&ドロップエリア */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        style={{
          padding: '24px',
          border: `2px dashed ${dragOver ? '#2563eb' : '#d1d5db'}`,
          borderRadius: '8px',
          textAlign: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: dragOver ? '#eff6ff' : '#f9fafb',
          transition: 'all 0.2s',
          opacity: disabled ? 0.5 : 1
        }}
      >
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>📸</div>
        <p style={{ color: '#4b5563', marginBottom: '4px', fontSize: '14px' }}>
          画像をドラッグ&ドロップ、またはクリックして選択
        </p>
        <p style={{ color: '#9ca3af', fontSize: '12px' }}>
          複数選択OK / JPEG, PNG, WebP対応 / アップロード後に種別変更可能
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      {/* 画像一覧 */}
      {value.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: viewMode === 'grid'
            ? 'repeat(auto-fill, minmax(180px, 1fr))'
            : '1fr',
          gap: '12px'
        }}>
          {value.map((img, index) => (
            <div
              key={index}
              style={{
                border: img.image_type === '0' ? '2px solid #f59e0b' : '1px solid #e5e7eb',
                borderRadius: '8px',
                overflow: 'hidden',
                background: '#fff',
                display: viewMode === 'list' ? 'flex' : 'block',
                alignItems: viewMode === 'list' ? 'center' : undefined,
                gap: viewMode === 'list' ? '12px' : undefined
              }}
            >
              {/* サムネイル */}
              <div style={{
                position: 'relative',
                width: viewMode === 'list' ? '120px' : '100%',
                minWidth: viewMode === 'list' ? '120px' : undefined,
                aspectRatio: '16/10',
                background: '#f3f4f6'
              }}>
                <img
                  src={img.preview || img.file_url || ''}
                  alt={img.caption || '物件画像'}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover'
                  }}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIxNTAiIGZpbGw9IiNlNWU3ZWIiLz48L3N2Zz4=';
                  }}
                />
                {/* 順番バッジ */}
                <div style={{
                  position: 'absolute',
                  top: '4px',
                  left: '4px',
                  background: 'rgba(0,0,0,0.6)',
                  color: '#fff',
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '4px'
                }}>
                  #{img.display_order}
                </div>
                {/* 公開バッジ */}
                <div style={{
                  position: 'absolute',
                  top: '4px',
                  right: '4px',
                  background: img.is_public ? '#10b981' : '#6b7280',
                  color: '#fff',
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '4px'
                }}>
                  {img.is_public ? '公開' : '非公開'}
                </div>
              </div>

              {/* コントロール */}
              <div style={{
                padding: '8px',
                flex: viewMode === 'list' ? 1 : undefined,
                display: 'flex',
                flexDirection: viewMode === 'list' ? 'row' : 'column',
                gap: '8px',
                alignItems: viewMode === 'list' ? 'center' : undefined,
                flexWrap: viewMode === 'list' ? 'wrap' : undefined
              }}>
                {/* 種別選択（即時反映） */}
                <select
                  value={img.image_type || '0'}
                  onChange={(e) => updateImage(index, { image_type: e.target.value })}
                  disabled={disabled}
                  style={{
                    flex: viewMode === 'list' ? '0 0 150px' : undefined,
                    width: viewMode === 'list' ? undefined : '100%',
                    padding: '4px 8px',
                    fontSize: '12px',
                    border: img.image_type === '0' ? '2px solid #f59e0b' : '1px solid #d1d5db',
                    borderRadius: '4px',
                    background: img.image_type === '0' ? '#fef3c7' : '#fff'
                  }}
                >
                  {IMAGE_TYPES.map(t => (
                    <option key={t.value} value={t.value}>
                      {t.icon} {t.label}
                    </option>
                  ))}
                </select>

                {/* キャプション（即時反映） */}
                <input
                  type="text"
                  placeholder="キャプション（任意）"
                  value={img.caption}
                  onChange={(e) => updateImage(index, { caption: e.target.value })}
                  disabled={disabled}
                  style={{
                    flex: viewMode === 'list' ? 1 : undefined,
                    width: viewMode === 'list' ? undefined : '100%',
                    minWidth: viewMode === 'list' ? '150px' : undefined,
                    padding: '4px 8px',
                    fontSize: '12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '4px'
                  }}
                />

                {/* アクションボタン */}
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <button
                    type="button"
                    onClick={() => moveImage(index, 'up')}
                    disabled={disabled || index === 0}
                    style={{
                      padding: '4px 6px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px',
                      background: '#fff',
                      cursor: index === 0 ? 'not-allowed' : 'pointer',
                      opacity: index === 0 ? 0.3 : 1,
                      fontSize: '12px'
                    }}
                    title="前へ"
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    onClick={() => moveImage(index, 'down')}
                    disabled={disabled || index === value.length - 1}
                    style={{
                      padding: '4px 6px',
                      border: '1px solid #d1d5db',
                      borderRadius: '4px',
                      background: '#fff',
                      cursor: index === value.length - 1 ? 'not-allowed' : 'pointer',
                      opacity: index === value.length - 1 ? 0.3 : 1,
                      fontSize: '12px'
                    }}
                    title="後へ"
                  >
                    ↓
                  </button>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={img.is_public}
                      onChange={(e) => updateImage(index, { is_public: e.target.checked })}
                      disabled={disabled}
                    />
                    公開
                  </label>
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    disabled={disabled}
                    style={{
                      padding: '4px 8px',
                      border: '1px solid #fca5a5',
                      borderRadius: '4px',
                      background: '#fff',
                      color: '#dc2626',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                    title="削除"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 画像がない場合 */}
      {value.length === 0 && (
        <div style={{
          padding: '32px',
          textAlign: 'center',
          color: '#9ca3af',
          border: '1px dashed #e5e7eb',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>🖼️</div>
          <p>まだ画像がありません</p>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
