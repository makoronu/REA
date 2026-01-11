# ポータル入稿アプリ開発

**新規ポータル対応時に使用。共通処理は抽象化済み、設定ファイル追加のみで対応。**

---

## 原則

1. **ハードコーディング禁止** → 全てJSONで設定化
2. **登録ボタンはユーザーが押す** → 法律上、自動送信禁止
3. **共通処理は1つ** → ポータル固有は設定ファイルのみ

---

## 実行順序

```
1_survey/
  → portal_info.md    # ポータル基本情報
  → auth.md           # ログイン・認証調査
  → form.md           # フォーム項目・セレクタ取得
  → validation.md     # バリデーション調査

2_design/
  → mapping.md        # マッピング設計
  → transform.md      # 変換ロジック定義

3_implement/
  → config.md         # 設定ファイル作成
  → test.md           # テスト実行

4_complete/
  → review.md         # レビュー・承認
```

---

## 共通アーキテクチャ

```
portal_configs/
  {portal_name}/
    portal.json       # ポータル基本情報
    auth.json         # 認証設定
    form.json         # フォーム定義
    mapping.json      # マッピング定義
    transform.json    # 変換ルール

common/
  login.py            # ログイン処理（設定駆動）
  form_filler.py      # フォーム入力（設定駆動）
  validator.py        # バリデーション（設定駆動）
  image_handler.py    # 画像処理（設定駆動）
  submission.py       # 入稿制御（登録ボタン待機）
```

---

## 停止条件

- 手動介入が必要なログイン → 待機してユーザーに通知
- バリデーションエラー → 停止してエラー内容表示
- 登録ボタン直前 → **必ず停止**、ユーザー操作を待つ
