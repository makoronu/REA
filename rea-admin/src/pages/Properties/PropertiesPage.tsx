// Build: 2025-12-25T08 - World-Class Properties Page
import { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { propertyService } from '../../services/propertyService';
import { metadataService } from '../../services/metadataService';
import { Property, PropertySearchParams } from '../../types/property';
import { formatPrice } from '../../constants';

// ============================================
// 型定義
// ============================================
interface FilterOption {
  value: string;
  label: string;
  group?: string;
}

interface ColumnDef {
  key: string;
  label: string;
  sortable: boolean;
  width: number;
  minWidth?: number;
}

interface SavedView {
  id: string;
  name: string;
  columns: string[];
  filters: FilterState;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

interface FilterState {
  search: string;
  property_type: string;
  sales_status: string;
  publication_status: string;
  price_min: string;
  price_max: string;
}

interface ContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  propertyId: number | null;
  property: Property | null;
}

type ViewMode = 'table' | 'card' | 'gallery';
type RowDensity = 'compact' | 'normal' | 'comfortable';

// ============================================
// 定数
// ============================================
const ITEMS_PER_PAGE = 20;
const DEBOUNCE_MS = 300;
const VIEWS_STORAGE_KEY = 'rea_property_views';

const ALL_COLUMNS: ColumnDef[] = [
  { key: 'id', label: 'ID', sortable: true, width: 70, minWidth: 50 },
  { key: 'company_property_number', label: '物件番号', sortable: true, width: 100, minWidth: 80 },
  { key: 'property_name', label: '物件名', sortable: true, width: 280, minWidth: 150 },
  { key: 'sale_price', label: '価格', sortable: true, width: 110, minWidth: 90 },
  { key: 'property_type', label: '種別', sortable: false, width: 90, minWidth: 70 },
  { key: 'sales_status', label: '販売状態', sortable: false, width: 100, minWidth: 80 },
  { key: 'publication_status', label: '公開', sortable: false, width: 70, minWidth: 60 },
  { key: 'prefecture', label: '都道府県', sortable: false, width: 90, minWidth: 70 },
  { key: 'city', label: '市区町村', sortable: false, width: 110, minWidth: 80 },
  { key: 'address_detail', label: '住所', sortable: false, width: 140, minWidth: 100 },
  { key: 'contractor_company_name', label: '元請会社', sortable: false, width: 130, minWidth: 100 },
  { key: 'created_at', label: '登録日', sortable: true, width: 100, minWidth: 80 },
];

const DEFAULT_COLUMNS = ['id', 'company_property_number', 'property_name', 'sale_price', 'property_type', 'sales_status', 'publication_status'];

const DEFAULT_FILTERS: FilterState = {
  search: '',
  property_type: '',
  sales_status: '',
  publication_status: '',
  price_min: '',
  price_max: '',
};

const DEFAULT_VIEWS: SavedView[] = [
  { id: 'all', name: 'すべて', columns: DEFAULT_COLUMNS, filters: DEFAULT_FILTERS, sortBy: 'id', sortOrder: 'desc' },
  { id: 'selling', name: '販売中', columns: DEFAULT_COLUMNS, filters: { ...DEFAULT_FILTERS, sales_status: '販売中' }, sortBy: 'id', sortOrder: 'desc' },
  { id: 'published', name: '公開中', columns: DEFAULT_COLUMNS, filters: { ...DEFAULT_FILTERS, publication_status: '公開' }, sortBy: 'id', sortOrder: 'desc' },
];

const SALES_STATUS_OPTIONS = ['販売中', '成約済', '取下げ', '商談中'];
const PUBLICATION_STATUS_OPTIONS = ['公開', '非公開'];

// ============================================
// ユーティリティ
// ============================================
const useDebounce = <T,>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
};

const formatDate = (date?: string) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('ja-JP');
};

// ============================================
// メインコンポーネント
// ============================================
const PropertiesPage = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // データ状態
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // メタデータ
  const [filterOptions, setFilterOptions] = useState<{
    sales_status: FilterOption[];
    publication_status: FilterOption[];
    property_type_simple: FilterOption[];
  }>({ sales_status: [], publication_status: [], property_type_simple: [] });
  const [propertyTypeMap, setPropertyTypeMap] = useState<Record<string, string>>({});

  // ビュー・表示設定
  const [views, setViews] = useState<SavedView[]>(() => {
    try {
      const saved = localStorage.getItem(VIEWS_STORAGE_KEY);
      return saved ? JSON.parse(saved) : DEFAULT_VIEWS;
    } catch { return DEFAULT_VIEWS; }
  });
  const [activeViewId, setActiveViewId] = useState('all');
  const [visibleColumns, setVisibleColumns] = useState<string[]>(DEFAULT_COLUMNS);
  const [columnWidths] = useState<Record<string, number>>({});
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [rowDensity, setRowDensity] = useState<RowDensity>('normal');

  // フィルター・ソート
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [sortBy, setSortBy] = useState<string>('id');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const debouncedSearch = useDebounce(filters.search, DEBOUNCE_MS);

  // 選択状態
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [lastSelectedIndex, setLastSelectedIndex] = useState<number | null>(null);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);

  // UI状態
  const [showFilters, setShowFilters] = useState(false);
  const [showColumnPicker, setShowColumnPicker] = useState(false);
  const [showViewMenu, setShowViewMenu] = useState(false);
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const [newViewName, setNewViewName] = useState('');
  const [exporting, setExporting] = useState(false);

  // コンテキストメニュー
  const [contextMenu, setContextMenu] = useState<ContextMenuState>({
    visible: false, x: 0, y: 0, propertyId: null, property: null
  });

  // インライン編集
  const [editingCell, setEditingCell] = useState<{ id: number; key: string } | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  // Refs
  const tableRef = useRef<HTMLTableElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // ============================================
  // URL同期
  // ============================================
  useEffect(() => {
    const params: Record<string, string> = {};
    if (filters.search) params.q = filters.search;
    if (filters.property_type) params.type = filters.property_type;
    if (filters.sales_status) params.status = filters.sales_status;
    if (filters.publication_status) params.pub = filters.publication_status;
    if (filters.price_min) params.min = filters.price_min;
    if (filters.price_max) params.max = filters.price_max;
    if (sortBy !== 'id') params.sort = sortBy;
    if (sortOrder !== 'desc') params.order = sortOrder;
    if (currentPage > 1) params.page = currentPage.toString();

    setSearchParams(params, { replace: true });
  }, [filters, sortBy, sortOrder, currentPage, setSearchParams]);

  // URLからフィルター復元
  useEffect(() => {
    const q = searchParams.get('q') || '';
    const type = searchParams.get('type') || '';
    const status = searchParams.get('status') || '';
    const pub = searchParams.get('pub') || '';
    const min = searchParams.get('min') || '';
    const max = searchParams.get('max') || '';
    const sort = searchParams.get('sort') || 'id';
    const order = (searchParams.get('order') || 'desc') as 'asc' | 'desc';
    const page = parseInt(searchParams.get('page') || '1', 10);

    setFilters({ search: q, property_type: type, sales_status: status, publication_status: pub, price_min: min, price_max: max });
    setSortBy(sort);
    setSortOrder(order);
    setCurrentPage(page);
  }, []); // 初回のみ

  // ============================================
  // データ取得
  // ============================================
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const options = await metadataService.getFilterOptions();
        setFilterOptions({
          sales_status: options.sales_status || [],
          publication_status: options.publication_status || [],
          property_type_simple: options.property_type_simple || [],
        });
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
      setError(null);
      const params: PropertySearchParams = {
        skip: (currentPage - 1) * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (debouncedSearch) params.search = debouncedSearch;
      if (filters.property_type) params.property_type = filters.property_type;
      if (filters.sales_status) params.sales_status = filters.sales_status;
      if (filters.publication_status) params.publication_status = filters.publication_status;
      if (filters.price_min) params.sale_price_min = parseFloat(filters.price_min) * 10000;
      if (filters.price_max) params.sale_price_max = parseFloat(filters.price_max) * 10000;

      const { items, total } = await propertyService.getPropertiesWithCount(params);
      setProperties(items);
      setTotalItems(total);
    } catch (err) {
      console.error('物件取得エラー:', err);
      setError('物件データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [currentPage, debouncedSearch, filters.property_type, filters.sales_status, filters.publication_status, filters.price_min, filters.price_max, sortBy, sortOrder]);

  useEffect(() => {
    fetchProperties();
  }, [fetchProperties]);

  // ============================================
  // ビュー管理
  // ============================================
  useEffect(() => {
    const view = views.find(v => v.id === activeViewId);
    if (view) {
      setVisibleColumns(view.columns);
      setFilters(view.filters);
      setSortBy(view.sortBy);
      setSortOrder(view.sortOrder);
    }
  }, [activeViewId, views]);

  useEffect(() => {
    localStorage.setItem(VIEWS_STORAGE_KEY, JSON.stringify(views));
  }, [views]);

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

  const deleteView = (viewId: string) => {
    if (DEFAULT_VIEWS.some(v => v.id === viewId)) return;
    setViews(views.filter(v => v.id !== viewId));
    if (activeViewId === viewId) setActiveViewId('all');
  };

  // ============================================
  // 選択操作
  // ============================================
  const handleRowSelect = (id: number, index: number, event: React.MouseEvent) => {
    event.stopPropagation();
    const newSelected = new Set(selectedIds);

    if (event.shiftKey && lastSelectedIndex !== null) {
      // 範囲選択
      const start = Math.min(lastSelectedIndex, index);
      const end = Math.max(lastSelectedIndex, index);
      for (let i = start; i <= end; i++) {
        newSelected.add(properties[i].id);
      }
    } else if (event.metaKey || event.ctrlKey) {
      // 追加/解除
      if (newSelected.has(id)) {
        newSelected.delete(id);
      } else {
        newSelected.add(id);
      }
    } else {
      // 単一選択
      newSelected.clear();
      newSelected.add(id);
    }

    setSelectedIds(newSelected);
    setLastSelectedIndex(index);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === properties.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(properties.map(p => p.id)));
    }
  };

  // ============================================
  // コンテキストメニュー
  // ============================================
  const handleContextMenu = (e: React.MouseEvent, property: Property) => {
    e.preventDefault();
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      propertyId: property.id,
      property,
    });
  };

  const closeContextMenu = () => {
    setContextMenu({ visible: false, x: 0, y: 0, propertyId: null, property: null });
  };

  useEffect(() => {
    const handleClick = () => closeContextMenu();
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeContextMenu();
    };
    document.addEventListener('click', handleClick);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('click', handleClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleStatusChange = async (id: number, field: string, value: string) => {
    try {
      await propertyService.updateProperty(id, { [field]: value });
      setProperties(prev => prev.map(p => p.id === id ? { ...p, [field]: value } : p));
      closeContextMenu();
    } catch (err) {
      console.error('ステータス更新エラー:', err);
      alert('更新に失敗しました');
    }
  };

  // ============================================
  // インライン編集
  // ============================================
  const startInlineEdit = (property: Property, key: string) => {
    setEditingCell({ id: property.id, key });
    setEditValue(String(getCellValue(property, key) || ''));
  };

  const saveInlineEdit = async () => {
    if (!editingCell) return;
    try {
      let value: string | number = editValue;
      if (editingCell.key === 'sale_price') {
        // 価格は万円単位で入力→円に変換
        value = parseFloat(editValue) * 10000;
      }
      await propertyService.updateProperty(editingCell.id, { [editingCell.key]: value });
      setProperties(prev => prev.map(p =>
        p.id === editingCell.id ? { ...p, [editingCell.key]: value } : p
      ));
      setEditingCell(null);
    } catch (err) {
      console.error('更新エラー:', err);
      alert('更新に失敗しました');
    }
  };

  const cancelInlineEdit = () => {
    setEditingCell(null);
    setEditValue('');
  };

  // ============================================
  // 一括操作
  // ============================================
  const handleBulkStatusChange = async (field: string, value: string) => {
    if (selectedIds.size === 0) return;
    if (!confirm(`${selectedIds.size}件の物件を「${value}」に変更しますか？`)) return;

    try {
      await Promise.all(
        Array.from(selectedIds).map(id => propertyService.updateProperty(id, { [field]: value }))
      );
      setProperties(prev => prev.map(p =>
        selectedIds.has(p.id) ? { ...p, [field]: value } : p
      ));
      setSelectedIds(new Set());
    } catch (err) {
      console.error('一括更新エラー:', err);
      alert('一括更新に失敗しました');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`${selectedIds.size}件の物件を削除しますか？この操作は取り消せません。`)) return;

    try {
      await Promise.all(Array.from(selectedIds).map(id => propertyService.deleteProperty(id)));
      setProperties(prev => prev.filter(p => !selectedIds.has(p.id)));
      setSelectedIds(new Set());
      setTotalItems(prev => prev - selectedIds.size);
    } catch (err) {
      console.error('一括削除エラー:', err);
      alert('一括削除に失敗しました');
    }
  };

  // ============================================
  // キーボード操作
  // ============================================
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (editingCell) {
        if (e.key === 'Escape') cancelInlineEdit();
        if (e.key === 'Enter') saveInlineEdit();
        return;
      }

      // フォーカスがinput/textareaの場合は無視
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      switch (e.key) {
        case 'j':
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex(prev => Math.min(prev + 1, properties.length - 1));
          break;
        case 'k':
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          if (focusedIndex >= 0 && properties[focusedIndex]) {
            navigate(`/properties/${properties[focusedIndex].id}/edit`);
          }
          break;
        case ' ':
          e.preventDefault();
          if (focusedIndex >= 0 && properties[focusedIndex]) {
            const id = properties[focusedIndex].id;
            setSelectedIds(prev => {
              const newSet = new Set(prev);
              if (newSet.has(id)) newSet.delete(id);
              else newSet.add(id);
              return newSet;
            });
          }
          break;
        case 'Delete':
        case 'Backspace':
          if (selectedIds.size > 0) handleBulkDelete();
          break;
        case 'a':
          if (e.metaKey || e.ctrlKey) {
            e.preventDefault();
            handleSelectAll();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [properties, focusedIndex, editingCell, selectedIds, navigate]);

  // ============================================
  // ソート
  // ============================================
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

  // ============================================
  // カラム幅調整（将来実装予定）
  // ============================================
  // const handleColumnResize = (key: string, newWidth: number) => {
  //   setColumnWidths(prev => ({ ...prev, [key]: Math.max(newWidth, ALL_COLUMNS.find(c => c.key === key)?.minWidth || 50) }));
  // };

  // ============================================
  // エクスポート
  // ============================================
  const handleHomesExport = async () => {
    if (properties.length === 0) {
      alert('出力する物件がありません');
      return;
    }
    setExporting(true);
    try {
      const propertyIds = selectedIds.size > 0 ? Array.from(selectedIds) : properties.map(p => p.id);
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
      a.download = `homes_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.csv`;
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

  // ============================================
  // セル値取得
  // ============================================
  const getCellValue = (property: Property, key: string): string | number => {
    switch (key) {
      case 'id': return property.id;
      case 'company_property_number': return property.company_property_number || '-';
      case 'property_name': return property.property_name || '-';
      case 'sale_price': return property.sale_price ? formatPrice(property.sale_price) : '-';
      case 'property_type': {
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

  // ============================================
  // アクティブフィルター数
  // ============================================
  const activeFilterCount = useMemo(() => {
    return [filters.search, filters.property_type, filters.sales_status, filters.publication_status, filters.price_min, filters.price_max].filter(Boolean).length;
  }, [filters]);

  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

  // ============================================
  // 行の高さ
  // ============================================
  const rowPadding = rowDensity === 'compact' ? 'py-1.5' : rowDensity === 'comfortable' ? 'py-4' : 'py-2.5';

  // ============================================
  // レンダリング
  // ============================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100" ref={containerRef}>
      {/* ヘッダー - World-Class Design */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">物件一覧</h1>
          {selectedIds.size > 0 && (
            <span className="px-3 py-1 bg-blue-500/10 text-blue-600 rounded-full text-sm font-semibold backdrop-blur-sm">
              {selectedIds.size}件選択
            </span>
          )}
        </div>
        <div className="flex gap-2">
          {selectedIds.size > 0 && (
            <>
              <div className="relative group">
                <button className="px-3 py-2 text-sm font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 transition-colors">
                  ステータス変更
                </button>
                <div className="absolute right-0 mt-1 w-40 bg-white/95 backdrop-blur-sm rounded-xl shadow-xl border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 overflow-hidden">
                  {SALES_STATUS_OPTIONS.map(status => (
                    <button
                      key={status}
                      onClick={() => handleBulkStatusChange('sales_status', status)}
                      className="block w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 transition-colors"
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
              <button
                onClick={handleBulkDelete}
                className="px-3 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
              >
                削除
              </button>
            </>
          )}
          <button
            onClick={handleHomesExport}
            disabled={exporting || properties.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-lg shadow-sm shadow-emerald-200 hover:shadow-md hover:shadow-emerald-200 disabled:opacity-50 transition-all"
          >
            {exporting ? '出力中...' : 'HOMES出力'}
          </button>
          <button
            onClick={() => navigate('/properties/new')}
            className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-sm shadow-blue-200 hover:shadow-md hover:shadow-blue-200 transition-all"
          >
            + 新規登録
          </button>
        </div>
      </div>

      {/* ビュータブ + ツールバー */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100/50 mb-4">
        {/* ビュータブ */}
        <div className="flex items-center border-b border-gray-100 px-2">
          <div className="flex gap-1 overflow-x-auto py-2">
            {views.map(view => (
              <button
                key={view.id}
                onClick={() => { setActiveViewId(view.id); setCurrentPage(1); }}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all
                  ${activeViewId === view.id ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                {view.name}
              </button>
            ))}
          </div>

          {/* ビュー追加メニュー */}
          <div className="relative ml-2">
            <button
              onClick={() => setShowViewMenu(!showViewMenu)}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              title="ビュー管理"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
            {showViewMenu && (
              <div className="absolute right-0 top-full mt-1 w-64 bg-white rounded-xl shadow-lg border p-3 z-50">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2">ビューを保存</div>
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={newViewName}
                    onChange={(e) => setNewViewName(e.target.value)}
                    placeholder="ビュー名"
                    className="flex-1 px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={saveCurrentView}
                    disabled={!newViewName.trim()}
                    className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    保存
                  </button>
                </div>
                <div className="border-t pt-2 mt-2">
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-2">カスタムビュー</div>
                  {views.filter(v => !DEFAULT_VIEWS.some(d => d.id === v.id)).map(view => (
                    <div key={view.id} className="flex items-center justify-between px-3 py-2 hover:bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-700">{view.name}</span>
                      <button onClick={() => deleteView(view.id)} className="text-gray-400 hover:text-red-500">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

          {/* 表示設定 */}
          <div className="relative ml-auto mr-2">
            <button
              onClick={() => setShowSettingsMenu(!showSettingsMenu)}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              title="表示設定"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            {showSettingsMenu && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-xl shadow-lg border p-3 z-50">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2">行の高さ</div>
                {(['compact', 'normal', 'comfortable'] as RowDensity[]).map(density => (
                  <button
                    key={density}
                    onClick={() => { setRowDensity(density); setShowSettingsMenu(false); }}
                    className={`block w-full text-left px-3 py-2 text-sm rounded-lg ${rowDensity === density ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}`}
                  >
                    {density === 'compact' ? 'コンパクト' : density === 'normal' ? '標準' : 'ゆったり'}
                  </button>
                ))}
                <div className="border-t mt-2 pt-2">
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-2">表示モード</div>
                  {(['table', 'card'] as ViewMode[]).map(mode => (
                    <button
                      key={mode}
                      onClick={() => { setViewMode(mode); setShowSettingsMenu(false); }}
                      className={`block w-full text-left px-3 py-2 text-sm rounded-lg ${viewMode === mode ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}`}
                    >
                      {mode === 'table' ? 'テーブル' : mode === 'card' ? 'カード' : 'ギャラリー'}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ツールバー */}
        <div className="px-4 py-3 border-b border-gray-100">
          <div className="flex items-center gap-3 flex-wrap">
            {/* 検索 - 洗練されたミニマルデザイン */}
            <div className="relative group">
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                placeholder="検索..."
                className="w-48 px-3 py-2 text-sm bg-gray-50 border-0 rounded-lg placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all"
              />
              <kbd className="absolute right-2 top-1/2 -translate-y-1/2 hidden sm:inline-flex px-1.5 py-0.5 text-[10px] font-medium text-gray-400 bg-gray-100 rounded">⌘K</kbd>
            </div>

            {/* フィルターチップ */}
            {filters.property_type && (
              <span
                onClick={() => setFilters({ ...filters, property_type: '' })}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-lg cursor-pointer hover:bg-blue-100"
              >
                種別: {propertyTypeMap[filters.property_type] || filters.property_type}
                <span className="opacity-60">×</span>
              </span>
            )}
            {filters.sales_status && (
              <span
                onClick={() => setFilters({ ...filters, sales_status: '' })}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-green-50 text-green-700 rounded-lg cursor-pointer hover:bg-green-100"
              >
                {filters.sales_status}
                <span className="opacity-60">×</span>
              </span>
            )}
            {filters.publication_status && (
              <span
                onClick={() => setFilters({ ...filters, publication_status: '' })}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-amber-50 text-amber-700 rounded-lg cursor-pointer hover:bg-amber-100"
              >
                {filters.publication_status}
                <span className="opacity-60">×</span>
              </span>
            )}
            {(filters.price_min || filters.price_max) && (
              <span
                onClick={() => setFilters({ ...filters, price_min: '', price_max: '' })}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-pink-50 text-pink-700 rounded-lg cursor-pointer hover:bg-pink-100"
              >
                価格: {filters.price_min || '0'}〜{filters.price_max || '∞'}万
                <span className="opacity-60">×</span>
              </span>
            )}

            {/* フィルター追加 */}
            <div className="relative">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 border border-dashed border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <span>+</span> フィルター
                {activeFilterCount > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">{activeFilterCount}</span>
                )}
              </button>
              {showFilters && (
                <div className="absolute top-full left-0 mt-1 w-72 bg-white rounded-xl shadow-lg border p-4 z-50">
                  {/* 物件種別 */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">物件種別</div>
                    <div className="flex flex-wrap gap-1.5">
                      {filterOptions.property_type_simple.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => setFilters({ ...filters, property_type: filters.property_type === opt.value ? '' : opt.value })}
                          className={`px-2.5 py-1 text-xs rounded-md border ${filters.property_type === opt.value ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:bg-gray-50'}`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  {/* ステータス */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">販売状態</div>
                    <div className="flex flex-wrap gap-1.5">
                      {filterOptions.sales_status.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => setFilters({ ...filters, sales_status: filters.sales_status === opt.value ? '' : opt.value })}
                          className={`px-2.5 py-1 text-xs rounded-md border ${filters.sales_status === opt.value ? 'border-green-500 bg-green-50 text-green-700' : 'border-gray-200 hover:bg-gray-50'}`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  {/* 公開状態 */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">公開状態</div>
                    <div className="flex flex-wrap gap-1.5">
                      {filterOptions.publication_status.map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => setFilters({ ...filters, publication_status: filters.publication_status === opt.value ? '' : opt.value })}
                          className={`px-2.5 py-1 text-xs rounded-md border ${filters.publication_status === opt.value ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-gray-200 hover:bg-gray-50'}`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  {/* 価格 */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-2">価格（万円）</div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={filters.price_min}
                        onChange={(e) => setFilters({ ...filters, price_min: e.target.value })}
                        placeholder="下限"
                        className="w-20 px-2 py-1.5 text-sm border rounded-md"
                      />
                      <span className="text-gray-400">〜</span>
                      <input
                        type="number"
                        value={filters.price_max}
                        onChange={(e) => setFilters({ ...filters, price_max: e.target.value })}
                        placeholder="上限"
                        className="w-20 px-2 py-1.5 text-sm border rounded-md"
                      />
                    </div>
                  </div>
                  {activeFilterCount > 0 && (
                    <button
                      onClick={() => setFilters(DEFAULT_FILTERS)}
                      className="w-full py-2 text-sm text-red-600 bg-red-50 rounded-lg hover:bg-red-100"
                    >
                      すべてクリア
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* 列選択 */}
            <div className="relative ml-auto">
              <button
                onClick={() => setShowColumnPicker(!showColumnPicker)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                </svg>
                列
              </button>
              {showColumnPicker && (
                <div className="absolute right-0 top-full mt-1 w-56 bg-white rounded-xl shadow-lg border p-3 z-50">
                  <div className="text-xs font-semibold text-gray-500 uppercase mb-2">表示する列</div>
                  <div className="max-h-60 overflow-y-auto">
                    {ALL_COLUMNS.map(col => (
                      <label key={col.key} className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={visibleColumns.includes(col.key)}
                          onChange={(e) => {
                            if (e.target.checked) setVisibleColumns([...visibleColumns, col.key]);
                            else setVisibleColumns(visibleColumns.filter(c => c !== col.key));
                          }}
                          className="accent-blue-600"
                        />
                        <span className="text-sm">{col.label}</span>
                      </label>
                    ))}
                  </div>
                  <div className="flex gap-2 mt-2 pt-2 border-t">
                    <button
                      onClick={() => setVisibleColumns(ALL_COLUMNS.map(c => c.key))}
                      className="flex-1 py-1.5 text-xs text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
                    >
                      全選択
                    </button>
                    <button
                      onClick={() => setVisibleColumns(DEFAULT_COLUMNS)}
                      className="flex-1 py-1.5 text-xs text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
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

      {/* テーブル / カード表示 */}
      {viewMode === 'table' ? (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table ref={tableRef} className="min-w-full">
              <thead className="sticky top-0 bg-white z-10 shadow-sm">
                <tr className="border-b border-gray-200">
                  <th className="px-3 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={properties.length > 0 && selectedIds.size === properties.length}
                      onChange={handleSelectAll}
                      className="accent-blue-600"
                    />
                  </th>
                  {visibleColumns.map(key => {
                    const col = ALL_COLUMNS.find(c => c.key === key);
                    if (!col) return null;
                    const width = columnWidths[key] || col.width;
                    return (
                      <th
                        key={key}
                        className={`px-3 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap ${col.sortable ? 'cursor-pointer hover:bg-gray-50 select-none' : ''}`}
                        style={{ width, minWidth: col.minWidth }}
                        onClick={() => handleSort(key)}
                      >
                        <div className="flex items-center gap-1">
                          {col.label}
                          {col.sortable && (
                            <span className={sortBy === key ? 'text-blue-600' : 'text-gray-300'}>
                              {sortBy === key ? (sortOrder === 'asc' ? '↑' : '↓') : '↕'}
                            </span>
                          )}
                        </div>
                      </th>
                    );
                  })}
                  <th className="px-3 py-3 text-right text-xs font-semibold text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  [...Array(8)].map((_, i) => (
                    <tr key={i} className="animate-pulse border-b border-gray-50">
                      <td className="px-3 py-3"><div className="w-4 h-4 bg-gray-200 rounded"></div></td>
                      {visibleColumns.map((_, j) => (
                        <td key={j} className="px-3 py-3"><div className="h-4 bg-gray-200 rounded w-full"></div></td>
                      ))}
                      <td className="px-3 py-3"><div className="h-4 bg-gray-200 rounded w-16 ml-auto"></div></td>
                    </tr>
                  ))
                ) : error ? (
                  <tr>
                    <td colSpan={visibleColumns.length + 2} className="px-4 py-16 text-center">
                      <div className="text-red-500 mb-4">{error}</div>
                      <button onClick={fetchProperties} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        再読み込み
                      </button>
                    </td>
                  </tr>
                ) : properties.length === 0 ? (
                  <tr>
                    <td colSpan={visibleColumns.length + 2} className="px-4 py-16 text-center">
                      <div className="text-gray-400 text-6xl mb-4">📋</div>
                      <div className="text-gray-500 mb-2">該当する物件がありません</div>
                      <div className="text-gray-400 text-sm">フィルターを変更するか、新規登録してください</div>
                    </td>
                  </tr>
                ) : (
                  properties.map((property, index) => (
                    <tr
                      key={property.id}
                      className={`border-b border-gray-50 transition-colors cursor-pointer
                        ${selectedIds.has(property.id) ? 'bg-blue-50' : ''}
                        ${focusedIndex === index ? 'ring-2 ring-inset ring-blue-400' : ''}
                        hover:bg-gray-50`}
                      onClick={() => navigate(`/properties/${property.id}/edit`)}
                      onContextMenu={(e) => handleContextMenu(e, property)}
                    >
                      <td className={`px-3 ${rowPadding}`} onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={selectedIds.has(property.id)}
                          onChange={(e) => handleRowSelect(property.id, index, e as unknown as React.MouseEvent)}
                          onClick={(e) => handleRowSelect(property.id, index, e as unknown as React.MouseEvent)}
                          className="accent-blue-600"
                        />
                      </td>
                      {visibleColumns.map(key => {
                        const value = getCellValue(property, key);
                        const isEditing = editingCell?.id === property.id && editingCell?.key === key;
                        const isEditable = ['sale_price', 'sales_status', 'publication_status'].includes(key);

                        return (
                          <td
                            key={key}
                            className={`px-3 ${rowPadding} text-sm`}
                            onDoubleClick={(e) => {
                              if (isEditable) {
                                e.stopPropagation();
                                startInlineEdit(property, key);
                              }
                            }}
                          >
                            {isEditing ? (
                              <input
                                autoFocus
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                onBlur={saveInlineEdit}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') saveInlineEdit();
                                  if (e.key === 'Escape') cancelInlineEdit();
                                }}
                                onClick={(e) => e.stopPropagation()}
                                className="w-full px-2 py-1 border rounded text-sm focus:ring-2 focus:ring-blue-500"
                              />
                            ) : key === 'sales_status' ? (
                              <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full
                                ${value === '販売中' ? 'bg-green-50 text-green-700' : value === '成約済' ? 'bg-blue-50 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
                                {value}
                              </span>
                            ) : key === 'publication_status' ? (
                              <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full
                                ${value === '公開' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                                {value}
                              </span>
                            ) : key === 'property_name' ? (
                              <span className="line-clamp-1 text-gray-900">{value}</span>
                            ) : key === 'sale_price' ? (
                              <span className="font-semibold text-gray-900">{value}</span>
                            ) : (
                              <span className="text-gray-700">{value}</span>
                            )}
                          </td>
                        );
                      })}
                      <td className={`px-3 ${rowPadding} text-right whitespace-nowrap`} onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => navigate(`/properties/${property.id}/edit`)}
                          className="px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                        >
                          編集
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        // カード表示
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            [...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-4 shadow-sm animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))
          ) : properties.map(property => (
            <div
              key={property.id}
              onClick={() => navigate(`/properties/${property.id}/edit`)}
              onContextMenu={(e) => handleContextMenu(e, property)}
              className={`bg-white rounded-xl p-4 shadow-sm cursor-pointer transition-all hover:shadow-md
                ${selectedIds.has(property.id) ? 'ring-2 ring-blue-500' : ''}`}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900 line-clamp-1">{property.property_name || '-'}</h3>
                <input
                  type="checkbox"
                  checked={selectedIds.has(property.id)}
                  onChange={() => setSelectedIds(prev => {
                    const newSet = new Set(prev);
                    if (newSet.has(property.id)) newSet.delete(property.id);
                    else newSet.add(property.id);
                    return newSet;
                  })}
                  onClick={(e) => e.stopPropagation()}
                  className="accent-blue-600"
                />
              </div>
              <div className="text-lg font-bold text-gray-900 mb-2">
                {property.sale_price ? formatPrice(property.sale_price) : '-'}
              </div>
              <div className="flex gap-2 mb-2">
                <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full
                  ${property.sales_status === '販売中' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                  {property.sales_status || '未設定'}
                </span>
                <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full
                  ${property.publication_status === '公開' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                  {property.publication_status || '非公開'}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                {property.prefecture}{property.city}{property.address_detail}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ページネーション */}
      {!loading && properties.length > 0 && (
        <div className="flex items-center justify-between mt-4 bg-white/80 backdrop-blur-sm px-4 py-3 rounded-2xl shadow-sm border border-gray-100/50">
          <div className="text-sm text-gray-500">
            全 {totalItems.toLocaleString()} 件中 {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, totalItems)} 件
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
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              次へ
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
            >
              最後
            </button>
          </div>
        </div>
      )}

      {/* コンテキストメニュー */}
      {contextMenu.visible && contextMenu.property && (
        <div
          className="fixed bg-white rounded-xl shadow-2xl border py-2 z-[9999] min-w-[200px]"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="px-4 py-2 border-b text-sm font-medium text-gray-700 truncate max-w-[250px]">
            {contextMenu.property.property_name || `物件 #${contextMenu.property.id}`}
          </div>

          {/* 販売ステータス変更 */}
          <div className="py-1">
            <div className="px-4 py-1 text-xs text-gray-400 uppercase">販売ステータス</div>
            {SALES_STATUS_OPTIONS.map(status => (
              <button
                key={status}
                onClick={() => handleStatusChange(contextMenu.propertyId!, 'sales_status', status)}
                className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-50
                  ${contextMenu.property?.sales_status === status ? 'text-blue-600 font-medium' : ''}`}
              >
                {status}
                {contextMenu.property?.sales_status === status && ' ✓'}
              </button>
            ))}
          </div>

          {/* 公開ステータス変更 */}
          <div className="py-1 border-t">
            <div className="px-4 py-1 text-xs text-gray-400 uppercase">公開状態</div>
            {PUBLICATION_STATUS_OPTIONS.map(status => (
              <button
                key={status}
                onClick={() => handleStatusChange(contextMenu.propertyId!, 'publication_status', status)}
                className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-50
                  ${contextMenu.property?.publication_status === status ? 'text-blue-600 font-medium' : ''}`}
              >
                {status}
                {contextMenu.property?.publication_status === status && ' ✓'}
              </button>
            ))}
          </div>

          {/* その他操作 */}
          <div className="py-1 border-t">
            <button
              onClick={() => {
                navigate(`/properties/${contextMenu.propertyId}/edit`);
                closeContextMenu();
              }}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50"
            >
              編集画面を開く
            </button>
            <button
              onClick={() => {
                window.open(`/properties/${contextMenu.propertyId}/edit`, '_blank');
                closeContextMenu();
              }}
              className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50"
            >
              新しいタブで開く
            </button>
            <button
              onClick={async () => {
                if (confirm('この物件を削除しますか？')) {
                  try {
                    await propertyService.deleteProperty(contextMenu.propertyId!);
                    setProperties(prev => prev.filter(p => p.id !== contextMenu.propertyId));
                    setTotalItems(prev => prev - 1);
                  } catch (err) {
                    console.error('削除エラー:', err);
                    alert('削除に失敗しました');
                  }
                }
                closeContextMenu();
              }}
              className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
            >
              削除
            </button>
          </div>
        </div>
      )}

      {/* キーボードショートカットヘルプ */}
      <div className="fixed bottom-4 left-4 text-xs text-gray-400">
        <span className="mr-3">j/k: 移動</span>
        <span className="mr-3">Enter: 編集</span>
        <span className="mr-3">Space: 選択</span>
        <span>⌘A: 全選択</span>
      </div>
    </div>
  );
};

export default PropertiesPage;
