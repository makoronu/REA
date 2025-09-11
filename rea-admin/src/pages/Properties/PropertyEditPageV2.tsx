import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { propertyFullService } from '../../services/propertyFullService';
import { PropertyFullData } from '../../types/propertyTables.types';
import { PropertyTabs } from '../../components/properties/PropertyTabs';

const PropertyEditPageV2 = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id;
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<PropertyFullData>({
    main: {
      id: 0,
      company_property_number: '',
      building_property_name: '',
      property_type: '',
      status: '',
    },
    contract: {
      property_id: 0,
      contractor_company_name: '',
      contractor_contact_person: '',
      contractor_phone: '',
      contractor_email: '',
    }
  });

  useEffect(() => {
    if (!isNew) {
      fetchPropertyData();
    }
  }, [id]);

  const fetchPropertyData = async () => {
    try {
      setLoading(true);
      const data = await propertyFullService.getPropertyFullData(Number(id));
      setFormData(data);
    } catch (err) {
      setError('物件データの取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      if (isNew) {
        await propertyFullService.createPropertyFullData(formData);
      } else {
        await propertyFullService.updatePropertyFullData(Number(id), formData);
      }
      navigate('/properties');
    } catch (err) {
      setError('保存に失敗しました');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center py-8">読み込み中...</div>;
  if (error) return <div className="text-red-500 text-center py-8">{error}</div>;

  return (
    <div className="max-w-7xl mx-auto px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          {isNew ? '新規物件登録' : '物件編集'}
        </h1>
      </div>

      <PropertyTabs data={formData} onChange={setFormData} />

      <div className="mt-8 flex justify-end space-x-4">
        <button
          onClick={() => navigate('/properties')}
          className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          キャンセル
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {saving ? '保存中...' : '保存'}
        </button>
      </div>
    </div>
  );
};

export default PropertyEditPageV2;
