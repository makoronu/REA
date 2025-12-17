# メール送信サービス
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Optional
import logging

from .config import EmailConfig

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP経由でメール送信"""

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        メール送信

        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body_text: 本文（テキスト）
            body_html: 本文（HTML）- オプション

        Returns:
            成功時True
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = "{} <{}>".format(
                Header(EmailConfig.SMTP_FROM_NAME, 'utf-8').encode(),
                EmailConfig.SMTP_FROM_EMAIL
            )
            msg['To'] = to_email

            part1 = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part1)

            if body_html:
                part2 = MIMEText(body_html, 'html', 'utf-8')
                msg.attach(part2)

            with smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT) as server:
                # localhost以外はTLS+認証
                if EmailConfig.SMTP_HOST != 'localhost':
                    server.starttls()
                    if EmailConfig.SMTP_USER and EmailConfig.SMTP_PASSWORD:
                        server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
                server.sendmail(
                    EmailConfig.SMTP_FROM_EMAIL,
                    to_email,
                    msg.as_string()
                )

            logger.info("Email sent successfully to: {}".format(to_email))
            return True

        except Exception as e:
            logger.error("Failed to send email: {}".format(str(e)))
            return False

    @staticmethod
    def send_password_reset_email(to_email: str, reset_token: str, user_name: str = '') -> bool:
        """
        パスワードリセットメール送信

        Args:
            to_email: 送信先メールアドレス
            reset_token: リセットトークン
            user_name: ユーザー名

        Returns:
            成功時True
        """
        reset_url = "{}/reset-password?token={}".format(
            EmailConfig.FRONTEND_URL,
            reset_token
        )

        subject = "【REA】パスワードリセットのご案内"

        body_text = """
{name}様

パスワードリセットのリクエストを受け付けました。
以下のURLからパスワードを再設定してください。

{url}

このリンクは{hours}時間有効です。

※ このメールに心当たりがない場合は、無視してください。
※ このメールは自動送信されています。返信しないでください。

--
REA - Real Estate Automation System
""".format(
            name=user_name if user_name else 'お客',
            url=reset_url,
            hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS
        )

        body_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #3B82F6; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>パスワードリセットのご案内</h2>
        <p>{name}様</p>
        <p>パスワードリセットのリクエストを受け付けました。<br>
        以下のボタンをクリックしてパスワードを再設定してください。</p>
        <p style="margin: 30px 0;">
            <a href="{url}" class="button">パスワードを再設定</a>
        </p>
        <p>または、以下のURLをブラウザに貼り付けてください：<br>
        <a href="{url}">{url}</a></p>
        <p>このリンクは<strong>{hours}時間</strong>有効です。</p>
        <div class="footer">
            <p>※ このメールに心当たりがない場合は、無視してください。<br>
            ※ このメールは自動送信されています。返信しないでください。</p>
            <p>REA - Real Estate Automation System</p>
        </div>
    </div>
</body>
</html>
""".format(
            name=user_name if user_name else 'お客',
            url=reset_url,
            hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS
        )

        return EmailService.send_email(to_email, subject, body_text, body_html)

    @staticmethod
    def send_welcome_email(to_email: str, user_name: str, reset_token: str) -> bool:
        """
        新規登録ウェルカムメール（初期パスワード設定用）

        Args:
            to_email: 送信先メールアドレス
            user_name: ユーザー名
            reset_token: パスワード設定用トークン

        Returns:
            成功時True
        """
        reset_url = "{}/reset-password?token={}".format(
            EmailConfig.FRONTEND_URL,
            reset_token
        )

        subject = "【REA】アカウント登録完了のご案内"

        body_text = """
{name}様

REAへのアカウント登録が完了しました。
以下のURLからパスワードを設定してください。

{url}

このリンクは{hours}時間有効です。

--
REA - Real Estate Automation System
""".format(
            name=user_name if user_name else 'お客',
            url=reset_url,
            hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS
        )

        body_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #3B82F6; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>アカウント登録完了のご案内</h2>
        <p>{name}様</p>
        <p>REAへのアカウント登録が完了しました。<br>
        以下のボタンをクリックしてパスワードを設定してください。</p>
        <p style="margin: 30px 0;">
            <a href="{url}" class="button">パスワードを設定</a>
        </p>
        <p>または、以下のURLをブラウザに貼り付けてください：<br>
        <a href="{url}">{url}</a></p>
        <p>このリンクは<strong>{hours}時間</strong>有効です。</p>
        <div class="footer">
            <p>※ このメールは自動送信されています。返信しないでください。</p>
            <p>REA - Real Estate Automation System</p>
        </div>
    </div>
</body>
</html>
""".format(
            name=user_name if user_name else 'お客',
            url=reset_url,
            hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS
        )

        return EmailService.send_email(to_email, subject, body_text, body_html)
