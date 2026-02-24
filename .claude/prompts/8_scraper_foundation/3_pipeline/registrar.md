# 登録（Registrar）

## やること
REA変換済みデータをDBに保存するレイヤーを実装する。
差分検知・消失検知・価格履歴記録を含む。**全サイト共通。**

## 作成ファイル
```
mi-scraper/src/pipeline/
├── registrar.py       (〜200行) — メイン登録ロジック
├── dedup.py           (〜100行) — 重複排除・名寄せ
└── status_tracker.py  (〜150行) — 消失検知・価格追跡
```

## registrar.py の責務

### 1. UPSERT（新規/更新判定）
```python
def register(property_data: dict, source_site: str, listing_id: str) -> str:
    """
    Returns: 'new' | 'updated' | 'unchanged'
    """
```
- `(source_site, listing_id)` のUNIQUE制約で判定
- 新規: INSERT + first_seen_at = now() + last_seen_at = now()
- 既存+変更あり: UPDATE + last_seen_at = now()
- 既存+変更なし: last_seen_at のみ更新

### 2. トランザクション
- scraped_properties INSERT/UPDATE
- price_history INSERT（価格変更時）
- listing_status_history INSERT（状態変更時）
- **上記3つを1トランザクションで実行**

### 3. セッション統計更新
- scrape_sessions の new/updated/disappeared カウンタを更新

## dedup.py の責務（名寄せ）

### 複数サイト間の同一物件検知
```python
def generate_dedup_key(address: str, land_area: float, price: int) -> str:
    """住所 + 面積 + 価格のハッシュで名寄せキーを生成"""
```
- 住所正規化（全角→半角、丁目表記統一）後にハッシュ
- 完全一致だけでなく「住所一致 + 面積±5% + 価格±10%」のファジーマッチも提供
- Phase 2（複数サイト対応時）で本格稼働

## status_tracker.py の責務

### 消失検知
```python
def detect_disappeared(source_site: str, session_id: int, seen_listing_ids: set) -> int:
    """
    今回の巡回で発見されなかった物件を消失扱いにする。
    Returns: 消失件数
    """
```
- 前回 active で今回 seen に含まれない → disappeared_at = now()
- listing_status_history に 'disappeared' を記録
- days_since_first_seen を算出

### 価格追跡
```python
def track_price_change(property_id: int, new_price: int) -> bool:
    """
    価格変更を検知して price_history に記録する。
    Returns: 変更があったか
    """
```
- 前回価格と比較
- 変更あり → price_history INSERT（price_change = new - old, change_count++）
- 変更なし → 何もしない

### 再出現検知
- disappeared_at が設定済みだが今回発見された → disappeared_at = NULL
- listing_status_history に 'reappeared' を記録

## 完了条件
- [ ] 新規物件がINSERTされる
- [ ] 既存物件が差分UPDATEされる
- [ ] 価格変更時にprice_historyに記録される
- [ ] 消失検知が動作する
- [ ] 再出現検知が動作する
- [ ] 全操作がトランザクション内
- [ ] 全ファイル500行以下

## 次の工程
→ ../4_api/api.md
