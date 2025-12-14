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
    if (price >= 100000000) {
      return (price / 100000000).toFixed(1) + '億円';
    }
    if (price >= 10000) {
      return (price / 10000).toFixed(0) + '万円';
    }
    return price.toLocaleString() + '円';
  };

  const getSortIcon = (column: string) => {
    if (sortBy !== column) return <span className="text-gray-300 ml-1">↕</span>;
    return <span className="text-blue-600 ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>;
  };

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  // スケルトンローディング
  const SkeletonRow = () => (
    <tr className="animate-pulse">
      {[...Array(8)].map((_, i) => (
        <td key={i} className="px-4 py-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </td>
      ))}
    </tr>
  );

  if (error) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => fetchProperties()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            再読み込み
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-semibold text-[#1A1A1A]">物件一覧</h1>
        <button
          onClick={handleNew}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium
            transition-all duration-200 ease-out
            hover:bg-blue-700 hover:scale-[1.02] hover:shadow-md
            active:scale-[0.98]"
        >
          新規物件登録
        </button>
      </div>

      {/* 検索・フィルタ */}
      <div className="bg-white p-6 rounded-xl mb-6 shadow-sm">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm font-medium text-[#6B7280] mb-2">検索</label>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="物件名・物件番号で検索"
              className="w-full px-4 py-3 border border-gray-200 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                transition-all duration-200"
            />
          </div>
          <div className="w-44">
            <label className="block text-sm font-medium text-[#6B7280] mb-2">物件種別</label>
            <select
              value={filterType}
              onChange={(e) => { setFilterType(e.target.value); setCurrentPage(1); }}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500
                transition-all duration-200 bg-white"
            >
              <option value="">すべて</option>
              <option value="売地">売地</option>
              <option value="中古戸建">中古戸建</option>
              <option value="マンション">マンション</option>
              <option value="収益">収益物件</option>
            </select>
          </div>
          <div className="w-44">
            <label className="block text-sm font-medium text-[#6B7280] mb-2">販売状態</label>
            <select
              value={filterStatus}
              onChange={(e) => { setFilterStatus(e.target.value); setCurrentPage(1); }}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500
                transition-all duration-200 bg-white"
            >
              <option value="">すべて</option>
              <option value="準備中">準備中</option>
              <option value="販売中">販売中</option>
              <option value="成約済">成約済</option>
            </select>
          </div>
          <button
            type="submit"
            className="px-6 py-3 bg-[#1A1A1A] text-white rounded-lg font-medium
              transition-all duration-200 ease-out
              hover:bg-gray-800 hover:scale-[1.02]
              active:scale-[0.98]"
          >
            検索
          </button>
          <button
            type="button"
            onClick={() => { setSearchText(''); setFilterType(''); setFilterStatus(''); setCurrentPage(1); }}
            className="px-6 py-3 bg-gray-100 text-[#6B7280] rounded-lg font-medium
              transition-all duration-200 ease-out
              hover:bg-gray-200
              active:scale-[0.98]"
          >
            クリア
          </button>
        </form>
      </div>

      {/* テーブル */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-gray-100">
              <th
                className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider cursor-pointer
                  hover:bg-gray-50 transition-colors select-none"
                onClick={() => handleSort('id')}
              >
                <span className="flex items-center">ID{getSortIcon('id')}</span>
              </th>
              <th
                className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider cursor-pointer
                  hover:bg-gray-50 transition-colors select-none"
                onClick={() => handleSort('company_property_number')}
              >
                <span className="flex items-center">物件番号{getSortIcon('company_property_number')}</span>
              </th>
              <th
                className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider cursor-pointer
                  hover:bg-gray-50 transition-colors select-none"
                onClick={() => handleSort('property_name')}
              >
                <span className="flex items-center">物件名{getSortIcon('property_name')}</span>
              </th>
              <th
                className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider cursor-pointer
                  hover:bg-gray-50 transition-colors select-none"
                onClick={() => handleSort('sale_price')}
              >
                <span className="flex items-center">価格{getSortIcon('sale_price')}</span>
              </th>
              <th className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider">
                物件種別
              </th>
              <th className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider">
                販売状態
              </th>
              <th className="px-4 py-4 text-left text-xs font-semibold text-[#6B7280] uppercase tracking-wider">
                公開
              </th>
              <th className="px-4 py-4 text-right text-xs font-semibold text-[#6B7280] uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => <SkeletonRow key={i} />)
            ) : properties.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-16 text-center text-[#6B7280]">
                  物件データがありません
                </td>
              </tr>
            ) : (
              properties.map((property) => (
                <tr
                  key={property.id}
                  className="border-b border-gray-50 hover:bg-blue-50/50 cursor-pointer
                    transition-colors duration-150"
                  onClick={() => handleEdit(property.id)}
                >
                  <td className="px-4 py-4 text-sm text-[#6B7280]">
                    {property.id}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#1A1A1A] font-medium">
                    {property.company_property_number || '-'}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#1A1A1A] max-w-xs">
                    <span className="line-clamp-1">{property.property_name || '-'}</span>
                  </td>
                  <td className="px-4 py-4 text-sm text-[#1A1A1A] font-semibold">
                    {formatPrice(property.sale_price)}
                  </td>
                  <td className="px-4 py-4 text-sm text-[#6B7280]">
                    {property.property_type?.replace(/【.*?】/, '') || '-'}
                  </td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full
                      ${property.sales_status === '販売中' ? 'bg-green-50 text-green-700' :
                        property.sales_status === '成約済' ? 'bg-blue-50 text-blue-700' :
                        'bg-gray-100 text-gray-600'}`}
                    >
                      {property.sales_status || '未設定'}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full
                      ${property.publication_status === '公開' ? 'bg-green-50 text-green-700' :
                        'bg-gray-100 text-gray-600'}`}
                    >
                      {property.publication_status === '公開' ? '公開' : '非公開'}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleEdit(property.id); }}
                      className="px-3 py-1.5 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded
                        transition-colors duration-150 mr-2"
                    >
                      編集
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(property.id); }}
                      className="px-3 py-1.5 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded
                        transition-colors duration-150"
                    >
                      削除
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ページネーション */}
      {!loading && properties.length > 0 && (
        <div className="flex items-center justify-between mt-6 bg-white px-6 py-4 rounded-xl shadow-sm">
          <div className="text-sm text-[#6B7280]">
            {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} 件表示
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded-lg border border-gray-200 text-sm font-medium
                disabled:opacity-40 disabled:cursor-not-allowed
                hover:bg-gray-50 transition-colors duration-150"
            >
              最初
            </button>
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded-lg border border-gray-200 text-sm font-medium
                disabled:opacity-40 disabled:cursor-not-allowed
                hover:bg-gray-50 transition-colors duration-150"
            >
              前へ
            </button>
            <span className="px-4 py-2 text-sm font-medium text-[#6B7280]">
              {currentPage} / {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={properties.length < ITEMS_PER_PAGE}
              className="px-4 py-2 rounded-lg border border-gray-200 text-sm font-medium
                disabled:opacity-40 disabled:cursor-not-allowed
                hover:bg-gray-50 transition-colors duration-150"
            >
              次へ
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertiesPage;
