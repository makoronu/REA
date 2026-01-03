/**
 * 日付フォーマットユーティリティ
 *
 * ADR-0001に基づき、日付フォーマットを定数ファイルで一元管理。
 *
 * メタデータ駆動ではなく定数化の理由:
 * - 開発者のみが変更
 * - 変更頻度が年1回以下
 * - 外部仕様（HOMES等）に依存
 */

// 日付フォーマット定数
export const DATE_FORMATS = {
  // 日本語表示用
  JA_DATE: 'ja-JP',
  JA_DATETIME: 'ja-JP',

  // Intl.DateTimeFormatオプション
  DATE_OPTIONS: {
    year: 'numeric' as const,
    month: '2-digit' as const,
    day: '2-digit' as const,
  },
  DATETIME_OPTIONS: {
    year: 'numeric' as const,
    month: '2-digit' as const,
    day: '2-digit' as const,
    hour: '2-digit' as const,
    minute: '2-digit' as const,
  },
} as const;

/**
 * 日付を日本語形式で表示
 * @param date 日付文字列またはDateオブジェクト
 * @returns フォーマット済み日付文字列
 */
export function formatDateJa(date: string | Date | null | undefined): string {
  if (!date) return '';
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString(DATE_FORMATS.JA_DATE, DATE_FORMATS.DATE_OPTIONS);
}

/**
 * 日時を日本語形式で表示
 * @param date 日時文字列またはDateオブジェクト
 * @returns フォーマット済み日時文字列
 */
export function formatDateTimeJa(date: string | Date | null | undefined): string {
  if (!date) return '';
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString(DATE_FORMATS.JA_DATETIME, DATE_FORMATS.DATETIME_OPTIONS);
}
