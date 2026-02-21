/**
 * buildTabGroups: タブ構築ロジック
 *
 * propertiesカラムを分類して、所在地/基本情報/価格・取引/管理・費用/土地/建物/設備/画像/登記の
 * タブグループを構築する。DynamicFormから切り出した純粋関数。
 */
import { ColumnWithLabel } from '../../services/metadataService';
import { TAB_GROUPS } from '../../constants';

export interface TabGroup {
  tableName: string;
  tableLabel: string;
  tableIcon: string;
  groups: Record<string, ColumnWithLabel[]>;
}

interface TableInfo {
  table_name: string;
  table_comment?: string;
}

// 物件種別によるフィールド表示判定
export const isFieldVisibleForPropertyType = (
  visibleFor: string[] | null | undefined,
  propertyType: string | null | undefined,
  columnName: string
): boolean => {
  if (columnName === 'property_type' || columnName === 'is_new_construction') return true;
  if (!propertyType) return false;
  if (visibleFor === null || visibleFor === undefined) return true;
  if (visibleFor.length === 0) return false;
  return visibleFor.includes(propertyType);
};

// グループ別にカラムを分類するヘルパー
const groupColumns = (columns: ColumnWithLabel[], defaultGroup: string): Record<string, ColumnWithLabel[]> => {
  return columns.reduce((acc, column) => {
    const groupName = column.group_name || defaultGroup;
    if (!acc[groupName]) acc[groupName] = [];
    acc[groupName].push(column);
    return acc;
  }, {} as Record<string, ColumnWithLabel[]>);
};

/**
 * タブグループを構築する
 */
export function buildTabGroups(
  orderedTables: TableInfo[],
  allColumns: Record<string, ColumnWithLabel[]> | undefined,
  propertiesColumns: ColumnWithLabel[],
  currentPropertyType: string | null,
): TabGroup[] {
  const locationGroups = TAB_GROUPS.location;
  const basicInfoGroups = TAB_GROUPS.basicInfo;
  const priceDealGroups = TAB_GROUPS.priceDeal;
  const managementGroups = TAB_GROUPS.management;

  const tabGroups: TabGroup[] = [];

  // 所在地・周辺情報タブ用のデータを先に準備
  const locationColumns = propertiesColumns.filter(col =>
    locationGroups.includes(col.group_name || '') &&
    isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name)
  );
  const locationTabData = locationColumns.length > 0 ? {
    tableName: 'properties_location',
    tableLabel: '所在地・周辺情報',
    tableIcon: '📍',
    groups: groupColumns(locationColumns, '所在地'),
  } : null;

  orderedTables.forEach(table => {
    const tableColumns = allColumns?.[table.table_name] || [];

    const filteredColumns = tableColumns.filter(col => {
      if (table.table_name === 'properties' && locationGroups.includes(col.group_name || '')) {
        return false;
      }
      if (TAB_GROUPS.excluded.includes(col.group_name || '')) {
        return false;
      }
      if (table.table_name === 'land_info' && TAB_GROUPS.regulationFromLandInfo.includes(col.group_name || '')) {
        return false;
      }
      return isFieldVisibleForPropertyType(col.visible_for, currentPropertyType, col.column_name);
    });

    const grouped = groupColumns(filteredColumns, '基本情報');

    if (table.table_name === 'properties') {
      if (locationTabData) {
        tabGroups.push(locationTabData);
      }

      // 基本情報タブ
      const basicInfoColumns = filteredColumns.filter(col =>
        basicInfoGroups.includes(col.group_name || '')
      );
      if (basicInfoColumns.length > 0) {
        tabGroups.push({
          tableName: 'properties_basic',
          tableLabel: '基本情報',
          tableIcon: '🏠',
          groups: groupColumns(basicInfoColumns, '基本情報'),
        });
      }

      // 価格・取引タブ
      const priceDealColumns = filteredColumns.filter(col =>
        priceDealGroups.includes(col.group_name || '')
      );
      if (priceDealColumns.length > 0) {
        tabGroups.push({
          tableName: 'properties_price',
          tableLabel: '価格・取引',
          tableIcon: '💰',
          groups: groupColumns(priceDealColumns, '価格情報'),
        });
      }

      // 管理・費用タブ
      const managementColumns = filteredColumns.filter(col =>
        managementGroups.includes(col.group_name || '')
      );
      if (managementColumns.length > 0) {
        tabGroups.push({
          tableName: 'properties_management',
          tableLabel: '管理・費用',
          tableIcon: '📋',
          groups: groupColumns(managementColumns, '管理情報'),
        });
      }

      return;
    }

    // 他のテーブル
    if (Object.keys(grouped).length > 0) {
      const tableLabels: Record<string, { label: string; icon: string }> = {
        'land_info': { label: '土地情報', icon: '🗺️' },
        'building_info': { label: '建物情報', icon: '🏗️' },
        'amenities': { label: '設備・周辺環境', icon: '🔧' },
        'property_images': { label: '画像情報', icon: '📸' },
      };

      const tableInfo = tableLabels[table.table_name] || {
        label: table.table_comment || table.table_name,
        icon: '📄'
      };

      tabGroups.push({
        tableName: table.table_name,
        tableLabel: tableInfo.label,
        tableIcon: tableInfo.icon,
        groups: grouped,
      });
    }
  });

  // 登記情報タブを追加
  tabGroups.push({
    tableName: 'registries',
    tableLabel: '登記情報',
    tableIcon: '📜',
    groups: {},
  });

  return tabGroups;
}

/**
 * グループ名からタブインデックスを取得する
 */
export function getTabIndexForGroup(tabGroups: TabGroup[], groupName: string): number | null {
  const groupToTabIndex: Record<string, number> = {};

  tabGroups.forEach((tab, index) => {
    Object.keys(tab.groups).forEach((grp) => {
      groupToTabIndex[grp] = index;
    });
    if (tab.tableName === 'properties_location') {
      TAB_GROUPS.location.forEach((grp) => { groupToTabIndex[grp] = index; });
    } else if (tab.tableName === 'properties_basic') {
      TAB_GROUPS.basicInfo.forEach((grp) => { groupToTabIndex[grp] = index; });
    } else if (tab.tableName === 'properties_price') {
      TAB_GROUPS.priceDeal.forEach((grp) => { groupToTabIndex[grp] = index; });
    } else if (tab.tableName === 'properties_management') {
      TAB_GROUPS.management.forEach((grp) => { groupToTabIndex[grp] = index; });
    } else if (tab.tableName === 'land_info') {
      groupToTabIndex['土地情報'] = index;
      groupToTabIndex['土地'] = index;
    } else if (tab.tableName === 'building_info') {
      groupToTabIndex['建物情報'] = index;
      groupToTabIndex['建物'] = index;
    }
  });

  const tabIndex = groupToTabIndex[groupName];
  return tabIndex !== undefined ? tabIndex : null;
}
