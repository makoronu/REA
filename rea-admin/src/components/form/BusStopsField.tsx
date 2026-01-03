import React, { useState } from 'react';
import { useFormContext, Controller } from 'react-hook-form';

interface BusStop {
  bus_stop_name: string;
  line_name: string;
  walk_minutes: number;
}

interface BusStopsFieldProps {
  disabled?: boolean;
}

// バス路線なしフラグ検出
const isNoBus = (v: any): boolean => {
  return v && typeof v === 'object' && !Array.isArray(v) && v.no_bus === true;
};

export const BusStopsField: React.FC<BusStopsFieldProps> = ({ disabled = false }) => {
  const { control } = useFormContext();
  const [newStop, setNewStop] = useState({ bus_stop_name: '', line_name: '', walk_minutes: '' });

  return (
    <Controller
      name="bus_stops"
      control={control}
      defaultValue={[]}
      render={({ field }) => {
        const noBus = isNoBus(field.value);
        const stops: BusStop[] = noBus ? [] : (Array.isArray(field.value) ? field.value : []);

        const handleNoBusChange = (checked: boolean) => {
          if (checked) {
            field.onChange({ no_bus: true });
          } else {
            field.onChange([]);
          }
        };

        const addStop = () => {
          if (!newStop.bus_stop_name) return;
          if (stops.length >= 5) return;

          field.onChange([...stops, {
            bus_stop_name: newStop.bus_stop_name,
            line_name: newStop.line_name,
            walk_minutes: parseInt(newStop.walk_minutes) || 0
          }]);
          setNewStop({ bus_stop_name: '', line_name: '', walk_minutes: '' });
        };

        const removeStop = (index: number) => {
          field.onChange(stops.filter((_, i) => i !== index));
        };

        const updateWalkMinutes = (index: number, minutes: number) => {
          const newStops = [...stops];
          newStops[index] = { ...newStops[index], walk_minutes: minutes };
          field.onChange(newStops);
        };

        return (
          <div style={{ marginTop: '8px' }}>
            {/* バス路線なしチェックボックス */}
            <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: noBus ? '#FEF3C7' : '#F9FAFB', borderRadius: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: disabled ? 'not-allowed' : 'pointer' }}>
                <input
                  type="checkbox"
                  checked={noBus}
                  onChange={(e) => handleNoBusChange(e.target.checked)}
                  disabled={disabled}
                  style={{ width: '18px', height: '18px', cursor: disabled ? 'not-allowed' : 'pointer' }}
                />
                <span style={{ fontWeight: 500 }}>バス路線なし</span>
              </label>
              {noBus && (
                <p style={{ fontSize: '12px', color: '#92400E', marginTop: '8px', marginLeft: '26px' }}>
                  バス路線がない物件として登録されます
                </p>
              )}
            </div>

            {!noBus && (
            <>
            {/* 登録済みバス停 */}
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                登録済み（{stops.length}/5）
              </div>
              {stops.length === 0 ? (
                <p style={{ fontSize: '13px', color: '#9CA3AF' }}>バス停が登録されていません</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {stops.map((stop, index) => (
                    <div
                      key={`${stop.bus_stop_name}-${index}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '10px 12px',
                        backgroundColor: '#F9FAFB',
                        borderRadius: '8px',
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <span style={{ fontWeight: 500 }}>{stop.bus_stop_name}</span>
                        {stop.line_name && (
                          <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '8px' }}>
                            （{stop.line_name}）
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '13px', color: '#6B7280' }}>徒歩</span>
                        <input
                          type="number"
                          value={stop.walk_minutes}
                          onChange={(e) => updateWalkMinutes(index, parseInt(e.target.value) || 0)}
                          disabled={disabled}
                          min="1"
                          style={{
                            width: '60px',
                            padding: '4px 8px',
                            fontSize: '13px',
                            border: '1px solid #E5E7EB',
                            borderRadius: '4px',
                            textAlign: 'right',
                          }}
                        />
                        <span style={{ fontSize: '13px', color: '#6B7280' }}>分</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeStop(index)}
                        disabled={disabled}
                        style={{
                          padding: '4px',
                          backgroundColor: 'transparent',
                          border: 'none',
                          cursor: disabled ? 'not-allowed' : 'pointer',
                          color: '#EF4444',
                        }}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 追加フォーム */}
            <div style={{ padding: '12px', backgroundColor: '#FEF3C7', borderRadius: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#92400E', marginBottom: '8px' }}>
                バス停を追加
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                <input
                  type="text"
                  value={newStop.bus_stop_name}
                  onChange={(e) => setNewStop({ ...newStop, bus_stop_name: e.target.value })}
                  placeholder="バス停名"
                  disabled={disabled || stops.length >= 5}
                  style={{
                    flex: 1,
                    minWidth: '120px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #FCD34D',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <input
                  type="text"
                  value={newStop.line_name}
                  onChange={(e) => setNewStop({ ...newStop, line_name: e.target.value })}
                  placeholder="路線名（任意）"
                  disabled={disabled || stops.length >= 5}
                  style={{
                    flex: 1,
                    minWidth: '120px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #FCD34D',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <input
                  type="number"
                  value={newStop.walk_minutes}
                  onChange={(e) => setNewStop({ ...newStop, walk_minutes: e.target.value })}
                  placeholder="徒歩(分)"
                  disabled={disabled || stops.length >= 5}
                  min="1"
                  style={{
                    width: '80px',
                    padding: '8px 12px',
                    fontSize: '13px',
                    border: '1px solid #FCD34D',
                    borderRadius: '6px',
                    backgroundColor: '#fff',
                  }}
                />
                <button
                  type="button"
                  onClick={addStop}
                  disabled={disabled || !newStop.bus_stop_name || stops.length >= 5}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    backgroundColor: newStop.bus_stop_name && stops.length < 5 ? '#F59E0B' : '#D1D5DB',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: disabled || !newStop.bus_stop_name || stops.length >= 5 ? 'not-allowed' : 'pointer',
                  }}
                >
                  追加
                </button>
              </div>
            </div>
            </>
            )}
          </div>
        );
      }}
    />
  );
};

export default BusStopsField;
