import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import ErrorBanner from './ErrorBanner';

interface ImageFile {
  id: string;
  file?: File;
  url: string;
  status: 'uploading' | 'uploaded' | 'error';
  progress?: number;
  error?: string;
}

interface ImageUploaderProps {
  propertyId?: number;
  images: string[];
  onImageUpload: (files: File[]) => Promise<string[]>;
  onImageDelete?: (imageUrl: string) => Promise<void>;
  onImagesChange: (images: string[]) => void;
  maxImages?: number;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  propertyId: _propertyId,
  images = [],
  onImageUpload,
  onImageDelete,
  onImagesChange,
  maxImages = 30
}) => {
  const [imageFiles, setImageFiles] = useState<ImageFile[]>(() => 
    images.map((url, index) => ({
      id: `existing-${index}`,
      url,
      status: 'uploaded' as const
    }))
  );
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [bannerMessage, setBannerMessage] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  // 画像アップロード処理
  const handleImageUpload = useCallback(async (acceptedFiles: File[]) => {
    // 最大枚数チェック
    if (imageFiles.length + acceptedFiles.length > maxImages) {
      setBannerMessage({ type: 'error', text: `画像は最大${maxImages}枚までアップロードできます` });
      return;
    }

    // プレビュー用の一時データを作成
    const newImageFiles: ImageFile[] = acceptedFiles.map((file) => ({
      id: `temp-${Date.now()}-${Math.random()}`,
      file,
      url: URL.createObjectURL(file),
      status: 'uploading' as const,
      progress: 0
    }));

    setImageFiles(prev => [...prev, ...newImageFiles]);

    try {
      // 実際のアップロード処理
      const uploadedUrls = await onImageUpload(acceptedFiles);
      
      // アップロード成功後の処理
      setImageFiles(prev => {
        const updated = [...prev];
        newImageFiles.forEach((tempFile, index) => {
          const fileIndex = updated.findIndex(f => f.id === tempFile.id);
          if (fileIndex !== -1 && uploadedUrls[index]) {
            // 一時URLをクリーンアップ
            if (tempFile.url.startsWith('blob:')) {
              URL.revokeObjectURL(tempFile.url);
            }
            
            updated[fileIndex] = {
              ...updated[fileIndex],
              url: uploadedUrls[index],
              status: 'uploaded',
              progress: 100
            };
          }
        });
        return updated;
      });

      // 親コンポーネントに通知
      const allUploadedUrls = imageFiles
        .filter(img => img.status === 'uploaded')
        .map(img => img.url)
        .concat(uploadedUrls);
      onImagesChange(allUploadedUrls);

    } catch (error) {
      console.error('画像アップロードエラー:', error);
      
      // エラー処理
      setImageFiles(prev => {
        const updated = [...prev];
        newImageFiles.forEach((tempFile) => {
          const fileIndex = updated.findIndex(f => f.id === tempFile.id);
          if (fileIndex !== -1) {
            updated[fileIndex] = {
              ...updated[fileIndex],
              status: 'error',
              error: 'アップロードに失敗しました'
            };
          }
        });
        return updated;
      });
    }
  }, [imageFiles, maxImages, onImageUpload, onImagesChange]);

  // ドラッグ&ドロップ設定
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleImageUpload,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  // 画像削除処理
  const handleImageDelete = async (imageFile: ImageFile) => {
    if (window.confirm('この画像を削除しますか？')) {
      try {
        if (onImageDelete && imageFile.status === 'uploaded') {
          await onImageDelete(imageFile.url);
        }
        
        setImageFiles(prev => prev.filter(img => img.id !== imageFile.id));
        
        const remainingUrls = imageFiles
          .filter(img => img.id !== imageFile.id && img.status === 'uploaded')
          .map(img => img.url);
        onImagesChange(remainingUrls);
        
      } catch (error) {
        console.error('画像削除エラー:', error);
        setBannerMessage({ type: 'error', text: '画像の削除に失敗しました' });
      }
    }
  };

  // ドラッグ&ドロップによる並び替え
  const handleDragStart = (_e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    
    if (draggedIndex === null || draggedIndex === dropIndex) return;

    const draggedImage = imageFiles[draggedIndex];
    const newImages = [...imageFiles];
    
    // 要素を削除して新しい位置に挿入
    newImages.splice(draggedIndex, 1);
    newImages.splice(dropIndex, 0, draggedImage);
    
    setImageFiles(newImages);
    setDraggedIndex(null);

    // 親コンポーネントに通知
    const uploadedUrls = newImages
      .filter(img => img.status === 'uploaded')
      .map(img => img.url);
    onImagesChange(uploadedUrls);
  };

  return (
    <div className="space-y-4">
      {/* メッセージ */}
      {bannerMessage && (
        <ErrorBanner type={bannerMessage.type} message={bannerMessage.text} onClose={() => setBannerMessage(null)} />
      )}
      {/* ドロップゾーン */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
      >
        <input {...getInputProps()} />
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive
            ? 'ここにドロップしてください'
            : 'クリックまたはドラッグ&ドロップで画像をアップロード'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          JPEG, PNG, GIF, WebP（最大10MB、{maxImages}枚まで）
        </p>
      </div>

      {/* 画像一覧 */}
      {imageFiles.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {imageFiles.map((imageFile, index) => (
            <div
              key={imageFile.id}
              className="relative group"
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, index)}
            >
              <div className="aspect-square relative overflow-hidden rounded-lg border border-gray-200">
                <img
                  src={imageFile.url}
                  alt={`画像 ${index + 1}`}
                  className="w-full h-full object-cover"
                />
                
                {/* ステータスオーバーレイ */}
                {imageFile.status === 'uploading' && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="text-white">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
                      <p className="text-xs mt-2">アップロード中...</p>
                    </div>
                  </div>
                )}
                
                {imageFile.status === 'error' && (
                  <div className="absolute inset-0 bg-red-500 bg-opacity-75 flex items-center justify-center">
                    <p className="text-white text-xs text-center px-2">{imageFile.error}</p>
                  </div>
                )}

                {/* 削除ボタン */}
                <button
                  onClick={() => handleImageDelete(imageFile)}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  type="button"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                {/* 順番表示 */}
                <div className="absolute bottom-1 left-1 bg-black bg-opacity-50 text-white text-xs rounded px-1">
                  {index + 1}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-sm text-gray-500">
        {imageFiles.filter(img => img.status === 'uploaded').length}/{maxImages}枚
      </p>
    </div>
  );
};

export default ImageUploader;