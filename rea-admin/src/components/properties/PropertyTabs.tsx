import { useState } from 'react';
import { PropertyFullData } from '../../types/propertyTables.types';

interface PropertyTabsProps {
  data: PropertyFullData;
  onChange: (data: PropertyFullData) => void;
}

export const PropertyTabs: React.FC<PropertyTabsProps> = ({ data, onChange }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    { label: '基本情報', key: 'main' },
    { label: '契約・元請会社', key: 'contract' },
    { label: '所在地', key: 'location' },
    { label: '価格情報', key: 'pricing' },
    { label: '建物情報', key: 'building' },
  ];

  return (
    <div>
      {/* タブヘッダー */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab, index) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(index)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === index
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* タブコンテンツ */}
      <div className="mt-6">
        {activeTab === 0 && <MainInfoTab data={data} onChange={onChange} />}
        {activeTab === 1 && <ContractTab data={data} onChange={onChange} />}
      </div>
    </div>
  );
};

// 基本情報タブ
const MainInfoTab: React.FC<PropertyTabsProps> = ({ data, onChange }) => {
  const handleChange = (field: string, value: any) => {
    onChange({
      ...data,
      main: { ...data.main, [field]: value }
    });
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">物件番号</label>
        <input
          type="text"
          value={data.main.company_property_number || ''}
          onChange={(e) => handleChange('company_property_number', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">物件名</label>
        <input
          type="text"
          value={data.main.building_property_name || ''}
          onChange={(e) => handleChange('building_property_name', e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
        />
      </div>
    </div>
  );
};

// 契約・元請会社タブ
const ContractTab: React.FC<PropertyTabsProps> = ({ data, onChange }) => {
  const handleChange = (field: string, value: any) => {
    onChange({
      ...data,
      contract: { ...data.contract, [field]: value, property_id: data.main.id }
    });
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-4">元請会社情報</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">会社名</label>
          <input
            type="text"
            value={data.contract?.contractor_company_name || ''}
            onChange={(e) => handleChange('contractor_company_name', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">担当者名</label>
          <input
            type="text"
            value={data.contract?.contractor_contact_person || ''}
            onChange={(e) => handleChange('contractor_contact_person', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">電話番号</label>
          <input
            type="tel"
            value={data.contract?.contractor_phone || ''}
            onChange={(e) => handleChange('contractor_phone', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">メールアドレス</label>
          <input
            type="email"
            value={data.contract?.contractor_email || ''}
            onChange={(e) => handleChange('contractor_email', e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
          />
        </div>
      </div>
    </div>
  );
};

