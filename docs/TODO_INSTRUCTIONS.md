# 作業指示書

ここにやって欲しいことを貼り付けてください。

---

（以下に記載）

以下のROADMAPに従って、不動産情報ライブラリAPI統合機能を実装してください。

## 基本方針

- メイン機能: 座標ベース自動判定 → テキスト表示（編集可能）
- サブ機能: MAP表示は確認用として最小限
- 免責: 「参考情報です。正確な内容は役所でご確認ください」
- 精度: 100%を目指さない。ユーザーが手動修正可能な設計

## APIエンドポイント共通仕様

- ベースURL: https://www.reinfolib.mlit.go.jp/ex-api/external/
- 認証: Ocp-Apim-Subscription-Key ヘッダー
- 形式: XYZタイル方式（z/x/y指定）
- 出力: GeoJSON または バイナリベクトルタイル（pbf）
- ズーム: 11（市）〜 15（詳細）

## Phase 1-A：テキスト判定のみ（MAP不要）


優先度3: 立地適正化計画 (XKT003) → 表示例「居住誘導区域内」
優先度4: 地区計画 (XKT024) → 表示例「○○地区計画区域内」or「対象外」
優先度5: 高度利用地区 (XKT025) → 表示例「対象外」
優先度6: 都市計画道路 (XKT030) → 表示例「計画道路あり（幅員○m）」or「なし」
優先度7: 自然公園地域 (XKT020) → 表示例「対象外」
優先度8: 災害危険区域 (XKT017) → 表示例「対象外」
優先度9: 大規模盛土造成地 (XKT021) → 表示例「対象外」
優先度10: 地すべり防止地区 (XKT022) → 表示例「対象外」
優先度11: 急傾斜地崩壊危険区域 (XKT023) → 表示例「対象外」

## Phase 1-B：テキスト判定 + MAP表示（確認用）


優先度1: 防火・準防火地域 (XKT014) → 表示例「準防火地域」これを既存MAPに追加、項目としても
優先度2: 都市計画区域/区域区分 (XKT001) → 表示例「市街化区域」→済


優先度1: 用途地域 (XKT002) → 表示例「第一種住居地域（60%/200%）」※実装済み、MAP追加
優先度2: 洪水浸水想定区域 (XKT026) → 表示例「浸水想定あり（0.5〜3m）」
優先度3: 土砂災害警戒区域 (XKT029) → 表示例「土砂災害警戒区域（急傾斜）」
優先度4: 津波浸水想定 (XKT028) → 表示例「津波浸水想定あり（2m）」
優先度5: 高潮浸水想定区域 (XKT027) → 表示例「対象外」
優先度6: 液状化傾向図 (XKT023) → 表示例「液状化リスク：中」

## Phase 1-C：周辺施設（既存機能拡張）

実装済み: 小学校区 (XKT004)、中学校区 (XKT005)、学校 (XKT006)
優先度1: 保育園・幼稚園等 (XKT007) → 距離計算・リスト表示
優先度2: 医療機関 (XKT010) → 距離計算・リスト表示
優先度3: 指定緊急避難場所 (XGT001) → 距離計算・リスト表示

## Phase 2：価格情報（将来検討・今回スキップ）

取引価格・成約価格 (XIT001)、地価公示・調査 (XPT002)

## 実装不要（スキップ）

XIT002（市区町村一覧）、XCT001（鑑定評価書）、XPT001（価格ポイント）
XKT011（福祉施設）、XKT015（駅別乗降客数）、XKT018（図書館）
XKT019（市区町村役場）、XKT031（人口集中地区）、XKT013（将来推計人口）

## DB設計案

property_regulationsテーブルを新規作成:
- property_id: propertiesへの外部キー
- 都市計画系: urban_planning_area, area_classification, use_district, building_coverage_ratio, floor_area_ratio, fire_prevention_district, height_district, district_plan, location_optimization, planned_road, planned_road_width
- 災害リスク系: flood_risk_level, flood_depth_min, flood_depth_max, landslide_warning_area, landslide_type, tsunami_risk_level, tsunami_depth, storm_surge_risk, liquefaction_risk
- その他制限: natural_park, disaster_risk_area, large_fill_area, landslide_prevention, steep_slope_area
- メタ情報: auto_fetched_at, manually_edited, verified_at, verified_by

## 実装順序

1. DB設計・マイグレーション作成
2. 不動産情報ライブラリAPI共通クライアント作成（認証、タイル座標変換）
3. Phase 1-A のAPI統合（テキスト判定のみ）
4. Phase 1-B のAPI統合（MAP表示含む）
5. Phase 1-C の周辺施設拡張
6. フロントエンド：物件詳細画面に法令制限セクション追加
7. フロントエンド：MAP表示コンポーネント（災害ハザード用）

まず現在のDB構造を確認し、実装計画を提案してください。
