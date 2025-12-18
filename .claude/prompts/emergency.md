# 緊急対応

**本番障害発生時に使用。パニックするな。**

---

## 1. 状況確認

### やること
1. 何が起きているか確認
2. 影響範囲を特定
3. 原因を推測

### 確認コマンド
```bash
# サービス状態
ssh rea-conoha "systemctl status rea-api"
ssh rea-conoha "systemctl status rea-admin"

# ログ確認
ssh rea-conoha "journalctl -u rea-api --since '10 minutes ago'"

# DB接続
ssh rea-conoha "psql -U postgres -c 'SELECT 1'"
```

---

## 2. 切り戻し判断

### 判断基準
| 状況 | 対応 |
|------|------|
| 軽微なバグ | その場で修正 |
| 重大なバグ | ロールバック |
| DB破損 | バックアップ復元 |

---

## 3. ロールバック手順

### コード戻し
```bash
ssh rea-conoha "cd /opt/rea && git checkout [前回のcommit hash]"
ssh rea-conoha "systemctl restart rea-api rea-admin"
```

### DB復元
```bash
ssh rea-conoha "psql -U postgres real_estate_db < /tmp/backup_YYYYMMDD.sql"
```

---

## 4. 報告

### 報告内容
```
【障害報告】
発生日時:
影響範囲:
原因:
対応内容:
現在の状態:
再発防止:
```

---

## 禁止事項

- パニックで適当に操作
- バックアップなしで復旧作業
- 報告せずに作業続行

---

## 完了後

```bash
afplay /System/Library/Sounds/Glass.aiff
```

ユーザーに状況報告すること。
