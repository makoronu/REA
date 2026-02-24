# FastAPI 基盤

## やること
Market Intelligence の API サーバーを構築する。

## 作成ファイル
```
mi-api/
├── app/
│   ├── main.py              (〜80行)  — FastAPIアプリ、CORS、ヘルスチェック
│   ├── config.py            (〜50行)  — 設定（環境変数読み込み）
│   ├── api/
│   │   └── endpoints/
│   │       ├── properties.py (〜200行) — 収集物件CRUD
│   │       ├── analytics.py  (〜200行) — 分析API
│   │       └── metadata.py   (〜100行) — メタデータAPI
│   ├── crud/
│   │   └── generic.py       (〜200行) — 汎用CRUD（REA踏襲）
│   └── database.py          (〜50行)  — DB接続
└── requirements.txt
```

## main.py
- FastAPI インスタンス
- CORS設定（localhost開発用）
- ヘルスチェック: `GET /health`
- ルーター登録

## properties.py エンドポイント
| メソッド | パス | 用途 |
|---------|------|------|
| GET | /properties | 収集物件一覧（フィルタ・ページネーション） |
| GET | /properties/{id} | 物件詳細 |
| GET | /properties/{id}/price-history | 価格履歴 |
| GET | /properties/disappeared | 消失物件一覧 |
| GET | /properties/stale | 滞留物件一覧（N日以上掲載中） |

## analytics.py エンドポイント
| メソッド | パス | 用途 |
|---------|------|------|
| GET | /analytics/area-report | エリアレポート（市区町村別相場） |
| GET | /analytics/comparable | 類似物件検索（査定書用） |
| GET | /analytics/map-properties | 地図表示用（バウンディングボックス） |
| GET | /analytics/market-stats | 市場統計（掲載数・消失数・平均価格） |

## metadata.py エンドポイント
| メソッド | パス | 用途 |
|---------|------|------|
| GET | /metadata/options/{category_code} | マスタオプション取得 |
| GET | /metadata/scrape-sessions | 巡回セッション一覧 |
| GET | /metadata/sources | 巡回対象一覧 |

## ルール
- REA の generic.py パターンを踏襲（汎用CRUD）
- 全 SELECT に `deleted_at IS NULL` フィルタ
- パラメータバインディング必須（SQLi防止）
- レスポンスは統一フォーマット
- ポート: 8010（REAの8005と衝突しない）

## 完了条件
- [ ] `GET /health` が200を返す
- [ ] 物件一覧API が動作する
- [ ] メタデータAPI が動作する
- [ ] 分析API の基本形ができている
- [ ] 全ファイル500行以下

## 次の工程
→ ../5_complete/quality.md
