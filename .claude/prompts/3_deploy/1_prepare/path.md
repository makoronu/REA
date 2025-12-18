# 本番パス確認

## やること
本番サーバーの実際のパスを確認

## コマンド
```bash
ssh rea-conoha "systemctl status rea-api | grep WorkingDirectory"
ssh rea-conoha "systemctl status rea-admin | grep WorkingDirectory"
```

## 確認ポイント
- ドキュメントのパスと一致しているか
- 不一致あれば先に解決

## 完了条件
- [ ] 本番パス確認した

## 次の工程
→ backup.md
