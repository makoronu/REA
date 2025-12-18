# デプロイ実行

## やること
deploy.shを実行

## コマンド
```bash
./scripts/deploy.sh
```

## deploy.shがやること
1. git push
2. 本番でgit pull
3. 設定ファイル保護・復元
4. npm install && build
5. サービス再起動
6. ヘルスチェック

## 完了条件
- [ ] deploy.sh成功

## 中断条件
- エラー発生 → 停止して報告

## 次の工程
→ ../4_verify/verify.md
