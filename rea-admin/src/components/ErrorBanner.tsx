import { useEffect, useRef } from 'react';
import { MESSAGE_TIMEOUT_MS } from '../constants';

interface ErrorBannerProps {
  type: 'error' | 'success';
  message: string;
  onClose: () => void;
}

/**
 * 共通メッセージバナー
 * - error: 画面上部固定・消えない・コピーボタン付き・×で手動閉じ
 * - success: 自動消去（MESSAGE_TIMEOUT_MS後）
 */
export default function ErrorBanner({ type, message, onClose }: ErrorBannerProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (type === 'success') {
      timerRef.current = setTimeout(onClose, MESSAGE_TIMEOUT_MS);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [type, onClose]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
    } catch {
      // clipboard API unavailable
    }
  };

  if (type === 'error') {
    return (
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        padding: '12px 16px',
        backgroundColor: '#FEF2F2',
        border: '1px solid #F87171',
        color: '#B91C1C',
        borderRadius: '6px',
        marginBottom: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
      }}>
        <span style={{ flex: 1, wordBreak: 'break-word' }}>{message}</span>
        <div style={{ display: 'flex', gap: '4px', flexShrink: 0 }}>
          <button
            onClick={handleCopy}
            title="コピー"
            style={{
              background: 'none',
              border: '1px solid #F87171',
              borderRadius: '4px',
              padding: '2px 8px',
              cursor: 'pointer',
              color: '#B91C1C',
              fontSize: '12px',
            }}
          >
            コピー
          </button>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#B91C1C',
              fontSize: '18px',
              lineHeight: 1,
              padding: '0 4px',
            }}
          >
            &times;
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      padding: '12px 16px',
      backgroundColor: '#F0FDF4',
      border: '1px solid #4ADE80',
      color: '#166534',
      borderRadius: '6px',
      marginBottom: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      <span>{message}</span>
      <button
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: '#166534',
          fontSize: '18px',
          lineHeight: 1,
          padding: '0 4px',
        }}
      >
        &times;
      </button>
    </div>
  );
}
