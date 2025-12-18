# REA (Real Estate Automation System)

> 親ファイル: `/Users/yaguchimakoto/my_programing/CLAUDE.md` の共通ルールを継承

**日本一の不動産情報システム** - メタデータ駆動アーキテクチャ

---

## 現在のセッション

| 項目 | 内容 |
|------|------|
| 作業中 | なし |
| 完了 | ユーザー管理機能、パスワードリセット、認証フロントエンド |
| 残り | ユーザー管理v1.0拡張、HOMES入稿、ZOHO画像同期 |
| 最終更新 | 2025-12-18 |
| 本番URL | https://realestateautomation.net/ |

---

## クイックスタート

```bash
# 1. FastAPI起動
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

# 2. フロントエンド起動
cd ~/my_programing/REA/rea-admin && npm run dev

# 3. DB接続確認
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python -c "from shared.database import READatabase; print(READatabase.health_check())"
```

**ポート**: PostgreSQL=5432、FastAPI=8005、フロント=5173

### テストアカウント

| Email | Password | Role |
|-------|----------|------|
| info@shirokuma2103.com | Sh1r09matk | 一般ユーザー |
| 4690kb@gmail.com | Test1234! | 会社管理者 |

---

## 最重要原則

### 1. メタデータ駆動ファースト

新機能依頼 → まず「column_labelsテーブル登録で対応可能か？」を検討。
独自実装は最後の手段。

### 2. ハードコーディング禁止

- 同じ値が2箇所以上 → 定数化
- 同じロジックが複数箇所 → 関数化
- マスターデータ → API経由（DBが唯一の真実）

### 3. 禁止事項

1. 既存ファイル未確認でコード作成
2. メタデータ駆動可能なのに独自実装
3. テーブル構造未確認でAPI実装
4. PYTHONPATH未設定でimport
5. 1関数100行超え / ネスト4段以上

---

## DB構成

### 主要テーブル
- `properties` - 物件基本情報
- `building_info` - 建物情報
- `land_info` - 土地情報
- `property_images` - 画像情報
- `column_labels` - **メタデータ駆動の核心**

### マスターテーブル
- `property_types` - 物件種別
- `master_options` - 選択肢（267件）
- `m_facilities` - 周辺施設（65万件）
- `m_stations` - 駅（1万件）

### テーブル構造確認

```bash
cd ~/my_programing/REA && PYTHONPATH=. python3 -c "
from shared.database import READatabase
db = READatabase()
conn = db.get_connection()
cur = conn.cursor()
cur.execute('''
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name = 'テーブル名' ORDER BY ordinal_position
''')
for row in cur.fetchall(): print(f'{row[0]}: {row[1]}')
cur.close(); conn.close()
"
```

---

## コーディング規則

### 開発優先順序

1. テーブル構造確認
2. メタデータ駆動で対応可能か検討
3. 既存API・コンポーネント確認
4. 最後にコード作成

### メタデータ駆動の核心

- フォーム自動生成: `DynamicForm.tsx`
- ENUM値: `column.options`使用
- 日本語ラベル: `column.label_ja`
- カラム追加: `column_labels`テーブルに登録

---

## バックアップ

```bash
# DBバックアップ
/Applications/Postgres.app/Contents/Versions/latest/bin/pg_dump -h localhost -p 5432 -U yaguchimakoto real_estate_db > ~/my_programing/REA/backups/backup_YYYYMMDD.sql

# 復元
/Applications/Postgres.app/Contents/Versions/latest/bin/psql -h localhost -p 5432 -U yaguchimakoto -d real_estate_db < backup.sql
```

**タイミング**: 作業開始時、DB変更前、1日の終わり

---

## 環境変数

```bash
# バックエンド（.env）
DATABASE_URL=postgresql://yaguchimakoto@localhost:5432/real_estate_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=real_estate_db
DB_USER=yaguchimakoto

# フロントエンド（rea-admin/.env）
VITE_API_URL=http://localhost:8005
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| DB接続エラー | ポート5432確認、Postgres.app起動確認 |
| importエラー | `PYTHONPATH=~/my_programing/REA`設定 |
| CORSエラー | FastAPIのCORS設定確認 |
| APIエラー | FastAPIターミナルでログ確認 |

---

## セルフテスト

UI変更後は必ずSeleniumでE2Eテスト実行。

```bash
cd ~/my_programing/REA && PYTHONPATH=. python tests/e2e/ui_test_helper.py
```

**禁止**: テストせずに「できた」と報告

---

## Git運用

```bash
# コミット
git add -A && git commit -m "タイプ: 内容"

# タイプ: feat / fix / refactor / docs / db
```

**1日の終わり**: `git push origin main`

---

## 目指す状態

> 「メタデータ変えるだけで新機能できた」
> 「このシステム、使ってて気持ちいい」
