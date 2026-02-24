# 登録（Registrar）

## やること
1. registrar.py: UPSERT（新規INSERT/既存UPDATE/unchanged判定）
2. dedup.py: 名寄せキー生成（住所+面積+価格ハッシュ）
3. status_tracker.py: 消失検知・価格追跡・再出現検知

## ルール
- scraped_properties + price_history + listing_status_history を1トランザクション
- 消失 = 前回activeで今回未発見 → disappeared_at設定
- 価格変更 → price_historyに追記（前回比記録）

## 完了条件
- [ ] 新規/更新/消失/価格変更/再出現が全て動作する
- [ ] 全操作がトランザクション内
- [ ] 全ファイル500行以下

## 次 → ../4_api/api.md
