# ハードコーディング撲滅ロードマップ

**作成日:** 2026-01-03
**更新日:** 2026-01-04（Seg4完了、全セグメント完了）
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
| **2** | UIマスタ化（ステータス・選択肢・UI色） | 40+ | フロントエンドマスタ化 | 高 | ✅完了（デプロイ待ち） |
| **3a** | 権限レベル閾値修正（バグ修正） | 1 | バグ修正 | **緊急** | ✅完了（デプロイ待ち） |
| **3b** | テーブル名・ストレージキー統一 | 18 | 一元管理 | 高 | ✅完了（デプロイ待ち） |
| **3c** | APIパス統一 | 40 | 一元管理 | 中 | ✅完了（デプロイ待ち） |
| **3d** | その他（学校コード、距離、サイズ） | 30+ | 一元管理 | 低 | ✅完了（デプロイ待ち） |
| **4** | 日付・メッセージ（placeholder・エラーメッセージ） | 85+ | UI/UX統一 | 低 | ✅完了（デプロイ待ち） |

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

### Seg3: 設定・構造（分割済み）

**分割理由:** 120+件は大きすぎるため、優先度別に4分割

#### Seg3a: 権限レベル閾値修正（緊急バグ修正）

| ファイル | 行 | 問題 |
|----------|-----|------|
| users.py | 66 | `role_level < 80` → DBのadminは50、不一致 |

**影響:** adminユーザーがユーザー管理APIにアクセスできない

#### Seg3b: テーブル名・ストレージキー統一（18件）

対象:
- generic.py ALLOWED_TABLES（6件）
- metadata.py ALLOWED_TABLES（重複）
- metadataService.ts テーブル名（4件）
- ローカルストレージキー（8件、重複定義あり）

#### Seg3c: APIパス統一（45件）

対象:
- フロントエンド全体（17ファイル）
- `apiPaths.ts` に集約予定

#### Seg3d: その他設定値（30+件）

対象:
- 学校種別コード
- 検索距離設定
- ページサイズ/制限値

### Seg4: 日付・メッセージ（85+件）

旧Seg5

対象:
- 日付フォーマット統一
- フォームplaceholder外部化
- エラーメッセージ統一（日英混在解消）

### Seg5: ステータス連動ロジックAPI一元化

**問題**: 販売ステータス→公開ステータス連動がフロント（2箇所）とAPI（1箇所）に分散

対象:
- PropertiesPage.tsx: handleStatusChange, handleBulkStatusChange
- DynamicForm.tsx: handleSalesStatusChange
- PropertyEditDynamicPage.tsx: handleSubmit

修正内容:
- フロント側のpublication_status自動設定を削除
- APIレスポンスでUI更新
- 連動ロジックはAPI（properties.py）に一元化

### Seg5バグ修正: ステータス連動の完全DB駆動化

**問題**:
- 売止め/成約/販売終了 → 非公開 の連動がAPIに未実装
- 販売中 → 公開前確認 の判定がハードコード
- option_value（文字列）とoption_code（数値）の型不一致

修正内容:
1. master_optionsに`triggers_unpublish`カラム追加（非公開連動）
2. master_optionsに`triggers_pre_check`カラム追加（公開前確認連動）
3. properties.pyで両方をDB駆動化（option_codeで比較）
4. フォールバックは空リスト（ハードコードなし）
5. `rea_`プレフィックス除去のマッピング追加（ADR-0002）

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-03 | 初版作成、Seg1計画策定 |
| 2026-01-03 | Seg1完了、Seg2-5を3つに統合（Seg2-4へ） |
| 2026-01-03 | Seg2完了、Seg3を4分割（3a〜3d）、権限バグ発見 |
| 2026-01-03 | Seg3a完了（ロールコードベース化） |
| 2026-01-03 | Seg3b完了（テーブル名・ストレージキー統一） |
| 2026-01-03 | Seg3c完了（APIパス統一、40件→apiPaths.ts） |
| 2026-01-04 | Seg3d完了（設定値DB化） |
| 2026-01-04 | land_info型変更時に0→NULL変換ミス発覚（ローカルのみ、本番無事） |

---

## インシデント: land_info 型変更ミス

**詳細:** `docs/incident_reports/2026-01-04_land_info_type_change.md`

### 判定結果

**部分再設計**

### 根本原因

「マッピングロジック = ハードコーディング」と誤認。

```
❌ 誤った判断:
  rea_1 という文字列がある → DB型を VARCHAR に変更

✓ 正しいアプローチ:
  DB は INTEGER のまま → API層で rea_1 ↔ 1 マッピング
```

### 教訓（ハードコーディング定義の明確化）

| 項目 | 判定 |
|------|------|
| `if status == 3` | ❌ ハードコーディング |
| `if status == SOLD` | ✓ 定数参照（OK） |
| `rea_1 → 1` マッピング | ✓ 変換ロジック（OK） |
| DB型変更で対応 | ❌ 設計ミス |

**マッピングテーブルはハードコーディングではない。**

---

## 次回タスク: ローカルDB復旧 + 型戻し

**優先度:** デプロイ前

### やること

1. **型を INTEGER に戻す**（8カラム）
2. **本番からデータ復旧**
3. **API層でマッピング実装**（rea_* ↔ 数値）

### 影響範囲（ローカルDBのみ、本番無事）

| カラム | 消失件数 |
|--------|----------|
| land_area_measurement | 2369 |
| land_category | 83 |
| land_rights | 113 |
| land_transaction_notice | 2370 |
| setback | 32 |
| terrain | 132 |
| city_planning | 409 |
| use_district | 0（データ無事） |
