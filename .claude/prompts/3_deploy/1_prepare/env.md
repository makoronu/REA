# .env確認

## やること
本番.envが正しいか確認

## 確認ポイント
- [ ] DATABASE_URLが本番DB
- [ ] API_URLが本番URL
- [ ] SECRET_KEYが本番用
- [ ] DEBUG=false

## コマンド
```bash
ssh rea-conoha "cat /opt/REA/.env | head -10"
```

## 完了条件
- [ ] 本番設定を確認した

## 中断条件
- 開発用設定 → 停止して報告

## 次の工程
→ config.md
