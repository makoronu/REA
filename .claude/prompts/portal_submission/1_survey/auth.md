# ログイン・認証調査

## やること

1. ログインページにアクセス（Selenium）
2. 認証方式を特定
   - ID/PW のみ
   - 2FA（SMS, メール, TOTP）
   - CAPTCHA
   - IP制限
   - その他

3. 手動介入ポイントを特定
   - 初回のみ？毎回？
   - セッション維持期間

4. `auth.json` を作成

## 出力テンプレート

```json
{
  "login_url": "",
  "auth_type": "password|2fa|captcha|ip_restricted",
  "manual_intervention": {
    "required": true,
    "timing": "first_time|every_time",
    "description": ""
  },
  "session": {
    "duration_minutes": null,
    "cookie_name": "",
    "can_persist": true
  },
  "selectors": {
    "username": "",
    "password": "",
    "submit": "",
    "captcha": null,
    "2fa_input": null
  }
}
```

## 完了条件

- [ ] 認証方式特定済み
- [ ] auth.json 作成済み
- [ ] ログイン成功確認済み

## 次 → form.md
