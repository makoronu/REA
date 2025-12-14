import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { propertyService } from '../../services/propertyService';
import { Property, PropertySearchParams } from '../../types/property';

const ITEMS_PER_PAGE = 20;

const PropertiesPage = () => {
  const navigate = useNavigate();
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ページネーション
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // 検索・フィルタ
  const [searchText, setSearchText] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // ソート
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchProperties = useCallback(async () => {
    try {
      setLoading(true);
      const params: PropertySearchParams = {
        skip: (currentPage - 1) * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (searchText) params.search = searchText;
      if (filterType) params.property_type = filterType;
      if (filterStatus) params.sales_status = filterStatus;

      const data = await propertyService.getProperties(params);
      setProperties(data);
      setTotalItems(data.length >= ITEMS_PER_PAGE ? (currentPage * ITEMS_PER_PAGE) + 1 : (currentPage - 1) * ITEMS_PER_PAGE + data.length);
    } catch (err) {
      setError('物件データの取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchText, filterType, filterStatus, sortBy, sortOrder]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  const handleEdit = (id: number) => {
    navigate(`/properties/${id}/edit`);
  };

  const handleNew = () => {
    navigate('/properties/new');
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('この物件を削除しますか？')) {
      try {
        await propertyService.deleteProperty(id);
        await fetchProperties();
      } catch (err) {
        console.error('削除に失敗しました:', err);
        alert('削除に失敗しました');
      }
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchProperties();
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const formatPrice = (price?: number) => {
    if (!price) return '-';
    return price.toLocaleString() + '円';
  };

  const getSortIcon = (column: string) => {
    if (sortBy !== column) return '↕';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  if (error) return <div className="text-red-500 text-center py-8">{error}</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">物件一覧</h1>
        <button
          onClick={handleNew}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md transition-colors"
        >
          新規物件登録
        </button>
      </div>

      {/* 検索・フィルタ */}
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">検索</label>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="物件名・物件番号で検索"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="w-40">
            <label className="block text-sm font-medium text-gray-700 mb-1">物件種別</label>
            <select
              value={filterType}
              onChange={(e) => { setFilterType(e.target.value); setCurrentPage(1); }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">すべて</option>
              <option value="【売地】売地">売地</option>
              <option value="【売戸建】中古戸建">中古戸建</option>
              <option value="mansion">マンション</option>
              <option value="revenue">収益物件</option>
            </select>
          </div>
          <div className="w-40">
            <label className="block text-sm font-medium text-gray-700 mb-1">販売状態</label>
            <select
              value={filterStatus}
              onChange={(e) => { setFilterStatus(e.target.value); setCurrentPage(1); }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">すべて</option>
              <option value="準備中">準備中</option>
              <option value="販売中">販売中</option>
              <option value="成約済">成約済</option>
            </select>
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            検索
          </button>
          <button
            type="button"
            onClick={() => { setSearchText(''); setFilterType(''); setFilterStatus(''); setCurrentPage(1); }}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            クリア
          </button>
        </form>
      </div>

      {loading ? (
        <div className="text-center py-8">読み込み中...</div>
      ) : properties.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">物件データがありません</p>
        </div>
      ) : (
        <>
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('id')}
                  >
                    ID {getSortIcon('id')}
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('company_property_number')}
                  >
                    物件番号 {getSortIcon('company_property_number')}
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('property_name')}
                  >
                    物件名 {getSortIcon('property_name')}
                  </th>
                  <th
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('sale_price')}
                  >
                    価格 {getSortIcon('sale_price')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    物件種別
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    販売状態
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    公開状態
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    アクション
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {properties.map((property) => (
                  <tr
                    key={property.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleEdit(property.id)}
                  >
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                      {property.id}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {property.company_property_number || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                      {property.property_name || '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 font-medium">
                      {formatPrice(property.sale_price)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {property.property_type || '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        property.sales_status === '販売中' ? 'bg-green-100 text-green-800' :
                        property.sales_status === '成約済' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {property.sales_status || '未設定'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        property.publication_status === '公開' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {property.publication_status || '非公開'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleEdit(property.id); }}
                        className="text-indigo-600 hover:text-indigo-900 mr-3"
                      >
                        編集
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(property.id); }}
                        className="text-red-600 hover:text-red-900"
                      >
                        削除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ページネーション */}
          <div className="flex items-center justify-between mt-4 bg-white px-4 py-3 rounded-lg shadow">
            <div className="text-sm text-gray-700">
              {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} 件表示
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
                className="px-3 py-1 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                最初
              </button>
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-1 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                前へ
              </button>
              <span className="px-3 py-1">
                {currentPage} / {totalPages || 1}
              </span>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={properties.length < ITEMS_PER_PAGE}
                className="px-3 py-1 rounded border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                次へ
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default PropertiesPage;
