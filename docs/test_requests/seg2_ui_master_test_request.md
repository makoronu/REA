# Seg2 UIマスタ化テスト依頼書

**作成日:** 2026-01-03
**対象:** Seg2 UIマスタ化（メタデータ駆動）

---

## 1. 概要

### 目的
フロントエンドの選択肢ハードコーディングをマスタテーブル駆動に変更し、管理画面からの設定変更を可能にする。

### 変更対象

| ファイル | 変更内容 |
|----------|----------|
| `scripts/migrations/seg2_ui_master.sql` | DBスキーマ拡張・マスタデータ投入 |
| `rea-api/app/api/api_v1/endpoints/metadata.py` | 3つの新規APIエンドポイント |
| `rea-admin/src/services/metadataService.ts` | API呼び出しメソッド追加 |
| `rea-admin/src/components/form/JsonEditors.tsx` | 選択肢をAPI駆動に変更 |
| `rea-admin/src/components/form/RegulationTab.tsx` | 防火地域・用途地域をAPI駆動に変更 |

---

## 2. デプロイ手順

### Step 1: DBマイグレーション

```bash
# 本番DBに接続
psql -h [本番ホスト] -U [ユーザー] -d rea

# マイグレーション実行
\i scripts/migrations/seg2_ui_master.sql
```

### Step 2: バックエンドデプロイ

```bash
# APIサーバー再起動
```

### Step 3: フロントエンドデプロイ

```bash
# ビルド・デプロイ
```

---

## 3. テスト項目

### 3.1 API動作確認

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 1 | `GET /api/v1/metadata/options/road_direction` | 8件の接道方向が返る（北, 北東, 東, 南東, 南, 南西, 西, 北西） | [ ] |
| 2 | `GET /api/v1/metadata/options/road_type` | 2件の接道種別が返る（公道, 私道） | [ ] |
| 3 | `GET /api/v1/metadata/options/road_status` | 6件の接道状況が返る | [ ] |
| 4 | `GET /api/v1/metadata/options/room_type` | 9件の間取タイプが返る（R, K, SK, DK, SDK, LK, SLK, LDK, SLDK） | [ ] |
| 5 | `GET /api/v1/metadata/options/fire_prevention` | 3件の防火地域が返る（防火地域, 準防火地域, 指定なし） | [ ] |
| 6 | `GET /api/v1/metadata/options/renovation_item` | 14件のリフォーム項目が返る | [ ] |
| 7 | `GET /api/v1/metadata/status-settings` | sales_status, publication_status, transaction_type が返る | [ ] |
| 8 | `GET /api/v1/metadata/categories` | マスタカテゴリ一覧が返る | [ ] |

### 3.2 物件編集画面 - 土地情報タブ

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 9 | 接道情報の追加 | 接道方向・種別・状況のドロップダウンに選択肢が表示される | [ ] |
| 10 | 接道方向選択 | 「北」「南東」等が正しく選択・保存できる | [ ] |
| 11 | 接道種別選択 | 「公道」「私道」が正しく選択・保存できる | [ ] |
| 12 | 接道状況選択 | 「建築基準法上の道路」「42条2項道路」等が正しく選択・保存できる | [ ] |

### 3.3 物件編集画面 - 建物情報タブ

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 13 | 間取り情報の追加 | 間取タイプのドロップダウンに選択肢が表示される | [ ] |
| 14 | 間取タイプ選択 | 「LDK」「SLDK」等が正しく選択・保存できる | [ ] |
| 15 | リフォーム履歴の追加 | リフォーム項目のドロップダウンに選択肢が表示される | [ ] |
| 16 | リフォーム項目選択 | 「キッチン」「浴室」「屋根」等が正しく選択・保存できる | [ ] |

### 3.4 物件編集画面 - 法令制限タブ

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 17 | 防火地域選択 | 「防火地域」「準防火地域」「指定なし」のドロップダウンが表示される | [ ] |
| 18 | 防火地域保存 | 選択した値が正しく保存される | [ ] |
| 19 | 法令制限自動取得 | 緯度経度を入力後、「法令制限を自動取得」ボタンで用途地域が取得される | [ ] |
| 20 | 用途地域自動登録 | 取得した用途地域名が正しいコードに変換されて登録される | [ ] |

### 3.5 フォールバック動作確認

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 21 | API障害時の動作 | APIがエラーを返した場合でも、デフォルト値で選択肢が表示される | [ ] |
| 22 | 警告ログ確認 | コンソールに「取得に失敗、デフォルト値を使用」の警告が表示される | [ ] |

---

## 4. 回帰テスト

| No | テスト内容 | 期待結果 | 確認 |
|----|-----------|----------|------|
| 23 | 既存物件の編集 | 既存データの表示・編集が正常に動作する | [ ] |
| 24 | 新規物件の登録 | 全フィールドが正常に入力・保存できる | [ ] |
| 25 | 公開バリデーション | 公開時のバリデーションが正常に動作する | [ ] |
| 26 | 物件一覧表示 | 一覧画面が正常に表示される | [ ] |

---

## 5. ロールバック手順

問題発生時は以下の手順でロールバック：

### DBロールバック

```sql
-- 追加したカラムを削除（必要に応じて）
ALTER TABLE master_options DROP COLUMN IF EXISTS is_default;
ALTER TABLE master_options DROP COLUMN IF EXISTS allows_publication;
ALTER TABLE master_options DROP COLUMN IF EXISTS linked_status;
ALTER TABLE master_options DROP COLUMN IF EXISTS ui_color;
ALTER TABLE master_options DROP COLUMN IF EXISTS shows_contractor;
ALTER TABLE master_categories DROP COLUMN IF EXISTS icon;

-- 追加したカテゴリ・オプションを削除
DELETE FROM master_options WHERE category_id IN (
  SELECT id FROM master_categories WHERE category_code IN (
    'road_direction', 'road_type', 'road_status',
    'room_type', 'fire_prevention', 'renovation_item'
  )
);
DELETE FROM master_categories WHERE category_code IN (
  'road_direction', 'road_type', 'road_status',
  'room_type', 'fire_prevention', 'renovation_item'
);
```

### コードロールバック

```bash
git revert [コミットハッシュ]
```

---

## 6. 確認者

| 担当 | 名前 | 日付 | 署名 |
|------|------|------|------|
| 実施者 | | | |
| 確認者 | | | |

---

## 7. 備考

- フォールバックパターンにより、APIエラー時もUIは動作継続
- 既存データへの影響なし（追加のみ）
- 本変更後、マスタオプションの追加・変更はDBで可能
