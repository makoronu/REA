# バグ調査

## やること
機能が動作しない場合のデータフロー調査

## 調査順序（必ずこの順番）
1. **フロントエンド**
   - コンポーネントでパラメータを正しく設定しているか
   - console.logで値を確認

2. **サービス層**
   - APIに正しくパラメータを渡しているか
   - propertyService.ts等を確認

3. **APIエンドポイント**
   - パラメータを受け取っているか
   - properties.py等を確認

4. **CRUD/DB層**
   - クエリに反映されているか
   - generic.py等を確認

## 確認コマンド
```bash
# API直接テスト
curl "http://localhost:8005/api/v1/[endpoint]?[params]"

# 本番テスト
curl "https://realestateautomation.net/api/v1/[endpoint]?[params]"
```

## 完了条件
- [ ] 各層でデータが正しく流れている
- [ ] APIで期待通りの結果が返る

## 次の工程
→ type_check.md
