# ハードコーディング撲滅ロードマップ

**作成日:** 2026-01-03
**更新日:** 2026-01-03
**ベース:** docs/hardcoding_audit_report.md

---

## 全体概要

| 項目 | 値 |
|------|-----|
| 総ハードコード件数 | 200+ |
| セグメント数 | 4（統合後） |
| 最優先 | Seg1（バリデーション問題解決） |

---

## セグメント一覧

| Seg | 対象 | 件数 | 目的 | 優先度 | 状態 |
|-----|------|------|------|--------|------|
| **1** | バリデーション | 5 | ユーザー問題解決 | 最高 | ✅完了（デプロイ待ち） |
| **2** | UIマスタ化（ステータス・選択肢・UI色） | 40+ | フロントエンドマスタ化 | 高 | 未着手 |
| **3** | 設定・構造（権限・ストレージ・テーブル名・APIパス） | 120+ | バックエンド一元化 | 中 | 未着手 |
| **4** | 日付・メッセージ（placeholder・エラーメッセージ） | 85+ | UI/UX統一 | 低 | 未着手 |

---

## Seg1: バリデーション（詳細）

### 問題

ユーザー報告: 「バリデーションがざる」「効くところと効かないところがある」

### 根本原因

`publication_validator.py` に5つのハードコーディングが存在し、field-visibility管理画面の設定が正しく反映されない。

### 対象（5件）

| No | 行 | 定数名 | 現在の値 | 修正後 |
|----|-----|--------|----------|--------|
| 1-1 | 24 | PUBLICATION_STATUSES_REQUIRING_VALIDATION | `["公開", "会員公開"]` | master_options.requires_validation=true |
| 1-2 | 27 | VALID_NONE_VALUES | `["なし", "該当なし", "なし（学区外）"]` | column_labels.valid_none_text |
| 1-3 | 30 | ZERO_VALID_COLUMNS | `["management_fee", "repair_reserve_fund"]` | column_labels.zero_is_valid |
| 1-4 | 78-102 | CONDITIONAL_EXCLUSIONS | 5ルール | column_labels.conditional_exclusion (JSON) |
| 1-5 | 66-71 | SPECIAL_FLAG_COLUMNS | 4フラグ | column_labels.special_flag_key |

### セグメント分割判断

**結論: Seg1は分割しない（一括実施）**

理由:
1. 全5件が同一ファイル（publication_validator.py）内
2. 全5件が同一のバリデーションフローで使用
3. DB変更は1回のマイグレーションで完結
4. 個別テストより統合テストの方が効率的

### 実施ステップ（分割ではなく順序）

```
Step 1: DBスキーマ変更
  - column_labels に4カラム追加
    - valid_none_text (text[])
    - zero_is_valid (boolean)
    - conditional_exclusion (jsonb)
    - special_flag_key (varchar)
  - master_options に1カラム追加
    - requires_validation (boolean)

Step 2: データ移行
  - 既存ハードコード値をDBに投入
  - 例: management_fee.zero_is_valid = true

Step 3: コード修正
  - publication_validator.py をDB読み込み型に変更

Step 4: テスト
  - ローカルでバリデーション動作確認
  - field-visibility設定が正しく反映されるか確認
```

### 完了条件

- [ ] field-visibility管理画面で設定した必須項目がバリデーションされる
- [ ] 「なし」「該当なし」等が有効値として認識される
- [ ] 条件付き除外が正しく動作する（detached→room_floor不要等）
- [ ] 特殊フラグ（no_station等）が正しく動作する

---

## Seg2〜Seg4（統合後）

### Seg2: UIマスタ化（40+件）

対象ファイル:
- constants.ts (SALES_STATUS, PUBLICATION_STATUS, TAB_GROUPS)
- DynamicForm.tsx (ステータス連動ロジック)
- PropertiesPage.tsx (UI色)
- RegulationTab.tsx, ImageUploader.tsx, NearbyFacilitiesField.tsx, JsonEditors.tsx (選択肢)

### Seg3: 設定・構造（120+件）

旧Seg3+Seg4を統合

対象:
- users.py 権限レベル閾値
- ローカルストレージキー統一
- ページサイズ/制限値統一
- 検索距離設定
- generic.py, metadata.py, admin.py 等のテーブル名
- フロントエンドのAPIパス
- 学校種別コード

### Seg4: 日付・メッセージ（85+件）

旧Seg5

対象:
- 日付フォーマット統一
- フォームplaceholder外部化
- エラーメッセージ統一（日英混在解消）

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-03 | 初版作成、Seg1計画策定 |
| 2026-01-03 | Seg1完了、Seg2-5を3つに統合（Seg2-4へ） |
