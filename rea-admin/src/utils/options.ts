/**
 * 選択肢パース共通ユーティリティ
 *
 * 重要: 全コンポーネントでこのファイルの関数を使用すること
 * 独自のパース処理を書くことは禁止
 *
 * 対応形式:
 * 1. OptionType[] - 正規形式（そのまま返す）
 * 2. 文字列 "1:ラベル1,2:ラベル2" - 旧形式（変換して返す）
 * 3. JSON文字列 '[{"value":"1","label":"ラベル1"}]' - 変換して返す
 * 4. null/undefined - 空配列を返す
 */

import { OptionType, isOptionTypeArray } from '../types/metadata';

/**
 * 選択肢をOptionType[]に変換する（唯一のパース関数）
 *
 * @param options - パース対象（配列、文字列、null等）
 * @returns OptionType[] - 常に配列を返す
 *
 * @example
 * // OptionType[]（そのまま）
 * parseOptions([{value: '1', label: 'ラベル1'}])
 * // => [{value: '1', label: 'ラベル1'}]
 *
 * @example
 * // 文字列形式
 * parseOptions('1:ラベル1,2:ラベル2')
 * // => [{value: '1', label: 'ラベル1'}, {value: '2', label: 'ラベル2'}]
 *
 * @example
 * // JSON文字列
 * parseOptions('[{"value":"1","label":"ラベル1"}]')
 * // => [{value: '1', label: 'ラベル1'}]
 *
 * @example
 * // null/undefined
 * parseOptions(null)
 * // => []
 */
export function parseOptions(options: unknown): OptionType[] {
  // null/undefined → 空配列
  if (options === null || options === undefined) {
    return [];
  }

  // 既にOptionType[]の場合 → そのまま返す
  if (isOptionTypeArray(options)) {
    return options;
  }

  // 配列の場合（OptionType[]以外の配列）→ 変換を試みる
  if (Array.isArray(options)) {
    return options
      .filter((item): item is Record<string, unknown> => item !== null && item !== undefined)
      .map((opt) => {
        if (typeof opt === 'object') {
          return {
            value: String(opt.value ?? opt.id ?? opt.code ?? ''),
            label: String(opt.label ?? opt.name ?? opt.option_value ?? opt.value ?? ''),
            group: opt.group ? String(opt.group) : opt.group_name ? String(opt.group_name) : undefined,
            color: opt.color ? String(opt.color) : undefined,
            bg: opt.bg ? String(opt.bg) : undefined,
          };
        }
        // プリミティブ値の場合
        const str = String(opt);
        return { value: str, label: str };
      });
  }

  // 文字列の場合
  if (typeof options === 'string') {
    const trimmed = options.trim();

    // 空文字列 → 空配列
    if (trimmed === '') {
      return [];
    }

    // JSON文字列かどうか判定
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) {
          return parseOptions(parsed); // 再帰で配列処理
        }
      } catch {
        // JSONパース失敗 → カンマ区切りとして処理
      }
    }

    // カンマ区切り形式 "1:ラベル1,2:ラベル2"
    const items = trimmed.split(',').map((item) => item.trim()).filter(Boolean);
    return items.map((item) => {
      const colonIndex = item.indexOf(':');
      if (colonIndex > 0) {
        const code = item.substring(0, colonIndex).trim();
        const label = item.substring(colonIndex + 1).trim();
        return { value: code, label: label || code };
      }
      // コロンなし → value = label
      return { value: item, label: item };
    });
  }

  // その他の型 → 空配列（エラーにしない）
  console.warn('[parseOptions] Unexpected options type:', typeof options, options);
  return [];
}

/**
 * 選択肢から値に対応するラベルを取得
 *
 * @param options - 選択肢配列
 * @param value - 検索する値
 * @returns ラベル文字列（見つからない場合はvalue自体を返す）
 */
export function getOptionLabel(options: OptionType[], value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return '';
  }
  const stringValue = String(value);
  const option = options.find((opt) => opt.value === stringValue);
  return option?.label ?? stringValue;
}

/**
 * 複数値から対応するラベル配列を取得
 *
 * @param options - 選択肢配列
 * @param values - 検索する値の配列（またはカンマ区切り文字列）
 * @returns ラベル配列
 */
export function getOptionLabels(
  options: OptionType[],
  values: string | string[] | number[] | null | undefined
): string[] {
  if (values === null || values === undefined) {
    return [];
  }

  let valueArray: string[];

  if (typeof values === 'string') {
    valueArray = values.split(',').map((v) => v.trim()).filter(Boolean);
  } else if (Array.isArray(values)) {
    valueArray = values.map(String);
  } else {
    return [];
  }

  return valueArray.map((v) => getOptionLabel(options, v));
}

/**
 * 選択肢をグループ別に分類
 *
 * @param options - 選択肢配列
 * @returns グループ名をキーとしたRecord
 */
export function groupOptions(options: OptionType[]): Record<string, OptionType[]> {
  return options.reduce((acc, option) => {
    const groupName = option.group ?? 'その他';
    if (!acc[groupName]) {
      acc[groupName] = [];
    }
    acc[groupName].push(option);
    return acc;
  }, {} as Record<string, OptionType[]>);
}

/**
 * 選択肢を値でフィルタリング
 *
 * @param options - 選択肢配列
 * @param filterFn - フィルター関数
 * @returns フィルタリングされた選択肢配列
 */
export function filterOptions(
  options: OptionType[],
  filterFn: (option: OptionType) => boolean
): OptionType[] {
  return options.filter(filterFn);
}

/**
 * 選択肢が空かどうかを判定
 *
 * @param options - 選択肢（パース前でもOK）
 * @returns 空の場合true
 */
export function isOptionsEmpty(options: unknown): boolean {
  const parsed = parseOptions(options);
  return parsed.length === 0;
}
