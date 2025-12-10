# REA (Real Estate Automation System)

**日本一の不動産情報システムを目指す**

マルチテナント対応の不動産管理システム。メタデータ駆動アーキテクチャで、DBスキーマ変更のみで新機能を追加可能。他社への販売を前提とした設計。

---

## 最重要原則：メタデータ駆動ファースト

**新機能依頼を受けたら、この順序で検討：**

1. **既存メタデータで対応可能？**
   - DBカラム追加 + `column_labels`登録で解決するか？
   - ENUM型/JSONB型で対応できるか？

2. **不可能な場合のみ独自実装**
   - 多対多リレーション、複雑なロジック、リアルタイム処理

3. **必ずユーザーに確認**
   - 実装方針を複数提案して選んでもらう

**例：**
```
ユーザー: 「設備管理機能を追加したい」

❌ 即座に「設備管理API作成します」
✅ 「amenitiesテーブルにboolean型カラム追加で、メタデータ駆動で自動対応できます。独自APIは不要です。どちらがいいですか？」
```

---

## クイックスタート

### ローカル環境（Mac + Claude Code）

```bash
# 1. Docker起動
/usr/local/bin/docker compose up -d postgres redis

# 2. FastAPI起動
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

# 3. フロントエンド起動
cd ~/my_programing/REA/rea-admin && npm run dev

# 4. DB接続確認
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python -c "from shared.database import READatabase; db = READatabase(); print('✅ 成功' if db else '❌ 失敗')"
```

### Codespaces環境

```bash
docker-compose up -d postgres redis
cd rea-api && export $(grep -v '^#' /workspaces/REA/.env | xargs) && PYTHONPATH=/workspaces/REA python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
cd rea-admin && npm run dev
```

**Codespaces注意**: VS Code下部「PORTS」タブで5173, 8005を**Public**に設定

---

## プロジェクト構成

```
~/my_programing/REA/  (または /workspaces/REA/)
├── CLAUDE.md                 # プロジェクト知識（Claude Code用）
├── rea-admin/src/
│   ├── components/common/    # 共通UI
│   ├── components/form/      # フォーム（DynamicForm.tsx等）
│   ├── pages/                # ページ
│   ├── services/             # API通信（metadataService.ts等）
│   └── hooks/                # カスタムフック（useAutoSave等）
├── rea-api/app/
│   ├── api/                  # エンドポイント
│   ├── models/               # SQLAlchemy
│   └── schemas/              # Pydantic
├── shared/database.py        # DB接続
└── docs/
    ├── ROADMAP.md            # ロードマップ
    └── logs/                 # 日次作業ログ
```

---

## DB構成

### 主要テーブル（5テーブル）
| テーブル | カラム数 | 役割 |
|---------|---------|------|
| properties | 44 | 物件基本情報 |
| amenities | 29 | 設備情報（14個のboolean） |
| building_info | 30 | 建物情報 |
| land_info | 29 | 土地情報 |
| property_images | 11 | 画像情報 |

### マスターデータ（マルチテナント対応）

**新マスターシステム（2025-12-10導入）**
| テーブル | 件数 | 役割 |
|---------|------|------|
| master_categories | 45 | ENUMカテゴリ（物件種別、建物構造等） |
| master_options | 267 | 選択肢（ホームズv4.3.2ベース） |
| company_master_settings | - | 会社別カスタマイズ |
| portal_mappings | - | ホームズ/SUUMO/athome連携 |

**既存マスター**
- column_labels（143件）- **メタデータ駆動の核心**
- equipment_master, property_types, building_structure, land_rights, current_status, floor_plan_room_types, image_types, zoning_districts

**ポート**: 5433（5432ではない）

### テーブル構造確認コマンド

```bash
# ローカル環境
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python -c "
from shared.database import READatabase
db = READatabase()
conn = db.get_connection()
cur = conn.cursor()
cur.execute('''
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'テーブル名'
    ORDER BY ordinal_position
''')
for row in cur.fetchall():
    print('{:<30} {}'.format(row[0], row[1]))
cur.close()
conn.close()
"
```

**確認ポイント：**
- JSONB型カラムがあるか？（柔軟な構造で対応できないか）
- 既存カラムで対応できないか？
- ENUM型は何があるか？

---

## コーディング思想

### 2人のエンジニアの融合：DHH × Uncle Bob

| エンジニア | 担当領域 | REAへの適用 |
|-----------|---------|-------------|
| **DHH** | 実用主義 | メタデータ駆動、設定より規約、早く動くものを優先 |
| **Uncle Bob** | 保守性 | 他社販売前提、読みやすいコード、テスト |

### コアコンセプト

**「規約で動き、誰でも読める」**
**「書かないコードが最高のコード。書くなら誰でも読めるコード。」**

### 実用主義（DHH）

**設定より規約**
```python
# ❌ 設定ファイルで指定
FIELD_TYPES = { 'property_name': 'text', 'price': 'number' }

# ✅ 規約で自動判断（メタデータ駆動）
# column_labelsテーブルに登録すれば自動で動く
```

**早く動くものを優先**
- まず動くものを作り、必要なら後でリファクタ
- 今必要ないものは作らない（YAGNI）
- 3回同じコードを書いたら抽象化を検討
- 「将来使うかも」は作らない理由

### 保守性（Uncle Bob）

**関数は1つのことだけ**
```python
# ❌ 複数のことをやる
def process_property(data):
    validated = validate(data)
    saved = save(validated)
    send_notification(saved)
    return saved

# ✅ 分割する
def process_property(data):
    validated = validate_property(data)
    return save_property(validated)
```

**名前に意図を込める**
```python
# ❌ 曖昧
if p > 1000000 and y < 10:

# ✅ 読めば分かる
is_premium_price = price > 1_000_000
is_relatively_new = building_age < 10
if is_premium_price and is_relatively_new:
```

**ネストを浅く（早期リターン）**
```python
# ❌ 深いネスト
def validate(data):
    if data:
        if data.get('price'):
            if data['price'] > 0:
                return True
    return False

# ✅ 早期リターン
def validate(data):
    if not data:
        return False
    if not data.get('price'):
        return False
    return data['price'] > 0
```

### バランスの取り方

| 状況 | DHH寄り | Uncle Bob寄り |
|------|---------|---------------|
| 新機能プロト | ✅ 早く動かす | - |
| 本番リリース前 | - | ✅ リファクタ・テスト |
| バグ修正 | ✅ 最小限の変更 | - |
| 他社納品前 | - | ✅ 読みやすさ最優先 |

---

## デザイン指針

### 3人のデザイナーの融合：原研哉 × 深澤直人 × 中村勇吾

| デザイナー | 担当領域 | REAへの適用 |
|-----------|---------|-------------|
| **原研哉** | 視覚的整理 | 白基調、余白の美学、情報の優先順位 |
| **深澤直人** | 無意識の使いやすさ | 自然な導線、迷わないUI、触りたくなる形 |
| **中村勇吾** | 触って楽しい | マイクロアニメーション、気持ちいいフィードバック |

### コアコンセプト

**「使ってて気持ちいい業務システム」**

- 毎日8時間使っても疲れない
- 操作に迷わない（考えさせない）
- 触ってて楽しい（ドーパミンが出る）

### 色とレイアウト（原研哉）

- **背景**: 白〜極薄グレー（#FAFAFA）
- **テキスト**: ほぼ黒（#1A1A1A）、グレー（#6B7280）
- **アクセント**: 1色のみ（ブランドカラー）
- **余白**: 詰め込まない。呼吸できる空間
- **罫線**: 最小限。影やスペースで区切る

### 操作性（深澤直人）

- **ボタン**: 押したくなる大きさ（最低44px）
- **入力欄**: フォーカス時に明確な変化
- **導線**: 左上→右下の自然な流れ
- **ラベル**: 曖昧な言葉禁止（「その他」より具体的に）
- **エラー**: 何が間違いで、どうすれば直るか明示

### インタラクション（中村勇吾）

- **保存成功**: ふわっと✓が出て消える（0.3秒）
- **タブ切り替え**: スライドアニメーション
- **入力完了**: フィールドが微かに光る
- **エラー**: 赤くブルッと震える（shake）
- **ホバー**: 微妙な拡大 or 色変化（即反応）
- **ローディング**: スケルトン or パルス（スピナー禁止）

### 実装例

```tsx
// ボタンのホバーアニメーション
<button className="
  px-4 py-2 
  bg-blue-600 text-white rounded-lg
  transition-all duration-200 ease-out
  hover:bg-blue-700 hover:scale-[1.02] hover:shadow-md
  active:scale-[0.98]
">
  保存
</button>
```

### やってはいけないこと

- ❌ 原色ベタ塗り（目が疲れる）
- ❌ 影の多用（古臭い）
- ❌ 3種類以上のフォントサイズ混在
- ❌ 意味のないアニメーション
- ❌ ローディングスピナーをグルグル回す
- ❌ モーダルの多用（画面遷移で解決）
- ❌ 「よろしいですか？」確認ダイアログ乱発

---

## コーディング規則

### 開発優先順序（必ず守る）

1. テーブル構造確認（上記コマンド使用）
2. **メタデータ駆動で対応可能か検討**
3. 既存API・コンポーネント確認
4. 最後にコード作成

### メタデータ駆動の核心

- フォーム自動生成: `DynamicForm.tsx`
- ENUM値: `column.options`使用（`column.enum_values`は❌）
- 日本語ラベル: `column.label_ja`
- カラム追加: `column_labels`テーブルに登録（コードに直書き❌）

### 必須ルール

- `PYTHONPATH=~/my_programing/REA`（ローカル）または `/workspaces/REA`（Codespaces）を常に設定
- 既存ファイルは必ず中身を確認してからコード作成
- エスケープ回避: f-stringより`format()`使用
- 環境変数フィルタ: `grep -v '^#'`でコメント除外

### 禁止事項

1. 手動フォームフィールド追加（メタデータ駆動で）
2. 既存ファイル未確認でコード作成
3. 一気に大量実装（段階的に）
4. 日本語ラベルハードコード（column_labels使用）
5. 車輪の再発明（lodash等活用）
6. テーブル構造未確認でAPI実装
7. カラム名の思い込み使用
8. メタデータ駆動可能なのに独自実装
9. 一部テーブルのみ確認
10. PYTHONPATH未設定でimport
11. 複数問題同時修正
12. 動く前から抽象化
13. 「将来のため」のコード
14. 自分しか読めない省略
15. 1関数100行超え
16. ネスト4段以上
17. マジックナンバー直書き
18. コメントアウトしたコード放置
19. テストなしで他社納品

### スタイリング

Tailwindが効かない場合はインラインstyle：
```tsx
// ❌ Tailwindレスポンシブが効かないことが多い
<div className="sm:grid-cols-2">

// ✅ インラインstyleで確実に
<div style={{gridTemplateColumns: 'repeat(2, 1fr)'}}>
```

---

## Git運用：自動コミット

**作業の区切りごとに自動でコミットする。**

### タイミング

- ファイル作成・編集完了後
- 機能実装完了後
- バグ修正後
- DB変更後

### コミットメッセージ

```bash
git add -A && git commit -m "タイプ: 日本語で簡潔な作業内容"
```

**タイプ例：**
- `feat:` 新機能
- `fix:` バグ修正
- `refactor:` リファクタリング
- `docs:` ドキュメント
- `style:` UIスタイル変更
- `db:` DB変更

**例：**
```
feat: 設備マスターテーブル追加
fix: メタデータAPI接続エラー修正
refactor: DynamicForm整理
docs: ROADMAP更新
db: master_optionsに267件投入
```

### 1日の作業終了時

```bash
git push origin main
```

---

## 環境変数

**バックエンド（.env）**
```
DATABASE_URL=postgresql://rea_user:rea_password@localhost:5433/real_estate_db
DB_HOST=localhost
DB_PORT=5433
DB_NAME=real_estate_db
DB_USER=rea_user
DB_PASSWORD=rea_password
REDIS_URL=redis://localhost:6379
```

**フロントエンド（rea-admin/.env）**
```
# ローカル
VITE_API_URL=http://localhost:8005

# Codespaces
# VITE_API_URL=https://${CODESPACE_NAME}-8005.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}
```

---

## トラブルシューティング

### よくあるエラー

| 症状 | 原因 | 対処 |
|------|------|------|
| DB接続エラー(5432) | ポート間違い | `DB_PORT=5433` |
| import エラー | PYTHONPATH未設定 | `PYTHONPATH=~/my_programing/REA` |
| CORSエラー | ポート非公開 | PORTSタブでPublic化（Codespaces） |
| Tailwindレスポンシブ効かない | Viteの問題 | インラインstyle使用 |
| docker: Command not found | パス未設定 | `/usr/local/bin/docker`使用 |
| カラム名エラー | 思い込み | テーブル構造確認 |

### 4段階デバッグ

1. **Level 1**: システム基盤 - `docker compose ps`、環境変数確認
2. **Level 2**: ログ確認 - ブラウザConsole、FastAPIターミナル、npm run devターミナル
3. **Level 3**: DB接続 - 接続テストコマンド実行
4. **Level 4**: 段階的切り分け - Docker → FastAPI → フロントエンド

---

## 作業フロー

### 開始時
1. `docs/ROADMAP.md` で現在地確認
2. Docker起動確認
3. Codespaces: ポート設定（5173, 8005 = Public）

### 実装前
1. 使用テーブル特定
2. **メタデータ駆動で対応可能か検討**
3. 全関連テーブル構造確認
4. 既存API・コンポーネント確認

### 実装中
1. メタデータ駆動厳守
2. ENUM: `column.options`使用
3. 段階的実装
4. PYTHONPATH設定

### 完了時
1. TypeScriptエラーなし
2. 既存機能破壊なし
3. レスポンシブOK
4. **Gitコミット**
5. 作業ログ記録（`docs/logs/`）
6. ROADMAP更新

### 1日の終わり
1. `git push origin main`
2. 作業ログに今日やったことを記録

---

## ユーティリティスクリプト（scripts/）

### column_labels投入
新しいカラムをメタデータに登録する時に使用。
```bash
# CSVから一括投入
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python scripts/insert_all_column_labels.py

# 個別投入（スクリプトを編集して使用）
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python scripts/insert_column_labels.py
```

### DB構造変更（migrate_to_new_structure.py）
テーブル構造を大幅に変更する時のみ使用。**破壊的操作**なので要注意。

### db_analyzer/
カラム分類・分析ツール。DB設計時の参考に。

---

## ローカル環境特有の注意点

- シェル: tcsh/cshの場合は `/bin/bash -c "..."` で実行
- Docker: `/usr/local/bin/docker compose` でフルパス指定
- npm: `/opt/homebrew/bin/npm` または `/usr/local/bin/npm`

---

## 目指す状態

### システムとして
> 「メタデータ変えるだけで新機能できた」
> 「このコード、初見でも何やってるか分かる」
> 「変更したい箇所がすぐ見つかる」

### UIとして
> 「このシステム、なんか使ってて気持ちいいんだよな」
> 「他のシステム使いたくなくなった」

**業務システムの常識を覆す。**