import { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { propertyService } from '../../services/propertyService';
import { metadataService } from '../../services/metadataService';
import { Property, PropertySearchParams } from '../../types/property';
import { formatPrice } from '../../constants';

// フィルターオプションの型
interface FilterOption {
  value: string;
  label: string;
  group?: string;
}

const ITEMS_PER_PAGE = 20;

// 利用可能なカラム定義
const ALL_COLUMNS = [
  { key: 'id', label: 'ID', sortable: true, width: 80 },
  { key: 'company_property_number', label: '物件番号', sortable: true, width: 100 },
  { key: 'property_name', label: '物件名', sortable: true, width: 300 },
  { key: 'sale_price', label: '価格', sortable: true, width: 120 },
  { key: 'property_type', label: '物件種別', sortable: false, width: 100 },
  { key: 'sales_status', label: '販売状態', sortable: false, width: 100 },
  { key: 'publication_status', label: '公開', sortable: false, width: 80 },
  { key: 'prefecture', label: '都道府県', sortable: false, width: 100 },
  { key: 'city', label: '市区町村', sortable: false, width: 120 },
  { key: 'address_detail', label: '住所', sortable: false, width: 150 },
  { key: 'contractor_company_name', label: '元請会社', sortable: false, width: 150 },
  { key: 'created_at', label: '登録日', sortable: true, width: 120 },
];

const DEFAULT_COLUMNS = ['id', 'company_property_number', 'property_name', 'sale_price', 'property_type', 'sales_status', 'publication_status'];

// ビューの型定義
interface SavedView {
  id: string;
  name: string;
  columns: string[];
  filters: {
    search: string;
    property_type: string;
    sales_status: string;
    publication_status: string;
    price_min: string;
    price_max: string;
  };
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

const VIEWS_STORAGE_KEY = 'rea_property_views';

// デフォルトビュー
const DEFAULT_VIEWS: SavedView[] = [
  {
    id: 'all',
    name: 'すべて',
    columns: DEFAULT_COLUMNS,
    filters: { search: '', property_type: '', sales_status: '', publication_status: '', price_min: '', price_max: '' },
    sortBy: 'id',
    sortOrder: 'desc',
  },
  {
    id: 'selling',
    name: '販売中',
    columns: DEFAULT_COLUMNS,
    filters: { search: '', property_type: '', sales_status: '販売中', publication_status: '', price_min: '', price_max: '' },
    sortBy: 'id',
    sortOrder: 'desc',
  },
  {
    id: 'published',
    name: '公開中',
    columns: DEFAULT_COLUMNS,
    filters: { search: '', property_type: '', sales_status: '', publication_status: '公開', price_min: '', price_max: '' },
    sortBy: 'id',
    sortOrder: 'desc',
  },
];

const PropertiesPage = () => {
  const navigate = useNavigate();
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // メタデータ駆動のフィルターオプション
  const [filterOptions, setFilterOptions] = useState<{
    sales_status: FilterOption[];
    publication_status: FilterOption[];
    property_type_simple: FilterOption[];
  }>({
    sales_status: [],
    publication_status: [],
    property_type_simple: [],
  });

  // 物件種別のID→ラベル変換マップ
  const [propertyTypeMap, setPropertyTypeMap] = useState<Record<string, string>>({});

  // ページネーション
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // ビュー管理
  const [views, setViews] = useState<SavedView[]>(() => {
    try {
      const saved = localStorage.getItem(VIEWS_STORAGE_KEY);
      return saved ? JSON.parse(saved) : DEFAULT_VIEWS;
    } catch {
      return DEFAULT_VIEWS;
    }
  });
  const [activeViewId, setActiveViewId] = useState('all');
  const [showViewMenu, setShowViewMenu] = useState(false);
  const [newViewName, setNewViewName] = useState('');

  // 表示カラム
  const [visibleColumns, setVisibleColumns] = useState<string[]>(DEFAULT_COLUMNS);
  const [showColumnPicker, setShowColumnPicker] = useState(false);

  // フィルター
  const [filters, setFilters] = useState({
    search: '',
    property_type: '',
    sales_status: '',
    publication_status: '',
    price_min: '',
    price_max: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  // ソート
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // refs
  const columnPickerRef = useRef<HTMLDivElement>(null);
  const viewMenuRef = useRef<HTMLDivElement>(null);

  // ビュー変更時
  useEffect(() => {
    const view = views.find(v => v.id === activeViewId);
    if (view) {
      setVisibleColumns(view.columns);
      setFilters(view.filters);
      setSortBy(view.sortBy);
      setSortOrder(view.sortOrder);
    }
  }, [activeViewId, views]);

  // ビューをLocalStorageに保存
  useEffect(() => {
    localStorage.setItem(VIEWS_STORAGE_KEY, JSON.stringify(views));
  }, [views]);

  // クリック外で閉じる
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (columnPickerRef.current && !columnPickerRef.current.contains(e.target as Node)) {
        setShowColumnPicker(false);
      }
      if (viewMenuRef.current && !viewMenuRef.current.contains(e.target as Node)) {
        setShowViewMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // フィルターオプションをメタデータから取得
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const options = await metadataService.getFilterOptions();
        setFilterOptions({
          sales_status: options.sales_status || [],
          publication_status: options.publication_status || [],
          property_type_simple: options.property_type_simple || [],
        });
        // 物件種別のID→ラベル変換マップを作成
        const typeMap: Record<string, string> = {};
        (options.property_type_simple || []).forEach((opt: FilterOption) => {
          typeMap[opt.value] = opt.label;
        });
        setPropertyTypeMap(typeMap);
      } catch (err) {
        console.error('フィルターオプション取得エラー:', err);
      }
    };
    loadFilterOptions();
  }, []);

  const fetchProperties = useCallback(async () => {
    try {
      setLoading(true);
      const params: PropertySearchParams = {
        skip: (currentPage - 1) * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (filters.search) params.search = filters.search;
      if (filters.property_type) params.property_type = filters.property_type;
      if (filters.sales_status) params.sales_status = filters.sales_status;
      if (filters.publication_status) params.publication_status = filters.publication_status;
      if (filters.price_min) params.sale_price_min = parseFloat(filters.price_min) * 10000;
      if (filters.price_max) params.sale_price_max = parseFloat(filters.price_max) * 10000;

      const data = await propertyService.getProperties(params);
      setProperties(data);
      setTotalItems(data.length >= ITEMS_PER_PAGE ? (currentPage * ITEMS_PER_PAGE) + 1 : (currentPage - 1) * ITEMS_PER_PAGE + data.length);
    } catch (err) {
      setError('物件データの取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, filters, sortBy, sortOrder]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  const handleEdit = (id: number) => navigate(`/properties/${id}/edit`);
  const handleNew = () => navigate('/properties/new');

  // HOMES CSV出力
  const [exporting, setExporting] = useState(false);
  const handleHomesExport = async () => {
    if (properties.length === 0) {
      alert('出力する物件がありません');
      return;
    }

    setExporting(true);
    try {
      const propertyIds = properties.map(p => p.id);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/portal/homes/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ property_ids: propertyIds }),
      });

      if (!response.ok) throw new Error('CSV出力に失敗しました');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `homes_${new Date().toISOString().slice(0,10).replace(/-/g,'')}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('HOMES出力エラー:', err);
      alert('HOMES CSV出力に失敗しました');
    } finally {
      setExporting(false);
    }
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

  const handleSort = (column: string) => {
    const colDef = ALL_COLUMNS.find(c => c.key === column);
    if (!colDef?.sortable) return;

    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  // formatPriceはconstants.tsから import済み
  const formatPriceDisplay = (price?: number) => {
    if (!price) return '-';
    return formatPrice(price);
  };

  const formatDate = (date?: string) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('ja-JP');
  };

  const getCellValue = (property: Property, key: string) => {
    switch (key) {
      case 'id': return property.id;
      case 'company_property_number': return property.company_property_number || '-';
      case 'property_name': return property.property_name || '-';
      case 'sale_price': return formatPriceDisplay(property.sale_price);
      case 'property_type': {
        // 英語ID（detached等）→日本語ラベル（一戸建て等）に変換
        const typeId = property.property_type?.replace(/【.*?】/, '');
        return typeId ? (propertyTypeMap[typeId] || typeId) : '-';
      }
      case 'sales_status': return property.sales_status || '未設定';
      case 'publication_status': return property.publication_status === '公開' ? '公開' : '非公開';
      case 'prefecture': return property.prefecture || '-';
      case 'city': return property.city || '-';
      case 'address_detail': return property.address_detail || '-';
      case 'contractor_company_name': return property.contractor_company_name || '-';
      case 'created_at': return formatDate(property.created_at);
      default: return '-';
    }
  };

  const getSortIcon = (column: string) => {
    const colDef = ALL_COLUMNS.find(c => c.key === column);
    if (!colDef?.sortable) return null;
    if (sortBy !== column) return <span className="text-gray-300 ml-1">↕</span>;
    return <span className="text-blue-600 ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>;
  };

  const getStatusBadgeClass = (key: string, value: string) => {
    if (key === 'sales_status') {
      if (value === '販売中') return 'bg-green-50 text-green-700';
      if (value === '成約済') return 'bg-blue-50 text-blue-700';
      return 'bg-gray-100 text-gray-600';
    }
    if (key === 'publication_status') {
      if (value === '公開') return 'bg-green-50 text-green-700';
      return 'bg-gray-100 text-gray-600';
    }
    return '';
  };

  // 現在のビューを保存
  const saveCurrentView = () => {
    if (!newViewName.trim()) return;

    const newView: SavedView = {
      id: `custom_${Date.now()}`,
      name: newViewName.trim(),
      columns: visibleColumns,
      filters,
      sortBy,
      sortOrder,
    };

    setViews([...views, newView]);
    setActiveViewId(newView.id);
    setNewViewName('');
    setShowViewMenu(false);
  };

  // ビューを削除
  const deleteView = (viewId: string) => {
    if (DEFAULT_VIEWS.some(v => v.id === viewId)) return; // デフォルトは削除不可
    setViews(views.filter(v => v.id !== viewId));
    if (activeViewId === viewId) setActiveViewId('all');
  };

  // 現在のビューを更新
  const updateCurrentView = () => {
    if (DEFAULT_VIEWS.some(v => v.id === activeViewId)) return;
    setViews(views.map(v =>
      v.id === activeViewId
        ? { ...v, columns: visibleColumns, filters, sortBy, sortOrder }
        : v
    ));
  };

  // アクティブフィルター数
  const activeFilterCount = [
    filters.search,
    filters.property_type,
    filters.sales_status,
    filters.publication_status,
    filters.price_min,
    filters.price_max,
  ].filter(Boolean).length;

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  const SkeletonRow = () => (
    <tr className="animate-pulse">
      <td className="px-3 py-4"><div className="h-4 w-4 bg-gray-200 rounded"></div></td>
      {visibleColumns.map((_, i) => (
        <td key={i} className="px-4 py-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </td>
      ))}
      <td className="px-4 py-4"><div className="h-4 bg-gray-200 rounded w-16"></div></td>
    </tr>
  );

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-semibold text-[#1A1A1A]">物件一覧</h1>
        <div className="flex gap-3">
          <button
            onClick={handleHomesExport}
            disabled={exporting || properties.length === 0}
            className="px-4 py-2.5 bg-emerald-600 text-white rounded-lg font-medium transition-all duration-200 hover:bg-emerald-700 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exporting ? '出力中...' : 'HOMES出力'}
          </button>
          <button
            onClick={handleNew}
            className="px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium transition-all duration-200 hover:bg-blue-700 hover:scale-[1.02] active:scale-[0.98]"
          >
            + 新規登録
          </button>
        </div>
      </div>

      {/* ビュータブ + ツールバー */}
      <div className="bg-white rounded-xl shadow-sm mb-4">
        {/* ビュータブ */}
        <div className="flex items-center border-b border-gray-100 px-2">
          <div className="flex gap-1 overflow-x-auto py-2">
            {views.map(view => (
              <button
                key={view.id}
                onClick={() => { setActiveViewId(view.id); setCurrentPage(1); }}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all
                  ${activeViewId === view.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50'
                  }`}
              >
                {view.name}
              </button>
            ))}
          </div>

          {/* ビューメニュー */}
          <div style={{ position: 'relative', marginLeft: '8px' }} ref={viewMenuRef}>
            <button
              onClick={() => setShowViewMenu(!showViewMenu)}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
              title="ビュー管理"
            >
              <svg style={{ width: '20px', height: '20px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>

            {showViewMenu && (
              <div className="absolute right-0 top-full mt-1 w-64 bg-white rounded-xl shadow-lg border border-gray-200 p-3 z-50">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2">ビューを保存</div>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={newViewName}
                    onChange={(e) => setNewViewName(e.target.value)}
                    placeholder="ビュー名"
                    className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={saveCurrentView}
                    disabled={!newViewName.trim()}
                    className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    保存
                  </button>
                </div>

                {!DEFAULT_VIEWS.some(v => v.id === activeViewId) && (
                  <button
                    onClick={updateCurrentView}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg mb-2"
                  >
                    現在のビューを更新
                  </button>
                )}

                <div className="border-t border-gray-100 pt-2 mt-2">
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-2">カスタムビュー</div>
                  {views.filter(v => !DEFAULT_VIEWS.some(d => d.id === v.id)).map(view => (
                    <div key={view.id} className="flex items-center justify-between px-3 py-2 hover:bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">{view.name}</span>
                      <button
                        onClick={() => deleteView(view.id)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                  {views.filter(v => !DEFAULT_VIEWS.some(d => d.id === v.id)).length === 0 && (
                    <p className="text-sm text-gray-400 px-3 py-2">カスタムビューなし</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ツールバー: 検索 + フィルターチップ + 列選択 */}
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="flex items-center gap-3 flex-wrap">
            {/* 検索 */}
            <div style={{ position: 'relative', flex: '0 0 auto' }}>
              <svg
                style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '16px',
                  height: '16px',
                  color: '#9CA3AF',
                  pointerEvents: 'none',
                }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={filters.search}
                onChange={(e) => { setFilters({ ...filters, search: e.target.value }); setCurrentPage(1); }}
                placeholder="物件名・番号で検索..."
                style={{
                  paddingLeft: '40px',
                  paddingRight: '16px',
                  paddingTop: '8px',
                  paddingBottom: '8px',
                  width: '220px',
                  fontSize: '14px',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  outline: 'none',
                }}
              />
            </div>

            {/* 適用中のフィルターチップ */}
            {filters.property_type && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 10px',
                  fontSize: '13px',
                  backgroundColor: '#EFF6FF',
                  color: '#2563EB',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
                onClick={() => { setFilters({ ...filters, property_type: '' }); setCurrentPage(1); }}
              >
                種別: {propertyTypeMap[filters.property_type] || filters.property_type}
                <span style={{ opacity: 0.6 }}>×</span>
              </span>
            )}
            {filters.sales_status && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 10px',
                  fontSize: '13px',
                  backgroundColor: '#F0FDF4',
                  color: '#16A34A',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
                onClick={() => { setFilters({ ...filters, sales_status: '' }); setCurrentPage(1); }}
              >
                {filters.sales_status}
                <span style={{ opacity: 0.6 }}>×</span>
              </span>
            )}
            {filters.publication_status && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 10px',
                  fontSize: '13px',
                  backgroundColor: '#FEF3C7',
                  color: '#D97706',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
                onClick={() => { setFilters({ ...filters, publication_status: '' }); setCurrentPage(1); }}
              >
                {filters.publication_status}
                <span style={{ opacity: 0.6 }}>×</span>
              </span>
            )}
            {(filters.price_min || filters.price_max) && (
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 10px',
                  fontSize: '13px',
                  backgroundColor: '#FDF2F8',
                  color: '#DB2777',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
                onClick={() => { setFilters({ ...filters, price_min: '', price_max: '' }); setCurrentPage(1); }}
              >
                価格: {filters.price_min || '0'}〜{filters.price_max || '∞'}万
                <span style={{ opacity: 0.6 }}>×</span>
              </span>
            )}

            {/* フィルター追加ボタン */}
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setShowFilters(!showFilters)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  fontSize: '13px',
                  color: '#6B7280',
                  backgroundColor: 'white',
                  border: '1px dashed #D1D5DB',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 150ms',
                }}
              >
                <span style={{ fontSize: '16px' }}>+</span>
                フィルター
              </button>

              {/* フィルターメニュー */}
              {showFilters && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    marginTop: '4px',
                    width: '280px',
                    backgroundColor: 'white',
                    borderRadius: '12px',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
                    border: '1px solid #E5E7EB',
                    padding: '12px',
                    zIndex: 50,
                  }}
                >
                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: '8px' }}>
                    フィルター条件
                  </div>

                  {/* 物件種別（メタデータ駆動） */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>物件種別</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {filterOptions.property_type_simple.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => { setFilters({ ...filters, property_type: filters.property_type === opt.value ? '' : opt.value }); setCurrentPage(1); }}
                          style={{
                            padding: '4px 10px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: filters.property_type === opt.value ? '1px solid #2563EB' : '1px solid #E5E7EB',
                            backgroundColor: filters.property_type === opt.value ? '#EFF6FF' : 'white',
                            color: filters.property_type === opt.value ? '#2563EB' : '#374151',
                            cursor: 'pointer',
                          }}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* ステータス（メタデータ駆動） */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>ステータス</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {filterOptions.sales_status.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => { setFilters({ ...filters, sales_status: filters.sales_status === opt.value ? '' : opt.value }); setCurrentPage(1); }}
                          style={{
                            padding: '4px 10px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: filters.sales_status === opt.value ? '1px solid #16A34A' : '1px solid #E5E7EB',
                            backgroundColor: filters.sales_status === opt.value ? '#F0FDF4' : 'white',
                            color: filters.sales_status === opt.value ? '#16A34A' : '#374151',
                            cursor: 'pointer',
                          }}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 公開状態（メタデータ駆動） */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>公開状態</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {filterOptions.publication_status.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => { setFilters({ ...filters, publication_status: filters.publication_status === opt.value ? '' : opt.value }); setCurrentPage(1); }}
                          style={{
                            padding: '4px 10px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: filters.publication_status === opt.value ? '1px solid #D97706' : '1px solid #E5E7EB',
                            backgroundColor: filters.publication_status === opt.value ? '#FEF3C7' : 'white',
                            color: filters.publication_status === opt.value ? '#D97706' : '#374151',
                            cursor: 'pointer',
                          }}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 価格範囲 */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>価格（万円）</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <input
                        type="number"
                        value={filters.price_min}
                        onChange={(e) => { setFilters({ ...filters, price_min: e.target.value }); setCurrentPage(1); }}
                        placeholder="下限"
                        style={{
                          width: '90px',
                          padding: '6px 10px',
                          fontSize: '13px',
                          border: '1px solid #E5E7EB',
                          borderRadius: '6px',
                        }}
                      />
                      <span style={{ color: '#9CA3AF' }}>〜</span>
                      <input
                        type="number"
                        value={filters.price_max}
                        onChange={(e) => { setFilters({ ...filters, price_max: e.target.value }); setCurrentPage(1); }}
                        placeholder="上限"
                        style={{
                          width: '90px',
                          padding: '6px 10px',
                          fontSize: '13px',
                          border: '1px solid #E5E7EB',
                          borderRadius: '6px',
                        }}
                      />
                    </div>
                  </div>

                  {/* クリアボタン */}
                  {activeFilterCount > 0 && (
                    <button
                      onClick={() => { setFilters({ search: '', property_type: '', sales_status: '', publication_status: '', price_min: '', price_max: '' }); setCurrentPage(1); }}
                      style={{
                        width: '100%',
                        padding: '8px',
                        fontSize: '13px',
                        color: '#EF4444',
                        backgroundColor: '#FEF2F2',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                      }}
                    >
                      すべてクリア
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* 右側: 列選択 */}
            <div style={{ marginLeft: 'auto', position: 'relative' }} ref={columnPickerRef}>
              <button
                onClick={() => setShowColumnPicker(!showColumnPicker)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  fontSize: '13px',
                  color: '#6B7280',
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                <svg style={{ width: '16px', height: '16px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                </svg>
                列
              </button>

              {showColumnPicker && (
                <div style={{
                  position: 'absolute',
                  right: 0,
                  top: '100%',
                  marginTop: '4px',
                  width: '220px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
                  border: '1px solid #E5E7EB',
                  padding: '12px',
                  zIndex: 50,
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: '8px' }}>
                    表示する列
                  </div>
                  <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
                    {ALL_COLUMNS.map(col => (
                      <label
                        key={col.key}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '6px 8px',
                          borderRadius: '4px',
                          cursor: 'pointer',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={visibleColumns.includes(col.key)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setVisibleColumns([...visibleColumns, col.key]);
                            } else {
                              setVisibleColumns(visibleColumns.filter(c => c !== col.key));
                            }
                          }}
                          style={{ accentColor: '#2563EB' }}
                        />
                        <span style={{ fontSize: '13px', color: '#374151' }}>{col.label}</span>
                      </label>
                    ))}
                  </div>
                  <div style={{ borderTop: '1px solid #E5E7EB', paddingTop: '8px', marginTop: '8px', display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => setVisibleColumns(ALL_COLUMNS.map(c => c.key))}
                      style={{ flex: 1, padding: '6px', fontSize: '12px', color: '#6B7280', backgroundColor: '#F3F4F6', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      全選択
                    </button>
                    <button
                      onClick={() => setVisibleColumns(DEFAULT_COLUMNS)}
                      style={{ flex: 1, padding: '6px', fontSize: '12px', color: '#6B7280', backgroundColor: '#F3F4F6', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      リセット
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* テーブル */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-100">
                {visibleColumns.map(key => {
                  const col = ALL_COLUMNS.find(c => c.key === key);
                  if (!col) return null;
                  return (
                    <th
                      key={key}
                      className={`px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap
                        ${col.sortable ? 'cursor-pointer hover:bg-gray-50 select-none' : ''}`}
                      style={{ minWidth: col.width }}
                      onClick={() => handleSort(key)}
                    >
                      <span className="flex items-center">
                        {col.label}
                        {getSortIcon(key)}
                      </span>
                    </th>
                  );
                })}
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => <SkeletonRow key={i} />)
              ) : error ? (
                <tr>
                  <td colSpan={visibleColumns.length + 2} className="px-4 py-16 text-center">
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button onClick={() => fetchProperties()} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">再読み込み</button>
                  </td>
                </tr>
              ) : properties.length === 0 ? (
                <tr>
                  <td colSpan={visibleColumns.length + 2} className="px-4 py-16 text-center text-gray-500">
                    該当する物件がありません
                  </td>
                </tr>
              ) : (
                properties.map((property) => (
                  <tr
                    key={property.id}
                    className="border-b border-gray-50 hover:bg-blue-50/50 cursor-pointer transition-colors"
                    onClick={() => handleEdit(property.id)}
                  >
                    {visibleColumns.map(key => {
                      const value = getCellValue(property, key);
                      const badgeClass = getStatusBadgeClass(key, String(value));

                      return (
                        <td key={key} className="px-4 py-3 text-sm">
                          {badgeClass ? (
                            <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${badgeClass}`}>
                              {value}
                            </span>
                          ) : key === 'property_name' ? (
                            <span className="line-clamp-1 max-w-xs text-gray-900">{value}</span>
                          ) : key === 'sale_price' ? (
                            <span className="font-semibold text-gray-900">{value}</span>
                          ) : (
                            <span className="text-gray-700">{value}</span>
                          )}
                        </td>
                      );
                    })}
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleEdit(property.id); }}
                        className="px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        編集
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(property.id); }}
                        className="px-2 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors ml-1"
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
      </div>

      {/* ページネーション */}
      {!loading && properties.length > 0 && (
        <div className="flex items-center justify-between mt-4 bg-white px-4 py-3 rounded-xl shadow-sm">
          <div className="text-sm text-gray-500">
            {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} 件
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              最初
            </button>
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              前へ
            </button>
            <span className="px-3 py-1.5 text-sm text-gray-500">
              {currentPage} / {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={properties.length < ITEMS_PER_PAGE}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
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
