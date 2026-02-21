/**
 * FieldGroup: フィールドグループコンポーネント
 *
 * 同じグループ名のフィールドをまとめて表示する
 * アコーディオン折りたたみ、フィールドタイプ別レイアウト、
 * 所在地グループのLocationField表示を担当
 */
import React, { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import { FieldFactory } from './FieldFactory';
import { LocationField } from './LocationField';

interface FieldGroupProps {
  groupName: string;
  columns: ColumnWithLabel[];
  disabled?: boolean;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
  onOpenGeoPanel?: () => void;
}

export const FieldGroup: React.FC<FieldGroupProps> = ({
  groupName,
  columns,
  disabled = false,
  collapsible = false,
  defaultCollapsed = false,
  onOpenGeoPanel,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const { watch } = useFormContext();

  // 引渡時期の値を監視（条件付き表示用）
  const deliveryTiming = watch('delivery_timing');

  // 条件付き表示フィールドのフィルタリング
  const shouldShowField = (columnName: string): boolean => {
    if (columnName === 'delivery_date') {
      return deliveryTiming === '3:期日指定';
    }
    if (columnName === 'move_in_consultation') {
      return deliveryTiming === '2:相談';
    }
    return true;
  };

  const visibleColumns = columns.filter(col =>
    !['id', 'property_id', 'created_at', 'updated_at'].includes(col.column_name) &&
    shouldShowField(col.column_name)
  );

  if (visibleColumns.length === 0) return null;

  // フィールドタイプ別分類
  const textareaFields = visibleColumns.filter(col => col.input_type === 'textarea');
  const checkboxFields = visibleColumns.filter(col =>
    col.input_type === 'checkbox' || col.data_type?.toLowerCase().includes('bool')
  );
  const jsonFields = visibleColumns.filter(col => col.input_type?.startsWith('json_'));
  const imageFields = visibleColumns.filter(col => col.input_type === 'images');
  const regularFields = visibleColumns.filter(col =>
    !textareaFields.includes(col) && !checkboxFields.includes(col) && !jsonFields.includes(col) && !imageFields.includes(col)
  );

  // グループアイコン
  const getGroupIcon = (name: string) => {
    const iconMap: Record<string, string> = {
      '所在地': '📍', '交通': '🚃', '学区': '🏫', '周辺施設': '🏪',
      '基本情報': '🏠', '基本・取引情報': '🏠', '価格情報': '💰',
      '契約条件': '📋', '元請会社': '🏢', '土地情報': '🗺️',
      '建物情報': '🏗️', '設備・周辺環境': '🔧', '画像情報': '📸',
      '管理情報': '⚙️', 'システム': '⚙️',
    };
    return iconMap[name] || '📄';
  };

  const isLocationGroup = groupName === '所在地';

  // 所在地グループの場合、緯度・経度フィールドを通常表示から除外
  const locationFieldNames = ['latitude', 'longitude'];
  const filteredRegularFields = isLocationGroup
    ? regularFields.filter(col => !locationFieldNames.includes(col.column_name))
    : regularFields;

  return (
    <div style={{
      marginBottom: '20px',
      padding: '16px',
      backgroundColor: '#FAFAFA',
      borderRadius: '12px',
    }}>
      {/* グループヘッダー */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: isCollapsed ? '0' : '16px',
          flexWrap: 'wrap',
          gap: '8px',
          cursor: collapsible ? 'pointer' : 'default',
          userSelect: 'none',
        }}
        onClick={() => collapsible && setIsCollapsed(!isCollapsed)}
      >
        {collapsible && (
          <span style={{
            fontSize: '14px',
            color: '#9CA3AF',
            marginRight: '4px',
            transition: 'transform 200ms ease',
            transform: isCollapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
          }}>
            ▼
          </span>
        )}
        <span style={{ fontSize: '24px', marginRight: '4px' }}>{getGroupIcon(groupName)}</span>
        <h3 style={{
          fontSize: '18px',
          fontWeight: 600,
          color: '#1A1A1A',
          margin: 0
        }}>
          {groupName}
        </h3>
        {collapsible && isCollapsed && (
          <span style={{ fontSize: '12px', color: '#9CA3AF', marginLeft: '8px' }}>
            ({visibleColumns.length}項目)
          </span>
        )}
      </div>

      {/* アコーディオン: 折りたたみ時はコンテンツを非表示 */}
      {!isCollapsed && (
        <>
          {/* 通常フィールド - 2列 */}
          {filteredRegularFields.length > 0 && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '16px',
              marginBottom: isLocationGroup || jsonFields.length > 0 || checkboxFields.length > 0 || textareaFields.length > 0 ? '16px' : 0,
            }}>
              {filteredRegularFields.map(column => (
                <div key={column.column_name}>
                  <FieldFactory column={column} disabled={disabled} />
                </div>
              ))}
            </div>
          )}

          {/* 所在地グループの場合、地図付き緯度経度フィールドを表示 */}
          {isLocationGroup && (
            <LocationField disabled={disabled} onOpenGeoPanel={onOpenGeoPanel} />
          )}

          {/* チェックボックス群 - 3列 */}
          {checkboxFields.length > 0 && (
            <div style={{ marginBottom: jsonFields.length > 0 || textareaFields.length > 0 ? '24px' : 0 }}>
              <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280', marginBottom: '12px' }}>設定項目</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                {checkboxFields.map(column => (
                  <div key={column.column_name}>
                    <FieldFactory column={column} disabled={disabled} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* JSON専用フィールド - フル幅 */}
          {jsonFields.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: textareaFields.length > 0 || imageFields.length > 0 ? '24px' : 0 }}>
              {jsonFields.map(column => (
                <div key={column.column_name}>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#6B7280', marginBottom: '8px' }}>
                    {column.label_ja || column.column_name}
                  </label>
                  <FieldFactory column={column} disabled={disabled} />
                </div>
              ))}
            </div>
          )}

          {/* 画像アップロード - フル幅 */}
          {imageFields.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: textareaFields.length > 0 ? '24px' : 0 }}>
              {imageFields.map(column => (
                <div key={column.column_name}>
                  <FieldFactory column={column} disabled={disabled} />
                </div>
              ))}
            </div>
          )}

          {/* テキストエリア - フル幅 */}
          {textareaFields.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280' }}>詳細項目</h4>
              {textareaFields.map(column => (
                <div key={column.column_name}>
                  <FieldFactory column={column} disabled={disabled} />
                </div>
              ))}
            </div>
          )}

        </>
      )}
    </div>
  );
};
