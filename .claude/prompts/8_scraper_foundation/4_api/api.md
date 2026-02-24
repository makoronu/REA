# FastAPI基盤

## やること
1. main.py: FastAPIアプリ、CORS、ヘルスチェック（port 8010）
2. properties.py: 収集物件CRUD（一覧/詳細/消失/滞留）
3. analytics.py: 分析API（エリアレポート/類似物件/地図表示/統計）
4. metadata.py: マスタオプション/巡回セッション/巡回対象

## ルール
- REAのgeneric.pyパターン踏襲
- 全SELECTにdeleted_at IS NULL
- パラメータバインディング必須

## 完了条件
- [ ] GET /health が200を返す
- [ ] 主要エンドポイントが動作する
- [ ] 全ファイル500行以下

## 次 → ../5_complete/quality.md
