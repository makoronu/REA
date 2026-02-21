/**
 * FieldGroup: フィールドグループコンポーネント
 *
 * 同じグループ名のフィールドをまとめて表示する
 * アコーディオン折りたたみ、フィールドタイプ別レイアウト、
 * 法規制自動取得、所在地グループのLocationField表示を担当
 */
import React, { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import { FieldFactory } from './FieldFactory';
import { LocationField } from './LocationField';
import { ZoningMapField } from './ZoningMapField';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';

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
  const { watch, setValue, getValues } = useFormContext();
  const [isLoadingZoning, setIsLoadingZoning] = useState(false);
  const [zoningMessage, setZoningMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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
      '法規制（自動取得）': '🔴'
    };
    return iconMap[name] || '📄';
  };

  const isAutoFetchGroup = groupName === '法規制（自動取得）';
  const isLocationGroup = groupName === '所在地';

  // 用途地域・都市計画区域自動取得ハンドラー
  const handleFetchZoning = async () => {
    let lat = getValues('latitude');
    let lng = getValues('longitude');

    if (!lat || !lng) {
      const prefecture = getValues('prefecture') || '';
      const city = getValues('city') || '';
      const address = getValues('address') || '';
      const addressDetail = getValues('address_detail') || '';
      const fullAddress = [prefecture, city, address, addressDetail].filter(Boolean).join('');

      if (!fullAddress) {
        setZoningMessage({ type: 'error', text: '住所を先に入力してください' });
        return;
      }

      setIsLoadingZoning(true);
      setZoningMessage({ type: 'success', text: '住所から座標を取得中...' });

      try {
        const geocodeRes = await fetch(`${API_BASE_URL}${API_PATHS.GEO.GEOCODE}?address=${encodeURIComponent(fullAddress)}`);
        const geocodeData = await geocodeRes.json();

        if (geocodeData.latitude && geocodeData.longitude) {
          lat = geocodeData.latitude;
          lng = geocodeData.longitude;
          setValue('latitude', lat, { shouldDirty: true });
          setValue('longitude', lng, { shouldDirty: true });
        } else {
          setZoningMessage({ type: 'error', text: '住所から座標を取得できませんでした' });
          setIsLoadingZoning(false);
          return;
        }
      } catch (err) {
        console.error('Geocode error:', err);
        setZoningMessage({ type: 'error', text: '住所から座標の取得に失敗しました' });
        setIsLoadingZoning(false);
        return;
      }
    } else {
      setIsLoadingZoning(true);
      setZoningMessage(null);
    }

    try {
      const [zoningRes, urbanRes] = await Promise.all([
        fetch(`${API_BASE_URL}${API_PATHS.GEO.ZONING}?lat=${lat}&lng=${lng}`),
        fetch(`${API_BASE_URL}${API_PATHS.GEO.URBAN_PLANNING}?lat=${lat}&lng=${lng}`)
      ]);

      const zoningData = await zoningRes.json();
      const urbanData = await urbanRes.json();

      const messages: string[] = [];

      if (zoningData.zones && zoningData.zones.length > 0) {
        const primary = zoningData.zones.find((z: any) => z.is_primary) || zoningData.zones[0];
        setValue('use_district', String(primary.zone_code), { shouldDirty: true });
        if (primary.building_coverage_ratio) {
          setValue('building_coverage_ratio', primary.building_coverage_ratio, { shouldDirty: true });
        }
        if (primary.floor_area_ratio) {
          setValue('floor_area_ratio', primary.floor_area_ratio, { shouldDirty: true });
        }
        messages.push(primary.zone_name);
      }

      if (urbanData.areas && urbanData.areas.length > 0) {
        const primaryUrban = urbanData.areas.find((a: any) => a.is_primary) || urbanData.areas[0];
        setValue('city_planning', String(primaryUrban.layer_no), { shouldDirty: true });
        messages.push(primaryUrban.area_type);
      }

      if (messages.length > 0) {
        setZoningMessage({ type: 'success', text: messages.join(' / ') });
      } else {
        setZoningMessage({ type: 'error', text: '該当するデータが見つかりませんでした' });
      }
    } catch (err: any) {
      console.error('Fetch error:', err);
      setZoningMessage({ type: 'error', text: err.message || 'データの取得に失敗しました' });
    } finally {
      setIsLoadingZoning(false);
    }
  };

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
          color: isAutoFetchGroup ? '#DC2626' : '#1A1A1A',
          margin: 0
        }}>
          {groupName}
        </h3>
        {collapsible && isCollapsed && (
          <span style={{ fontSize: '12px', color: '#9CA3AF', marginLeft: '8px' }}>
            ({visibleColumns.length}項目)
          </span>
        )}
        {isAutoFetchGroup && (
          <>
            <button
              type="button"
              onClick={handleFetchZoning}
              disabled={isLoadingZoning || disabled}
              style={{
                marginLeft: '12px',
                padding: '6px 12px',
                fontSize: '12px',
                fontWeight: 500,
                color: '#fff',
                backgroundColor: isLoadingZoning ? '#9CA3AF' : '#DC2626',
                border: 'none',
                borderRadius: '6px',
                cursor: isLoadingZoning || disabled ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {isLoadingZoning ? (
                <>
                  <span style={{
                    width: '12px',
                    height: '12px',
                    border: '2px solid #fff',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                  }} />
                  取得中...
                </>
              ) : (
                '位置情報から自動取得'
              )}
            </button>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          </>
        )}
      </div>

      {/* メッセージ表示 */}
      {isAutoFetchGroup && zoningMessage && !isCollapsed && (
        <div style={{
          marginBottom: '16px',
          padding: '10px 14px',
          borderRadius: '6px',
          fontSize: '13px',
          backgroundColor: zoningMessage.type === 'success' ? '#D1FAE5' : '#FEE2E2',
          color: zoningMessage.type === 'success' ? '#065F46' : '#991B1B',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span>{zoningMessage.text}</span>
          <button onClick={() => setZoningMessage(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px', lineHeight: 1, padding: '0 4px', color: 'inherit' }}>&times;</button>
        </div>
      )}

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

          {/* 用途地域マップ表示（法規制グループの場合） */}
          {isAutoFetchGroup && (
            <ZoningMapField />
          )}
        </>
      )}
    </div>
  );
};
