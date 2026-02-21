/**
 * SelectionFields: 選択系フィールドコンポーネント
 *
 * ラジオボタン・マルチセレクト・セレクトボックスのレンダリングを担当
 * FieldFactoryから委譲される
 */
import React from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ColumnWithLabel } from '../../services/metadataService';
import { parseOptions } from '../../utils/options';
import { getInputTypeFromDataType, inputBaseStyle, READONLY_FIELDS } from './fieldUtils';

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

interface SelectionFieldProps {
  column: ColumnWithLabel;
  disabled?: boolean;
}

/**
 * 選択系フィールドをレンダリング
 * radio, multi_select, enum select を処理。該当しない場合はnullを返す
 */
export const SelectionField: React.FC<SelectionFieldProps> = ({ column, disabled = false }) => {
  const { control, formState: { errors } } = useFormContext();
  const error = errors[column.column_name];

  const isReadOnly = READONLY_FIELDS.includes(column.column_name);
  const enumSource = column.options;
  const inputType = column.input_type || getInputTypeFromDataType(column.data_type);
  const isMasterRef = typeof enumSource === 'string' && enumSource.includes('マスター参照');

  // ─── radio with options（enumSourceあり、「未選択」なし）───
  if (inputType === 'radio' && enumSource) {
    const radioOptions = parseOptions(enumSource);
    return (
      <Controller
        name={column.column_name}
        control={control}
        render={({ field }) => (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', padding: '8px 0' }}>
            {radioOptions.map(option => {
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
                    style={{ width: '16px', height: '16px', accentColor: '#3B82F6' }}
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

  // ─── multi_select with options（enumSourceあり）───
  if (inputType === 'multi_select' && enumSource) {
    const multiOptions = parseOptions(enumSource);
    return (
      <Controller
        name={column.column_name}
        control={control}
        render={({ field }) => {
          const selectedValues: string[] = Array.isArray(field.value)
            ? field.value
            : (field.value ? String(field.value).split(',').map(v => v.trim()) : []);

          const toggleValue = (value: string) => {
            const newValues = selectedValues.includes(value)
              ? selectedValues.filter(v => v !== value)
              : [...selectedValues, value];
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
                      style={{ width: '16px', height: '16px', accentColor: '#3B82F6' }}
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

  // ─── enum select（USER-DEFINED型 or optionsあり、マスター参照除外）───
  if ((column.data_type === 'USER-DEFINED' || enumSource) &&
      enumSource &&
      !isMasterRef &&
      inputType !== 'radio' &&
      inputType !== 'multi_select') {
    const enumOptions = parseOptions(enumSource);
    if (enumOptions.length > 0) {
      const hasGroups = enumOptions.some(opt => opt.group);
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

  // ─── radio without options（「未選択」オプション付き）───
  if (inputType === 'radio') {
    const radioOptions = parseOptions(column.options);
    const radioOptionsWithEmpty = [{ value: '', label: '未選択' }, ...radioOptions];
    return (
      <Controller
        name={column.column_name}
        control={control}
        render={({ field }) => (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', padding: '8px 0' }}>
            {radioOptionsWithEmpty.map(option => {
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
                    style={{ width: '16px', height: '16px', accentColor: '#3B82F6' }}
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

  // ─── multi_select without options ───
  if (inputType === 'multi_select') {
    const multiOptions = parseOptions(column.options);
    return (
      <Controller
        name={column.column_name}
        control={control}
        render={({ field }) => {
          const selectedValues: string[] = Array.isArray(field.value)
            ? field.value
            : (field.value ? String(field.value).split(',').map(v => v.trim()) : []);

          const toggleValue = (value: string) => {
            const newValues = selectedValues.includes(value)
              ? selectedValues.filter(v => v !== value)
              : [...selectedValues, value];
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
                      style={{ width: '16px', height: '16px', accentColor: '#3B82F6' }}
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

  return null;
};
