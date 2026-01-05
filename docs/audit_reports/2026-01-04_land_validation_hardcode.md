# 個別プロトコル調査レポート

## 概要

| 項目 | 内容 |
|------|------|
| 対象 | 土地物件 公開時バリデーション問題 |
| 日時 | 2026-01-04 19:40 |
| 調査者 | Claude |
| 判定 | 要修正（定数ファイル集約） |

---

## 調査範囲

| ファイル | 種別 | 役割 |
|----------|------|------|
| `rea-api/app/services/publication_validator.py` | API | バリデーションロジック |
| `rea-api/app/api/api_v1/endpoints/properties.py` | API | エンドポイント |
| `rea-admin/src/components/form/DynamicForm.tsx` | UI | フロントUI |

---

## 発見した問題

### ハードコード一覧（4件）

| ファイル | 行 | コード | 重要度 |
|----------|-----|--------|--------|
| DynamicForm.tsx | 1382 | `['販売中', '商談中']` | 中 |
| DynamicForm.tsx | 1400 | `['公開', '会員公開']` | 中 |
| properties.py | 267 | `VALID_PUBLICATION_STATUSES = [...]` | 中 |
| publication_validator.py | 143-144 | `["detached"]` | 低 |

---

## バリデーション動作確認

### バックエンド（テストスクリプト実行）

```
property_id: 1908（土地物件）
is_valid: False
missing_fields: 3件（最寄駅、バス停、近隣施設）
```

→ **バックエンドは正常動作**

### フロントエンド

- コード上は正しく見える
- 実動作未確認（ブラウザ開発者ツール確認が必要）

---

## 判断

### 問い

ハードコーディング違反 vs シンプルさ のトレードオフをどう判断するか？

### 結論

**B. 定数ファイル集約**を採用

### 根拠

ADR-0001「メタデータ駆動と定数ファイルの使い分け」に基づく判断：

| 基準 | 公開ステータス判定 | 判定 |
|------|-------------------|------|
| 誰が変更？ | 開発者のみ | 定数ファイル |
| 変更頻度 | 年1回以下 | 定数ファイル |
| ビジネスロジック | 根幹（安定） | 定数ファイル |

完全メタデータ駆動は**過剰な抽象化**（Tenet 2違反）

---

## 修正方針

### フロントエンド

```typescript
// rea-admin/src/constants.ts に追加
export const VALIDATION_REQUIRED_STATUSES = ['公開', '会員公開'];
export const PUBLICATION_EDITABLE_SALES_STATUSES = ['販売中', '商談中'];
```

DynamicForm.tsx でこれらを参照するよう修正。

### バックエンド

```python
# rea-api/app/core/constants.py に追加（または既存ファイル）
VALID_PUBLICATION_STATUSES = ["公開", "非公開", "会員公開", "公開前確認"]
```

properties.py でこれを参照するよう修正。

---

## 残課題

「土地だけバリデーションが効かない」問題の根本原因は未特定。
ブラウザ開発者ツールで `validate-publication` リクエストの確認が必要。

---

## 関連ドキュメント

- ADR-0001: メタデータ駆動と定数ファイルの使い分け
