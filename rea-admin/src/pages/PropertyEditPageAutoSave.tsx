import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Property, PropertyFormData } from '../types/property';
import { propertyService } from '../services/propertyService';
import { useAutoSave } from '../hooks/useAutoSave';
import ImageUploader from '../components/ImageUploader';

const PropertyEditPageAutoSave: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<PropertyFormData>({
    title: '',
    price: 0,
    price_unit: '万円',
    is_active: true,
    source: 'manual',
    images: []
  });
  const [propertyId, setPropertyId] = useState<number | null>(id ? parseInt(id) : null);

  // 自動保存の処理関数
  const handleAutoSave = useCallback(async (data: PropertyFormData) => {
    if (!propertyId) {
      // 新規作成の場合、最初の保存で物件を作成
      if (data.title && data.price) {
        const newProperty = await propertyService.createProperty(data);
        setPropertyId(newProperty.id);
        // URLを更新して編集モードに切り替え
        window.history.replaceState(null, '', `/properties/${newProperty.id}/edit`);
      }
    } else {
      // 既存物件の更新
      await propertyService.updatePropertyWithImages(propertyId, data, data.images || []);
    }
  }, [propertyId]);

  // 自動保存フック
  const {
    isSaving,
    lastSaved,
    saveStatus,
    saveError,
    saveImmediately
  } = useAutoSave(formData, {
    onSave: handleAutoSave,
    delay: 1000, // 1秒後に自動保存
    enabled: true
  });

  // 編集モードの場合、既存データを取得
  useEffect(() => {
    if (isEditMode && id) {
      fetchProperty(parseInt(id));
    }
  }, [id, isEditMode]);

  const fetchProperty = async (propertyId: number) => {
    setLoading(true);
    try {
      const property = await propertyService.getProperty(propertyId);
      const { id, created_at, updated_at, ...formData } = property;
      setFormData({
        ...formData,
        images: property.images || []
      });
      setPropertyId(propertyId);
    } catch (error) {
      console.error('物件データの取得に失敗しました:', error);
      alert('物件データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? undefined : parseFloat(value)) : value
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // 画像アップロード処理
  const handleImageUpload = async (files: File[]): Promise<string[]> => {
    if (!propertyId) {
      // 物件がまだ作成されていない場合は、先に作成
      if (formData.title && formData.price) {
        await saveImmediately();
        // propertyIdが設定されるまで少し待つ
        await new Promise(resolve => setTimeout(resolve, 500));
      } else {
        throw new Error('物件名と価格を入力してから画像をアップロードしてください');
      }
    }

    if (propertyId) {
      return await propertyService.uploadImages(propertyId, files);
    }
    
    return [];
  };

  // 画像削除処理
  const handleImageDelete = async (imageUrl: string) => {
    if (propertyId) {
      await propertyService.deleteImage(propertyId, imageUrl);
    }
  };

  // 画像の変更を反映
  const handleImagesChange = (images: string[]) => {
    setFormData(prev => ({
      ...prev,
      images
    }));
  };

  // 保存ステータスの表示
  const renderSaveStatus = () => {
    if (saveStatus === 'saving') {
      return (
        <div className="flex items-center text-blue-600">
          <svg className="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          保存中...
        </div>
      );
    }
    
    if (saveStatus === 'saved' && lastSaved) {
      return (
        <div className="flex items-center text-green-600">
          <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          保存済み（{new Date(lastSaved).toLocaleTimeString()}）
        </div>
      );
    }
    
    if (saveStatus === 'error') {
      return (
        <div className="flex items-center text-red-600">
          <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          保存エラー
        </div>
      );
    }
    
    return null;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">
          {isEditMode ? '物件編集' : '物件新規登録'}
        </h1>
        <div className="flex items-center gap-4">
          {renderSaveStatus()}
          <button
            onClick={() => navigate('/properties')}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            一覧に戻る
          </button>
        </div>
      </div>

      <div className="space-y-6 bg-white rounded-lg shadow p-6">
        {/* 基本情報 */}
        <div className="border-b pb-6">
          <h2 className="text-lg font-semibold mb-4">基本情報</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                物件名 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                価格 <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  name="price"
                  value={formData.price || ''}
                  onChange={handleInputChange}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <select
                  name="price_unit"
                  value={formData.price_unit}
                  onChange={handleInputChange}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="万円">万円</option>
                  <option value="円">円</option>
                  <option value="その他">その他</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                物件種別
              </label>
              <select
                name="property_type"
                value={formData.property_type || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">選択してください</option>
                <option value="マンション">マンション</option>
                <option value="一戸建て">一戸建て</option>
                <option value="土地">土地</option>
                <option value="その他">その他</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                公開中
              </label>
            </div>
          </div>
        </div>

        {/* 画像アップロード */}
        <div className="border-b pb-6">
          <h2 className="text-lg font-semibold mb-4">物件画像</h2>
          <ImageUploader
            propertyId={propertyId || undefined}
            images={formData.images || []}
            onImageUpload={handleImageUpload}
            onImageDelete={handleImageDelete}
            onImagesChange={handleImagesChange}
            maxImages={30}
          />
        </div>

        {/* 元請会社情報 */}
        <div className="border-b pb-6">
          <h2 className="text-lg font-semibold mb-4">元請会社情報</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                会社名
              </label>
              <input
                type="text"
                name="contractor_company_name"
                value={formData.contractor_company_name || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                担当者名
              </label>
              <input
                type="text"
                name="contractor_contact_person"
                value={formData.contractor_contact_person || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                電話番号
              </label>
              <input
                type="tel"
                name="contractor_phone"
                value={formData.contractor_phone || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                メールアドレス
              </label>
              <input
                type="email"
                name="contractor_email"
                value={formData.contractor_email || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                会社住所
              </label>
              <input
                type="text"
                name="contractor_address"
                value={formData.contractor_address || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                宅建免許番号
              </label>
              <input
                type="text"
                name="contractor_license_number"
                value={formData.contractor_license_number || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 物件詳細 */}
        <div className="border-b pb-6">
          <h2 className="text-lg font-semibold mb-4">物件詳細</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                建物面積（㎡）
              </label>
              <input
                type="number"
                name="area_building"
                value={formData.area_building || ''}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                土地面積（㎡）
              </label>
              <input
                type="number"
                name="area_land"
                value={formData.area_land || ''}
                onChange={handleInputChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                間取り
              </label>
              <input
                type="text"
                name="layout"
                value={formData.layout || ''}
                onChange={handleInputChange}
                placeholder="例: 3LDK"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                築年
              </label>
              <input
                type="number"
                name="built_year"
                value={formData.built_year || ''}
                onChange={handleInputChange}
                placeholder="例: 2020"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                最寄り駅
              </label>
              <input
                type="text"
                name="station_name"
                value={formData.station_name || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                徒歩時間（分）
              </label>
              <input
                type="number"
                name="station_walk_time"
                value={formData.station_walk_time || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 住所情報 */}
        <div className="border-b pb-6">
          <h2 className="text-lg font-semibold mb-4">住所情報</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                都道府県
              </label>
              <input
                type="text"
                name="prefecture"
                value={formData.prefecture || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                市区町村
              </label>
              <input
                type="text"
                name="city"
                value={formData.city || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                詳細住所
              </label>
              <input
                type="text"
                name="address"
                value={formData.address || ''}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 物件説明 */}
        <div className="pb-6">
          <h2 className="text-lg font-semibold mb-4">物件説明</h2>
          <textarea
            name="description"
            value={formData.description || ''}
            onChange={handleInputChange}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="物件の特徴や魅力を記入してください"
          />
        </div>

        {/* 情報 */}
        <div className="text-sm text-gray-500">
          <p>※ 入力内容は自動的に保存されます</p>
          {propertyId && <p>物件ID: {propertyId}</p>}
        </div>
      </div>
    </div>
  );
};

export default PropertyEditPageAutoSave;