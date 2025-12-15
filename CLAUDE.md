# REA (Real Estate Automation System)

> **親ファイル参照**: このファイルは `/Users/yaguchimakoto/my_programing/CLAUDE.md` の共通ルールを継承しています。
> 開発ルール、禁止事項、Git運用、セルフテストルール等は親ファイルを参照してください。

---

**日本一の不動産情報システムを目指す**

マルチテナント対応の不動産管理システム。メタデータ駆動アーキテクチャで、DBスキーマ変更のみで新機能を追加可能。他社への販売を前提とした設計。

---

## 現在のセッション（復旧用）

**⚠️ Claudeは必ずセッション開始時にここを確認し、作業終了時に更新すること。**

| 項目 | 内容 |
|------|------|
| 作業中 | なし |
| 完了 | **Phase 2: マスターテーブル統合**（旧マスター6テーブル削除、master_options統一、メタデータAPI改修）、Phase 3一部（3-1, 3-3）|
| 残り | Phase 3残り（enum_values廃止）、Phase 4（FK制約）、Phase 5（property_type統一）→ ZOHO画像同期 |
| 最終更新 | 2025-12-15 17:10 |
| 備考 | データ設計正規化Phase 2完了。選択肢データはmaster_options (source='rea') に統一。 |

### メタ駆動マッピングシステム

**作成日**: 2025-12-14
**概要**: DBテーブルから変換ルールを読み込む汎用マッパー

**テーブル**:
- `import_field_mappings`: フィールドマッピング（50件）
- `import_value_mappings`: 値変換マッピング（192件）

**対応フィールド**: property_type, publication_status, sales_status, current_status, use_district, building_structure, direction, room_type, land_rights, setback, terrain, land_category, city_planning, road_access, road_type, parking_availability, transaction_type, delivery_timing

**使い方**:
```python
from app.services.zoho.mapper import MetaDrivenMapper
mapper = MetaDrivenMapper(source_type="zoho")  # 他のソースは source_type変更
result = mapper.map_record(raw_data)
```

### セッション運用ルール

1. **セッション開始時**: このセクションを確認し、前回の続きがあれば引き継ぐ
2. **作業中**: 大きなタスクを始めたら「作業中」を更新
3. **セッション終了時**: 進捗を記録し、次回への引き継ぎ事項を「備考」に残す
4. **タスク完了時**: 「作業中」を「なし」にクリア

### 失敗から学んだこと（2025-12-14）

**問題**: セッション中断時に進捗が失われた

**原因**:
- ROADMAPのタスク状態を更新していなかった
- CLAUDE.mdのセッション情報を更新していなかった
- 「後でまとめて記録」と思っていた

**対策（必ず守る）**:
1. **タスク完了直後**: ROADMAPの該当行を `[x]` に更新
2. **作業の区切りごと**: CLAUDE.mdの「作業中」「完了」を更新
3. **コミット時**: 進捗がわかるコミットメッセージ
4. **セッション終了時**: 必ずログを残す（`docs/logs/YYYY-MM-DD.md`）

**心得**: 記録は「後で」ではなく「今すぐ」。セッションはいつ落ちるかわからない。

### 失敗事例: ZOHOインポートの値体系不整合（2025-12-14）

**問題**: ZOHOからインポートしたデータが編集画面で正しく表示されない

**原因**:
1. **property_type**: DBに「一戸建て」（label）を入れたが、selectのvalueは「detached」（id）を期待
2. **郵便番号**: ZOHOにそもそもデータがない（96.6%がNULL）
3. **property_name_public**: DBカラムがboolean型だがスキーマはstring型を期待

**根本原因**:
- `property_types`テーブルの構造（id=英語, label=日本語）を確認せずにマッピングした
- 複数の値体系（ENUM, master_options, property_types, column_labels.enum_values）が混在
- インポート後の動作確認をSeleniumでちゃんとやらなかった

**対策（必ず守る）**:
1. **マッピング作成前**: 対象テーブルの構造と既存データを必ず確認
2. **selectフィールド**: valueとlabelの両方を確認（APIのmetadata/columnsでoptionsを確認）
3. **インポート後**: 必ず編集画面をSeleniumで開いてフィールドに値が表示されるか確認
4. **値体系の統一**: property_typesテーブルのid（英語）を使用、日本語はlabelのみ

**修正したもの**:
- property_type: 「一戸建て」→「detached」等に一括変換
- property_name_public: boolean→text型に変更
- 郵便番号: m_postal_codesマスター作成、住所から自動補完

### 失敗事例: 登記取込機能の目的を理解していなかった（2025-12-14）

**問題**: 登記取込機能のUIが使いにくい

**最初の実装（間違い）**:
- 登記レコード1件ずつに「物件登録」ボタン
- 登記レコードを永続的に保存する設計

**ユーザーの指摘**:
- 「登記レコードは記録に残さない」
- 「物件DBに乗っけるためだぞ、意味わかる？」
- 「この登記取り込みの意味がわかってない」

**正しい理解**:
- 登記取込の目的 = 物件DBへの登録（登記レコードの保存ではない）
- 不動産取引では「土地数筆＋建物1棟」が1物件
- 登記レコードは一時的な取り込みデータ

**対策（必ず守る）**:
1. **機能の目的を最初に確認**: 「何のために」この機能があるのか
2. **業務フローを理解する**: 技術実装より先に、業務を理解
3. **一時データは一時データとして扱う**: 使い終わったら削除

**改善後の実装**:
- チェックボックスで複数の登記を選択
- 「まとめて物件登録」ボタン
- 物件登録後、登記レコードは自動削除
- UIタイトルを「取込待ち」に変更（一時データであることを明示）

### 失敗事例: 同名カラムの上書き問題（2025-12-14）

**問題**: 編集画面で住所データ（postal_code, prefecture, city, address）がNULLで表示される

**原因**:
- `/properties/{id}/full` APIで複数テーブルをマージする際の処理
- `properties`テーブルと`land_info`テーブルに同名カラムがある
- `land_info`の値（NULL）が`properties`の値を上書きした

**コード（問題箇所）**:
```python
# properties.py:117-119
for key, value in land_dict.items():
    if key not in ['id', 'property_id', 'created_at', 'updated_at']:
        result[key] = value  # ← NULLでも上書きしてしまう
```

**対策（必ず守る）**:
1. **複数テーブルマージ時**: カラム名の重複を事前に確認
2. **マージロジック**: NULLの場合は上書きしない、または優先順位を設定
3. **デバッグ時**: SQLクエリ結果と最終レスポンスを両方確認

**修正方針（明日対応）**:
```python
# NULL値はスキップ（propertiesの値を優先）
for key, value in land_dict.items():
    if key not in ['id', 'property_id', 'created_at', 'updated_at']:
        if value is not None or key not in result:
            result[key] = value
```

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

## 最重要原則：ハードコーディング禁止

**マジックナンバー、定数、繰り返しロジックは必ず共通化する。**

### なぜ最重要か

- 機能が増えるほど、ハードコーディングは**指数関数的に負債になる**
- 1箇所の変更が10箇所の修正を要求する状態は**開発スピード・保守スピードを殺す**
- 他社販売を前提としたシステムでは**致命的なコスト増**になる

### 共通化ファイル

| ファイル | 役割 |
|---------|------|
| `shared/constants.py` | 定数・計算関数（徒歩分数、学校種別コード、検索半径等） |
| `rea-admin/src/components/common/` | 共通UIコンポーネント |

### 具体的なルール

**バックエンド:**
```python
# ❌ ハードコーディング
walk_min = max(1, round(distance_m / 80))  # 6箇所に同じコード
WHERE school_type = '16001'  # マジックナンバー

# ✅ 共通化
from shared.constants import calc_walk_minutes, SCHOOL_TYPE_CODES
walk_min = calc_walk_minutes(distance_m)
WHERE school_type = %s, (SCHOOL_TYPE_CODES['elementary'],)
```

**フロントエンド:**
```tsx
// ❌ ハードコーディング
const FACILITY_CATEGORIES = [
  { value: 'convenience', label: 'コンビニ' },
  // ... 12個手動管理
];

// ✅ APIから取得（DBが唯一の真実）
const categories = await fetch('/api/v1/geo/facility-categories');
```

### 開発フェーズと共通化のバランス

**開発初期は速度優先、区切りで共通化フェーズを入れる。**

```
[機能開発] → [機能開発] → [機能開発] → [共通化フェーズ] → [機能開発] → ...
```

**共通化フェーズでやること：**
1. `grep`でコードベース全体を検索し、重複パターンを洗い出す
2. 2箇所以上で使われている値・ロジックを`shared/constants.py`に移動
3. 類似UIコンポーネントを`components/common/`に統合

**タイミング：**
- 機能がひと段落したとき
- ロードマップの大きな区切り
- 「なんか同じコード書いてるな」と感じたとき

**ロードマップ作成時は必ず「共通化フェーズ」を入れる。**

### 新規実装時のチェックリスト

1. **同じ値が2箇所以上に出現しないか？** → 定数化
2. **同じ計算ロジックが複数箇所にないか？** → 関数化
3. **フロントにマスターデータを直書きしていないか？** → API経由に
4. **既存の共通化ファイルに追加できないか？** → `shared/constants.py`確認

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

### 周辺施設データ（2025-12-11構築）

| テーブル | 役割 |
|---------|------|
| m_facilities | 周辺施設（約65万件） |
| m_facility_categories | 施設カテゴリ（20種表示） |
| m_stations | 駅（約10,000件） |
| m_data_sources | **データソース管理** |

**データソース一覧**
| カテゴリ | データソース | 更新スクリプト |
|---------|-------------|---------------|
| 学校（小中高大短大高専幼稚園認定こども園専門学校） | 国土数値情報 P29 | `scripts/data_import/import_schools.py` |
| 職業訓練校 | 手動収集（北海道8校のみ） | `scripts/data_import/import_vocational_training.py` |
| 駅 | HeartRails Express API | `scripts/data_import/import_stations.py` |
| 商業施設（スーパー、コンビニ等） | OpenStreetMap | `scripts/data_import/import_osm_facilities.py` |
| 医療機関（病院、診療所） | 国土数値情報 P04 | `scripts/data_import/import_medical.py` |
| 公共施設（役所、郵便局等） | OpenStreetMap | `scripts/data_import/import_osm_facilities.py` |

**データ更新方法**
```bash
cd ~/my_programing/REA
PYTHONPATH=~/my_programing/REA python3 scripts/data_import/import_schools.py
```

**未対応データ**
- 保育所: 公式CSVなし（ここdeサーチにAPIなし）
- 職業訓練校（北海道以外）: 手動収集が必要（全国166校中8校のみ）

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

### コミュニケーションルール

- **URLは単独行で表示**（前後に改行を入れる。文章とくっつけない）
  ```
  ❌ 編集画面（http://localhost:5173/properties/1/edit）を開いて

  ✅ 編集画面を開いてください。

     http://localhost:5173/properties/1/edit
  ```

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

## DBバックアップ運用

**データは取り戻せない。こまめにバックアップを取る。**

### バックアップ保存先

```
~/my_programing/REA/backups/
```

### バックアップコマンド

```bash
# ローカル環境
/usr/local/bin/docker compose exec -T postgres pg_dump -U rea_user real_estate_db > ~/my_programing/REA/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Codespaces
docker compose exec -T postgres pg_dump -U rea_user real_estate_db > /workspaces/REA/backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 復元コマンド

```bash
# ローカル環境
cat ~/my_programing/REA/backups/backup_YYYYMMDD_HHMMSS.sql | /usr/local/bin/docker compose exec -T postgres psql -U rea_user real_estate_db

# Codespaces
cat /workspaces/REA/backups/backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T postgres psql -U rea_user real_estate_db
```

### バックアップを取るタイミング（必須）

| タイミング | 理由 |
|-----------|------|
| **作業開始時** | 何かやらかしても戻れる |
| **DB構造変更前** | ALTER TABLE, DROP等の前 |
| **大量データ投入前** | INSERT, UPDATE, DELETEの前 |
| **マイグレーション前** | スキーマ変更の前 |
| **1日の終わり** | 日次バックアップとして |

### 古いバックアップの整理

1週間以上前のバックアップは削除してOK（容量節約）。ただし、重要なマイルストーン時点のバックアップは残す。

```bash
# 7日以上前のバックアップを確認
find ~/my_programing/REA/backups -name "backup_*.sql" -mtime +7

# 削除する場合（慎重に）
find ~/my_programing/REA/backups -name "backup_*.sql" -mtime +7 -delete
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

### 完了時（セルフテスト必須）

**UI変更・機能実装後は、必ずSeleniumでE2Eテストを実行し、自分で確認してから報告する。**

1. TypeScriptエラーなし
2. **E2Eテスト実行**（ユーザーが見える形で）
3. 既存機能破壊なし
4. レスポンシブOK
5. **Gitコミット**
6. 作業ログ記録（`docs/logs/`）
7. ROADMAP更新

### セルフテストルール

**「できたよ」と報告する前に、必ず自分でテストして確認する。**

#### テスト実行コマンド
```bash
# フロントエンド・API起動後に実行
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python tests/e2e/ui_test_helper.py

# 全テスト実行
cd ~/my_programing/REA && PYTHONPATH=~/my_programing/REA python -m pytest tests/e2e/ -v -s
```

#### テストの流れ

1. **実装完了後**: Seleniumでブラウザを起動（ヘッドレスではない＝ユーザーに見える）
2. **自動操作**: 変更した画面を開き、操作をシミュレート
3. **スクリーンショット**: 各ステップでスクリーンショットを保存（`test_screenshots/`）
4. **厳重確認**:
   - 表示崩れがないか
   - エラーが出ていないか
   - 期待通りに動作するか
5. **問題なければ報告**: 「E2Eテスト完了。問題なし。」と報告
6. **問題あれば修正**: 黙って直してから再テスト

#### 確認ポイント

| チェック項目 | 確認方法 |
|-------------|---------|
| ページ読み込み | 要素が表示されるか |
| フォーム入力 | 入力・送信が動作するか |
| タブ切り替え | 正しく切り替わるか |
| レスポンシブ | 画面サイズ変更で崩れないか |
| APIエラー | コンソールに500エラーがないか |

#### テストファイル

| ファイル | 役割 |
|---------|------|
| `tests/e2e/ui_test_helper.py` | UIテスト用ヘルパークラス |
| `tests/e2e/test_property_crud.py` | 物件CRUD操作テスト |

#### 禁止事項

- テストせずに「できた」と報告する
- ヘッドレスモードでテストを隠れて実行する（ユーザーに見せる）
- エラーを見つけても報告せずに放置する
- スクリーンショットを確認せずに「OK」と言う

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