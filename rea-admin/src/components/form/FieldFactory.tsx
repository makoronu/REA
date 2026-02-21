/**
 * FieldFactory: フィールドレンダラー
 *
 * カラム定義(ColumnWithLabel)から適切な入力フィールドを生成する
 * 選択系フィールドはSelectionFieldに委譲、郵便番号はPostalCodeFieldに委譲
 */
import React from 'react';
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
import { TransportationField } from './TransportationField';
import { BusStopsField } from './BusStopsField';
import { NearbyFacilitiesField } from './NearbyFacilitiesField';
import { parseOptions } from '../../utils/options';
import { PostalCodeField } from './PostalCodeField';
import { SelectionField } from './SelectionFields';
import { LegalChecklistField } from './LegalChecklistField';
import { getInputTypeFromDataType, inputBaseStyle, READONLY_FIELDS } from './fieldUtils';

interface FieldFactoryProps {
  column: ColumnWithLabel;
  disabled?: boolean;
}

export const FieldFactory: React.FC<FieldFactoryProps> = ({ column, disabled = false }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[column.column_name];

  // システム管理フィールドを非表示
  const hiddenFields = ['id', 'property_id', 'created_at', 'updated_at'];
  if (hiddenFields.includes(column.column_name)) return null;

  // 読み取り専用
  const isReadOnly = READONLY_FIELDS.includes(column.column_name);

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
    const isMasterRef = typeof enumSource === 'string' && enumSource.includes('マスター参照');

    // 選択系フィールド（radio, multi_select, enum select）はSelectionFieldに委譲
    if (inputType === 'radio' || inputType === 'multi_select') {
      return <SelectionField column={column} disabled={disabled || isReadOnly} />;
    }
    if ((column.data_type === 'USER-DEFINED' || enumSource) &&
        enumSource && !isMasterRef) {
      const enumOptions = parseOptions(enumSource);
      if (enumOptions.length > 0) {
        return <SelectionField column={column} disabled={disabled || isReadOnly} />;
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

      case 'transportation':
        return <TransportationField disabled={disabled || isReadOnly} />;

      case 'bus_stops':
        return <BusStopsField disabled={disabled || isReadOnly} />;

      case 'nearby_facilities':
        return <NearbyFacilitiesField disabled={disabled || isReadOnly} />;

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

      case 'json_legal_checklist':
        return <LegalChecklistField disabled={disabled || isReadOnly} />;

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

  // checkboxは特別扱い（ラベルなし）
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
