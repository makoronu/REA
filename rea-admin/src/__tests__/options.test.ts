/**
 * options.ts のユニットテスト
 *
 * 実行方法（vitest導入後）:
 *   npm install -D vitest
 *   npx vitest run
 *
 * または手動実行:
 *   npx ts-node src/__tests__/options.test.ts
 */

import { parseOptions, getOptionLabel, getOptionLabels, groupOptions, isOptionsEmpty } from '../utils/options';

// テストケース定義
const testCases = [
  // 正常系：OptionType[]
  {
    name: 'OptionType[] をそのまま返す',
    input: [{ value: '1', label: 'ラベル1' }, { value: '2', label: 'ラベル2' }],
    expected: [{ value: '1', label: 'ラベル1' }, { value: '2', label: 'ラベル2' }],
  },

  // 正常系：カンマ区切り文字列
  {
    name: 'カンマ区切り文字列をパース',
    input: '1:ラベル1,2:ラベル2',
    expected: [{ value: '1', label: 'ラベル1' }, { value: '2', label: 'ラベル2' }],
  },

  // 正常系：JSON文字列
  {
    name: 'JSON文字列をパース',
    input: '[{"value":"1","label":"ラベル1"}]',
    expected: [{ value: '1', label: 'ラベル1' }],
  },

  // エッジケース：null
  {
    name: 'null → 空配列',
    input: null,
    expected: [],
  },

  // エッジケース：undefined
  {
    name: 'undefined → 空配列',
    input: undefined,
    expected: [],
  },

  // エッジケース：空文字列
  {
    name: '空文字列 → 空配列',
    input: '',
    expected: [],
  },

  // エッジケース：コロンなし
  {
    name: 'コロンなし → value = label',
    input: 'オプション1,オプション2',
    expected: [{ value: 'オプション1', label: 'オプション1' }, { value: 'オプション2', label: 'オプション2' }],
  },
];

// テスト実行関数
function runTests() {
  console.log('=== parseOptions テスト開始 ===\n');

  let passed = 0;
  let failed = 0;

  for (const testCase of testCases) {
    const result = parseOptions(testCase.input);
    const isEqual = JSON.stringify(result) === JSON.stringify(testCase.expected);

    if (isEqual) {
      console.log(`✅ PASS: ${testCase.name}`);
      passed++;
    } else {
      console.log(`❌ FAIL: ${testCase.name}`);
      console.log(`  期待: ${JSON.stringify(testCase.expected)}`);
      console.log(`  結果: ${JSON.stringify(result)}`);
      failed++;
    }
  }

  console.log(`\n=== 結果: ${passed}/${testCases.length} 成功 ===`);

  // getOptionLabel テスト
  console.log('\n=== getOptionLabel テスト ===');
  const options = [{ value: '1', label: 'ラベル1' }, { value: '2', label: 'ラベル2' }];
  const label = getOptionLabel(options, '1');
  console.log(label === 'ラベル1' ? '✅ PASS: getOptionLabel' : '❌ FAIL: getOptionLabel');

  // getOptionLabels テスト
  console.log('\n=== getOptionLabels テスト ===');
  const labels = getOptionLabels(options, '1,2');
  console.log(labels[0] === 'ラベル1' && labels[1] === 'ラベル2' ? '✅ PASS: getOptionLabels' : '❌ FAIL: getOptionLabels');

  // groupOptions テスト
  console.log('\n=== groupOptions テスト ===');
  const groupedOptions = [
    { value: '1', label: 'A1', group: 'A' },
    { value: '2', label: 'A2', group: 'A' },
    { value: '3', label: 'B1', group: 'B' },
  ];
  const grouped = groupOptions(groupedOptions);
  console.log(grouped['A']?.length === 2 && grouped['B']?.length === 1 ? '✅ PASS: groupOptions' : '❌ FAIL: groupOptions');

  // isOptionsEmpty テスト
  console.log('\n=== isOptionsEmpty テスト ===');
  console.log(isOptionsEmpty(null) === true ? '✅ PASS: isOptionsEmpty(null)' : '❌ FAIL');
  console.log(isOptionsEmpty('1:ラベル') === false ? '✅ PASS: isOptionsEmpty("1:ラベル")' : '❌ FAIL');

  return failed === 0;
}

// モジュールとして実行された場合にテスト実行
if (typeof require !== 'undefined' && require.main === module) {
  const success = runTests();
  process.exit(success ? 0 : 1);
}

export { runTests };
