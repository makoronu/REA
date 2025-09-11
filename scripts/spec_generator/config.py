import os
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

"""
REA仕様書生成ツール 設定ファイル
"""
from pathlib import Path

class Config:
    # パス設定
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    OUTPUT_DIR = PROJECT_ROOT / 'docs' / 'claude_specs'
    
    # データベース設定
    DB_NAME = os.getenv("DB_NAME", "real_estate_db")
    DB_USER = "rea_user"
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = "5432"
    
    # API設定
    API_URL = "http://localhost:8005"
    API_TIMEOUT = 2
    
    # プロジェクト情報
    PROJECT_NAME = "REA (Real Estate Automation)"
    DESCRIPTION = "不動産業務完全自動化システム Python版"
    GITHUB = "https://github.com/makoronu/REA"
    CURRENT_PHASE = "Phase 2/5 完了（スクレイピング実装済み）"
    
    # 実装状況
    COMPLETED_PHASES = [
        {
            'phase': 'Phase 1',
            'name': 'データベース基盤・API',
            'details': [
                'PostgreSQL 15 + 11テーブル',
                'FastAPI + 8エンドポイント', 
                '元請会社情報管理機能'
            ]
        },
        {
            'phase': 'Phase 2',
            'name': 'スクレイピング（Mac版）',
            'details': [
                'ホームズ対応完了',
                '段階処理システム実装',
                'Bot対策実装済み'
            ]
        }
    ]
    
    IN_PROGRESS = {
        'phase': 'Phase 3',
        'name': 'React管理画面・自動入稿',
        'progress': '設計段階'
    }
    
    PLANNED = [
        'Phase 4: AI機能・検索最適化',
        'Phase 5: 公開検索サイト'
    ]
    
    # 技術スタック
    TECH_STACK = {
        'backend': [
            'Python 3.9+',
            'FastAPI 0.104.1',
            'SQLAlchemy 2.0.23',
            'PostgreSQL 15',
            'Docker'
        ],
        'scraping': [
            'Selenium 4.15.2',
            'undetected-chromedriver 3.5.3',
            'BeautifulSoup4 4.12.2'
        ],
        'planned': [
            'React 18',
            'TypeScript',
            'Tailwind CSS'
        ]
    }