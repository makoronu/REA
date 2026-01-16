import React, { useState } from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import {
  RoadInfoEditor,
  FloorPlansEditor,
  FacilitiesEditor,
  TransportationEditor,
  RenovationsEditor,
  KeyValueEditor
} from './JsonEditors';
import { ImageUploader } from './ImageUploader';
import { geoService } from '../../services/geoService';
import { LocationField } from './LocationField';
import { TransportationField } from './TransportationField';
import { BusStopsField } from './BusStopsField';
import { NearbyFacilitiesField } from './NearbyFacilitiesField';
import { ZoningMapField } from './ZoningMapField';
import { API_BASE_URL } from '../../config';
import { API_PATHS } from '../../constants/apiPaths';
import { parseOptions } from '../../utils/options';

interface FieldFactoryProps {
  column: ColumnWithLabel;
  disabled?: boolean;
}

// 共通インプットスタイル - 枠線なし、下線のみ
const inputBaseStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px 0',
  fontSize: '15px',
  backgroundColor: 'transparent',
  border: 'none',
  borderBottom: '1.5px solid #E5E7EB',
  borderRadius: 0,
  outline: 'none',
  transition: 'border-color 150ms, box-shadow 150ms',
};

const selectStyle: React.CSSProperties = {
  ...inputBaseStyle,
  cursor: 'pointer',
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236B7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 0 center',
  backgroundSize: '20px',
  paddingRight: '28px',
};

// 郵便番号フィールド - 住所自動入力機能付き
const PostalCodeField: React.FC<{ column: ColumnWithLabel; disabled: boolean }> = ({ column, disabled }) => {
  const { control, setValue } = useFormContext();
  const [isSearching, setIsSearching] = useState(false);
  const [searchStatus, setSearchStatus] = useState<'idle' | 'success' | 'notfound'>('idle');

  const handlePostalCodeChange = async (value: string, fieldOnChange: (value: string) => void) => {
    fieldOnChange(value);

    // ハイフンを除去して7桁になったら自動検索
    const cleanCode = value.replace(/[^0-9]/g, '');
    if (cleanCode.length === 7) {
      setIsSearching(true);
      setSearchStatus('idle');

      const result = await geoService.searchByPostalCode(value);

      if (result) {
        // 住所フィールドに自動入力
        setValue('prefecture', result.address1, { shouldDirty: true });
        setValue('city', result.address2, { shouldDirty: true });
        setValue('address', result.address3, { shouldDirty: true });
        // 土地情報テーブルにもあれば
        setValue('land_prefecture', result.address1, { shouldDirty: true });
        setValue('land_city', result.address2, { shouldDirty: true });
        setValue('land_address', result.address3, { shouldDirty: true });
        setSearchStatus('success');
      } else {
        setSearchStatus('notfound');
      }

      setIsSearching(false);

      // 3秒後にステータスをリセット
      setTimeout(() => setSearchStatus('idle'), 3000);
    }
  };

  return (
    <Controller
      name={column.column_name}
      control={control}
      render={({ field }) => (
        <div style={{ position: 'relative' }}>
          <input
            {...field}
            type="text"
            id={column.column_name}
            placeholder="123-4567"
            disabled={disabled}
            onChange={(e) => handlePostalCodeChange(e.target.value, field.onChange)}
            style={{
              width: '100%',
              padding: '12px 0',
              paddingRight: '100px',
              fontSize: '15px',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: '1.5px solid #E5E7EB',
              borderRadius: 0,
              outline: 'none',
              transition: 'border-color 150ms',
            }}
            onFocus={(e) => e.target.style.borderBottomColor = '#3B82F6'}
            onBlur={(e) => e.target.style.borderBottomColor = '#E5E7EB'}
          />
          {/* ステータス表示 */}
          <div style={{
            position: 'absolute',
            right: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            {isSearching && (
              <span style={{ color: '#3B82F6' }}>検索中...</span>
            )}
            {searchStatus === 'success' && (
              <span style={{ color: '#10B981' }}>✓ 住所入力済</span>
            )}
            {searchStatus === 'notfound' && (
              <span style={{ color: '#F59E0B' }}>見つかりません</span>
            )}
          </div>
        </div>
      )}
    />
  );
};

// データ型から入力タイプを推測
const getInputTypeFromDataType = (dataType?: string): string => {
  if (!dataType) return 'text';
  const lowerType = dataType.toLowerCase();
  if (lowerType.includes('int') || lowerType.includes('numeric') || lowerType.includes('decimal')) return 'number';
  if (lowerType.includes('bool')) return 'checkbox';
  if (lowerType.includes('date') && !lowerType.includes('datetime')) return 'date';
  if (lowerType.includes('datetime') || lowerType.includes('timestamp')) return 'datetime';
  return 'text';
};

export const FieldFactory: React.FC<FieldFactoryProps> = ({ column, disabled = false }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[column.column_name];

  // システム管理フィールドを非表示
  const hiddenFields = ['id', 'property_id', 'created_at', 'updated_at'];
  if (hiddenFields.includes(column.column_name)) return null;

  // 読み取り専用
  const readOnlyFields = ['homes_record_id'];
  const isReadOnly = readOnlyFields.includes(column.column_name);

  // ラベル
  const renderLabel = () => (
    <label
      htmlFor={column.column_name}
      style={{
        display: 'block',
        fontSize: '13px',
        fontWeight: 500,
        color: '#6B7280',
        marginBottom: '4px',
      }}
    >
      {column.label_ja || column.column_name}
      {column.is_required && <span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>}
      {isReadOnly && <span style={{ color: '#9CA3AF', marginLeft: '8px', fontSize: '11px' }}>(読み取り専用)</span>}
    </label>
  );

  // ヘルプテキスト
  const renderHelpText = () => {
    if (!column.help_text && !column.description) return null;
    return (
      <p style={{ marginTop: '4px', fontSize: '12px', color: '#9CA3AF' }}>
        {column.help_text || column.description}
      </p>
    );
  };

  // エラー
  const renderError = () => {
    if (!error) return null;
    const errorMessage = typeof error === 'object' && 'message' in error
      ? String(error.message)
      : 'このフィールドは必須です';
    return (
      <p style={{ marginTop: '4px', fontSize: '12px', color: '#EF4444' }}>
        {errorMessage}
      </p>
    );
  };

  // フィールドレンダリング
  const renderField = () => {
    const enumSource = column.options;
    const inputType = column.input_type || getInputTypeFromDataType(column.data_type);

    // マスター参照チェック（文字列の場合のみ）
    const isMasterRef = typeof enumSource === 'string' && enumSource.includes('マスター参照');

    // input_typeがradioの場合は先にradioを返す
    if (inputType === 'radio' && enumSource) {
      const radioOptions = parseOptions(enumSource);
      return (
        <Controller
          name={column.column_name}
          control={control}
          render={({ field }) => (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '8px 0' }}>
              {radioOptions.map(option => {
                // DBから数値で返ってくる場合も文字列と比較できるように
                const isSelected = String(field.value) === String(option.value);
                return (
                  <label
                    key={option.value}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                      gap: '6px',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      backgroundColor: isSelected ? '#EFF6FF' : '#F9FAFB',
                      border: isSelected ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <input
                      type="radio"
                      name={column.column_name}
                      value={option.value}
                      checked={isSelected}
                      onChange={() => field.onChange(option.value)}
                      disabled={disabled || isReadOnly}
                      style={{
                        width: '16px',
                        height: '16px',
                        accentColor: '#3B82F6',
                      }}
                    />
                    <span style={{ fontSize: '14px', color: isSelected ? '#1D4ED8' : '#374151' }}>
                      {option.label}
                    </span>
                  </label>
                );
              })}
            </div>
          )}
        />
      );
    }

    // input_typeがmulti_selectの場合は先にmulti_selectを返す
    if (inputType === 'multi_select' && enumSource) {
      const multiOptions = parseOptions(enumSource);
      return (
        <Controller
          name={column.column_name}
          control={control}
          render={({ field }) => {
            // 値を配列として扱う（カンマ区切り文字列も対応）
            const selectedValues: string[] = Array.isArray(field.value)
              ? field.value
              : (field.value ? String(field.value).split(',').map(v => v.trim()) : []);

            const toggleValue = (value: string) => {
              const newValues = selectedValues.includes(value)
                ? selectedValues.filter(v => v !== value)
                : [...selectedValues, value];
              // カンマ区切り文字列で保存（DB互換性のため）
              field.onChange(newValues.join(','));
            };

            return (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '8px 0' }}>
                {multiOptions.map(option => {
                  const isSelected = selectedValues.includes(option.value);
                  return (
                    <label
                      key={option.value}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '6px',
                        backgroundColor: isSelected ? '#DBEAFE' : '#F9FAFB',
                        border: isSelected ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleValue(option.value)}
                        disabled={disabled || isReadOnly}
                        style={{
                          width: '16px',
                          height: '16px',
                          accentColor: '#3B82F6',
                        }}
                      />
                      <span style={{ fontSize: '14px', color: isSelected ? '#1D4ED8' : '#374151' }}>
                        {option.label}
                      </span>
                    </label>
                  );
                })}
              </div>
            );
          }}
        />
      );
    }

    // ENUM型セレクト（radioでもmulti_selectでもない場合）
    if ((column.data_type === 'USER-DEFINED' || enumSource) &&
        enumSource &&
        !isMasterRef &&
        inputType !== 'radio' &&
        inputType !== 'multi_select') {
      const enumOptions = parseOptions(enumSource);
      if (enumOptions.length > 0) {
        // グループがあるかチェック
        const hasGroups = enumOptions.some(opt => opt.group);

        // グループ別にまとめる
        const groupedOptions = hasGroups
          ? enumOptions.reduce((acc, opt) => {
              const group = opt.group || 'その他';
              if (!acc[group]) acc[group] = [];
              acc[group].push(opt);
              return acc;
            }, {} as Record<string, typeof enumOptions>)
          : null;

        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <select
                {...field}
                id={column.column_name}
                disabled={disabled || isReadOnly}
                style={{
                  ...selectStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              >
                <option value="">選択してください</option>
                {groupedOptions ? (
                  // グループ別表示
                  Object.entries(groupedOptions).map(([groupName, options]) => (
                    <optgroup key={groupName} label={groupName}>
                      {options.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </optgroup>
                  ))
                ) : (
                  // フラット表示
                  enumOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))
                )}
              </select>
            )}
          />
        );
      }
    }

    switch (inputType) {
      case 'textarea':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <textarea
                {...field}
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                rows={3}
                style={{
                  ...inputBaseStyle,
                  resize: 'vertical',
                  minHeight: '80px',
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'number':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="number"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                onChange={(e) => {
                  const value = e.target.value;
                  field.onChange(value === '' ? null : Number(value));
                }}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'checkbox':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <label style={{
                display: 'flex',
                alignItems: 'center',
                cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                padding: '8px 0',
              }}>
                <input
                  {...field}
                  type="checkbox"
                  id={column.column_name}
                  disabled={disabled || isReadOnly}
                  checked={field.value || false}
                  style={{
                    width: '18px',
                    height: '18px',
                    accentColor: '#3B82F6',
                    marginRight: '10px',
                  }}
                />
                <span style={{ fontSize: '14px', color: '#374151' }}>
                  {column.label_ja || column.column_name}
                </span>
              </label>
            )}
          />
        );

      case 'radio':
        const radioOptions = parseOptions(column.options);
        // 「未選択」オプションを先頭に追加
        const radioOptionsWithEmpty = [{ value: '', label: '未選択' }, ...radioOptions];
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', padding: '8px 0' }}>
                {radioOptionsWithEmpty.map(option => {
                  // DBから数値で返ってくる場合も文字列と比較できるように
                  const isSelected = option.value === ''
                    ? (!field.value || field.value === '')
                    : String(field.value) === String(option.value);
                  return (
                    <label
                      key={option.value || '_empty'}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '6px',
                        backgroundColor: isSelected ? '#EFF6FF' : '#F9FAFB',
                        border: isSelected ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <input
                        type="radio"
                        name={column.column_name}
                        value={option.value}
                        checked={isSelected}
                        onChange={() => field.onChange(option.value)}
                        disabled={disabled || isReadOnly}
                        style={{
                          width: '16px',
                          height: '16px',
                          accentColor: '#3B82F6',
                        }}
                      />
                      <span style={{ fontSize: '14px', color: isSelected ? '#1D4ED8' : '#374151' }}>
                        {option.label}
                      </span>
                    </label>
                  );
                })}
              </div>
            )}
          />
        );

      case 'multi_select':
        const multiOptions = parseOptions(column.options);
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => {
              // 値を配列として扱う（カンマ区切り文字列も対応）
              const selectedValues: string[] = Array.isArray(field.value)
                ? field.value
                : (field.value ? String(field.value).split(',').map(v => v.trim()) : []);

              const toggleValue = (value: string) => {
                const newValues = selectedValues.includes(value)
                  ? selectedValues.filter(v => v !== value)
                  : [...selectedValues, value];
                // カンマ区切り文字列で保存（DB互換性のため）
                field.onChange(newValues.join(','));
              };

              return (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '8px 0' }}>
                  {multiOptions.map(option => {
                    const isSelected = selectedValues.includes(option.value);
                    return (
                      <label
                        key={option.value}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          cursor: disabled || isReadOnly ? 'not-allowed' : 'pointer',
                          gap: '6px',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          backgroundColor: isSelected ? '#DBEAFE' : '#F9FAFB',
                          border: isSelected ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleValue(option.value)}
                          disabled={disabled || isReadOnly}
                          style={{
                            width: '16px',
                            height: '16px',
                            accentColor: '#3B82F6',
                          }}
                        />
                        <span style={{ fontSize: '14px', color: isSelected ? '#1D4ED8' : '#374151' }}>
                          {option.label}
                        </span>
                      </label>
                    );
                  })}
                </div>
              );
            }}
          />
        );

      case 'date':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="date"
                id={column.column_name}
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'datetime':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="datetime-local"
                id={column.column_name}
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'email':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="email"
                id={column.column_name}
                placeholder={column.placeholder || 'example@example.com'}
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'tel':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="tel"
                id={column.column_name}
                placeholder={column.placeholder || '090-1234-5678'}
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );

      case 'postal_code':
        return <PostalCodeField column={column} disabled={disabled || isReadOnly} />;

      // 交通（最寄駅）フィールド
      case 'transportation':
        return <TransportationField disabled={disabled || isReadOnly} />;

      // バス停フィールド
      case 'bus_stops':
        return <BusStopsField disabled={disabled || isReadOnly} />;

      // 近隣施設フィールド
      case 'nearby_facilities':
        return <NearbyFacilitiesField disabled={disabled || isReadOnly} />;

      // JSON専用フィールド
      case 'json_road_info':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <RoadInfoEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'json_floor_plans':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <FloorPlansEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'json_facilities':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <FacilitiesEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'json_transportation':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <TransportationEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'json_renovations':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <RenovationsEditor
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'images':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <ImageUploader
                value={field.value || []}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'key_value':
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <KeyValueEditor
                value={field.value || {}}
                onChange={field.onChange}
                disabled={disabled || isReadOnly}
              />
            )}
          />
        );

      case 'text':
      default:
        return (
          <Controller
            name={column.column_name}
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="text"
                id={column.column_name}
                placeholder={column.placeholder}
                disabled={disabled || isReadOnly}
                style={{
                  ...inputBaseStyle,
                  borderBottomColor: error ? '#EF4444' : '#E5E7EB',
                  backgroundColor: isReadOnly ? '#F9FAFB' : 'transparent',
                }}
                onFocus={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#3B82F6'}
                onBlur={(e) => e.target.style.borderBottomColor = error ? '#EF4444' : '#E5E7EB'}
              />
            )}
          />
        );
    }
  };

  // checkboxは特別扱い
  if (column.input_type === 'checkbox' || (column.data_type && column.data_type.toLowerCase().includes('bool'))) {
    return (
      <div style={{ marginBottom: '16px' }}>
        {renderField()}
        {renderHelpText()}
        {renderError()}
      </div>
    );
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      {renderLabel()}
      {renderField()}
      {renderHelpText()}
      {renderError()}
    </div>
  );
};

// =================================================================
// FieldGroup - 枠線なし
// =================================================================

interface FieldGroupProps {
  groupName: string;
  columns: ColumnWithLabel[];
  disabled?: boolean;
  collapsible?: boolean;  // アコーディオン機能（折りたたみ可能）
  defaultCollapsed?: boolean;  // 初期状態で折りたたみ
}

export const FieldGroup: React.FC<FieldGroupProps> = ({
  groupName,
  columns,
  disabled = false,
  collapsible = false,
  defaultCollapsed = false,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const { watch, setValue, getValues } = useFormContext();
  const [isLoadingZoning, setIsLoadingZoning] = useState(false);
  const [zoningMessage, setZoningMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // 引渡時期の値を監視（条件付き表示用）
  const deliveryTiming = watch('delivery_timing');

  // 条件付き表示フィールドのフィルタリング
  const shouldShowField = (columnName: string): boolean => {
    // delivery_date は「3:期日指定」の場合のみ表示
    if (columnName === 'delivery_date') {
      return deliveryTiming === '3:期日指定';
    }
    // move_in_consultation は「2:相談」の場合のみ表示
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
  const getGroupIcon = (groupName: string) => {
    const iconMap: Record<string, string> = {
      '所在地': '📍', '交通': '🚃', '学区': '🏫', '周辺施設': '🏪',
      '基本情報': '🏠', '基本・取引情報': '🏠', '価格情報': '💰',
      '契約条件': '📋', '元請会社': '🏢', '土地情報': '🗺️',
      '建物情報': '🏗️', '設備・周辺環境': '🔧', '画像情報': '📸',
      '管理情報': '⚙️', 'システム': '⚙️',
      '法規制（自動取得）': '🔴'
    };
    return iconMap[groupName] || '📄';
  };

  // 自動取得グループかどうか（ラベルを赤く表示）
  const isAutoFetchGroup = groupName === '法規制（自動取得）';

  // 所在地グループかどうか
  const isLocationGroup = groupName === '所在地';

  // 用途地域・都市計画区域自動取得ハンドラー
  const handleFetchZoning = async () => {
    let lat = getValues('latitude');
    let lng = getValues('longitude');

    console.log('handleFetchZoning called, lat:', lat, 'lng:', lng);

    // 緯度経度がなければ、住所からジオコードして取得
    if (!lat || !lng) {
      const prefecture = getValues('prefecture') || '';
      const city = getValues('city') || '';
      const address = getValues('address') || '';
      const addressDetail = getValues('address_detail') || '';
      const fullAddress = [prefecture, city, address, addressDetail].filter(Boolean).join('');

      if (!fullAddress) {
        setZoningMessage({ type: 'error', text: '住所を先に入力してください' });
        setTimeout(() => setZoningMessage(null), 5000);
        return;
      }

      setIsLoadingZoning(true);
      setZoningMessage({ type: 'success', text: '住所から座標を取得中...' });

      try {
        // ジオコードで緯度経度を取得
        const geocodeRes = await fetch(`${API_BASE_URL}${API_PATHS.GEO.GEOCODE}?address=${encodeURIComponent(fullAddress)}`);
        const geocodeData = await geocodeRes.json();

        if (geocodeData.latitude && geocodeData.longitude) {
          lat = geocodeData.latitude;
          lng = geocodeData.longitude;
          // フォームに緯度経度をセット
          setValue('latitude', lat, { shouldDirty: true });
          setValue('longitude', lng, { shouldDirty: true });
          console.log('Geocoded:', lat, lng);
        } else {
          setZoningMessage({ type: 'error', text: '住所から座標を取得できませんでした' });
          setIsLoadingZoning(false);
          setTimeout(() => setZoningMessage(null), 5000);
          return;
        }
      } catch (err) {
        console.error('Geocode error:', err);
        setZoningMessage({ type: 'error', text: '住所から座標の取得に失敗しました' });
        setIsLoadingZoning(false);
        setTimeout(() => setZoningMessage(null), 5000);
        return;
      }
    } else {
      setIsLoadingZoning(true);
      setZoningMessage(null);
    }

    try {
      console.log('Fetching zoning data for:', lat, lng);

      // 用途地域と都市計画区域を同時に取得
      const [zoningRes, urbanRes] = await Promise.all([
        fetch(`${API_BASE_URL}${API_PATHS.GEO.ZONING}?lat=${lat}&lng=${lng}`),
        fetch(`${API_BASE_URL}${API_PATHS.GEO.URBAN_PLANNING}?lat=${lat}&lng=${lng}`)
      ]);

      const zoningData = await zoningRes.json();
      const urbanData = await urbanRes.json();

      console.log('Zoning data:', zoningData);
      console.log('Urban data:', urbanData);

      const messages: string[] = [];

      // 用途地域を設定
      if (zoningData.zones && zoningData.zones.length > 0) {
        const primary = zoningData.zones.find((z: any) => z.is_primary) || zoningData.zones[0];

        console.log('Setting use_district to:', primary.zone_code);
        setValue('use_district', String(primary.zone_code), { shouldDirty: true });
        if (primary.building_coverage_ratio) {
          setValue('building_coverage_ratio', primary.building_coverage_ratio, { shouldDirty: true });
        }
        if (primary.floor_area_ratio) {
          setValue('floor_area_ratio', primary.floor_area_ratio, { shouldDirty: true });
        }

        messages.push(primary.zone_name);
      }

      // 都市計画区域を設定
      if (urbanData.areas && urbanData.areas.length > 0) {
        const primaryUrban = urbanData.areas.find((a: any) => a.is_primary) || urbanData.areas[0];

        console.log('Urban planning API response:', urbanData);
        console.log('Primary urban area:', primaryUrban);
        console.log('Setting city_planning to:', String(primaryUrban.layer_no), '(area_type:', primaryUrban.area_type, ')');

        // city_planningカラムに設定（layer_no: 1=市街化区域, 2=市街化調整区域）
        setValue('city_planning', String(primaryUrban.layer_no), { shouldDirty: true });

        // 設定後の値を確認
        setTimeout(() => {
          const currentValue = getValues('city_planning');
          console.log('city_planning after setValue:', currentValue);
        }, 100);

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
      setTimeout(() => setZoningMessage(null), 5000);
    }
  };

  // 所在地グループの場合、緯度・経度フィールドを通常表示から除外
  const locationFieldNames = ['latitude', 'longitude'];
  const filteredRegularFields = isLocationGroup
    ? regularFields.filter(col => !locationFieldNames.includes(col.column_name))
    : regularFields;

  return (
    <div style={{
      marginBottom: '32px',
      padding: '24px',
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
        {/* アコーディオン矢印 */}
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
        {/* 折りたたみ時のフィールド数表示 */}
        {collapsible && isCollapsed && (
          <span style={{
            fontSize: '12px',
            color: '#9CA3AF',
            marginLeft: '8px',
          }}>
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
        }}>
          {zoningMessage.text}
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
              gap: '24px',
              marginBottom: isLocationGroup || jsonFields.length > 0 || checkboxFields.length > 0 || textareaFields.length > 0 ? '24px' : 0,
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
            <LocationField disabled={disabled} />
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
