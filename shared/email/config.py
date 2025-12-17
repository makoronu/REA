# メール設定
import os


class EmailConfig:
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'noreply@example.com')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'REA System')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    PASSWORD_RESET_EXPIRE_HOURS = int(os.getenv('PASSWORD_RESET_EXPIRE_HOURS', '24'))
