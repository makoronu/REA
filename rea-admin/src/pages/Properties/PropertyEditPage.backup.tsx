import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { propertyService } from '../../services/propertyService';
import { Property, PropertyFormData } from '../../types/property';

const PropertyEditPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id;
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<PropertyFormData>({
    company_property_number: '',
    property_type: '',
    building_property_name: '',
    postal_code: '',
    address_name: '',
    address_detail_public: '',
    rent_price: undefined,
    building_area: undefined,
    room_count: undefined,
    room_type: '',
    contractor_company_name: '',
    contractor_contact_person: '',
    contractor_phone: '',
    contractor_email: '',
  });

  useEffect(() => {
    if (!isNew) {
      fetchProperty();
    }
  }, [id]);

  const fetchProperty = async () => {
    try {
      setLoading(true);
      const data = await propertyService.getProperty(Number(id));
      setFormData(data);
    } catch (err) {
      setError('物件データの取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? undefined : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      if (isNew) {
        await propertyService.createProperty(formData);
      } else {
        await propertyService.updateProperty(Number(id), formData);
      }
      navigate('/properties');
    } catch (err) {
      setError('保存に失敗しました');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handlePDFImport = () => {
    navigate(`/import/touki?returnTo=/properties/${id || 'new'}/edit`);
  };

  if (loading) return <div className="text-center py-8">読み込み中...</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">
          {isNew ? '新規物件登録' : '物件編集'}
        </h1>
        <button
          onClick={handlePDFImport}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors flex items-center gap-2"
        >
          <span>📄</span>
          登記簿PDFから取込
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-8">
        {/* 基本情報 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">基本情報</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                物件番号
              </label>
              <input
                type="text"
                name="company_property_number"
                value={formData.company_property_number || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                物件種別
              </label>
              <select
                name="property_type"
                value={formData.property_type || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">選択してください</option>
                <option value="アパート">アパート</option>
                <option value="マンション">マンション</option>
                <option value="一戸建て">一戸建て</option>
                <option value="土地">土地</option>
              </select>
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                物件名
              </label>
              <input
                type="text"
                name="building_property_name"
                value={formData.building_property_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 所在地情報 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">所在地情報</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                郵便番号
              </label>
              <input
                type="text"
                name="postal_code"
                value={formData.postal_code || ''}
                onChange={handleChange}
                placeholder="123-4567"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                住所
              </label>
              <input
                type="text"
                name="address_name"
                value={formData.address_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 物件詳細 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">物件詳細</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                賃料・価格（円）
              </label>
              <input
                type="number"
                name="rent_price"
                value={formData.rent_price || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                面積（㎡）
              </label>
              <input
                type="number"
                name="building_area"
                value={formData.building_area || ''}
                onChange={handleChange}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* 元請会社情報 */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">元請会社情報</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                会社名
              </label>
              <input
                type="text"
                name="contractor_company_name"
                value={formData.contractor_company_name || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                担当者名
              </label>
              <input
                type="text"
                name="contractor_contact_person"
                value={formData.contractor_contact_person || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                電話番号
              </label>
              <input
                type="tel"
                name="contractor_phone"
                value={formData.contractor_phone || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                メールアドレス
              </label>
              <input
                type="email"
                name="contractor_email"
                value={formData.contractor_email || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* ボタン */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => navigate('/properties')}
            className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            キャンセル
          </button>
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50"
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PropertyEditPage;