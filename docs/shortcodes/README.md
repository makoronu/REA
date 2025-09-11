# ⚡ REA ショートコード - 超効率Claude連携

## 🎯 使い方
```
👤 [ショートコード] "[質問内容]"

例:
👤 @rea-pricing "利回り計算を実装したい"
👤 @rea-images "30枚アップロード機能のバグ修正"
👤 @rea-api "新しいエンドポイント追加方法"
```

## ⚡ ショートコード一覧

| ショートコード | 機能 | 対象ファイル |
|---------------|------|-------------|
| `@rea-pricing` | Pricing | docs/claude_chunks/pricing/overview.md |
| `@rea-images` | Images | docs/claude_chunks/images/overview.md |
| `@rea-location` | Location | docs/claude_chunks/location/overview.md |
| `@rea-building` | Building | docs/claude_chunks/building/overview.md |
| `@rea-api` | Api | docs/claude_chunks/api/overview.md |
| `@rea-dev` | Dev | docs/claude_chunks/development/overview.md |
| `@rea-db` | Db | docs/01_database/current_structure.md |
| `@rea-help` | Help | docs/claude_integration/quick_reference.md |


## 🚀 実際の使用例

### 💰 価格機能
```
👤 @rea-pricing "利回り計算APIの実装方法"
→ Claude が docs/claude_chunks/pricing/overview.md を確認して回答
```

### 📸 画像機能
```
👤 @rea-images "画像一括削除機能の実装"
→ Claude が docs/claude_chunks/images/overview.md を確認して回答
```

### 🔧 トラブル対応
```
👤 @rea-dev "PostgreSQL接続エラーの解決方法"
→ Claude が docs/claude_chunks/development/overview.md を確認して回答
```

---
生成日時: 2025-07-21 18:16:11
