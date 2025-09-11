# 🏢 REA Project Complete Specification

**Generated**: 2025-07-19T07:21:49.934952
**Mode**: live

---

## 🚀 Overview
- **Project Name**: REA (Real Estate Automation)
- **Description**: 不動産業務完全自動化システム Python版
- **Project Path**: /Users/yaguchimakoto/my_programing/REA
- **Current Phase**: Phase 2/5 完了（スクレイピング実装済み）
- **Api Url**: http://localhost:8005
- **Github**: https://github.com/makoronu/REA

## 📊 Database Structure

### Summary
- **Total Tables**: 1
- **Total Columns**: 1
- **Total Records**: 1

### Table Details

#### alembic_version
- Columns: 1
- Records: 1

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| version_num | character varying | NO |  |

## 🔌 API Specification

### Total Endpoints: 0
**Base URL**: http://localhost:8005

| Method | Path | Summary |
|--------|------|---------|

## 💻 Implementation Status

### ✅ Completed

**Phase 1: データベース基盤・API**
- PostgreSQL 15 + 11テーブル
- FastAPI + 8エンドポイント
- 元請会社情報管理機能

**Phase 2: スクレイピング（Mac版）**
- ホームズ対応完了
- 段階処理システム実装
- Bot対策実装済み

### 🔄 In Progress
**Phase 3: React管理画面・自動入稿** (設計段階)

### ⏳ Planned
- Phase 4: AI機能・検索最適化
- Phase 5: 公開検索サイト

## 📝 Recent Changes

**Last Update**: 2025-07-19 07:21

**Recent Commits:**
- f7b828c 🎉 REA Python版プロジェクト初期化

## 🛠 Development Guide

### Tech Stack

**Backend:**
- Python 3.9+
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL 15
- Docker

**Scraping:**
- Selenium 4.15.2
- undetected-chromedriver 3.5.3
- BeautifulSoup4 4.12.2

**Planned:**
- React 18
- TypeScript
- Tailwind CSS

### Code Patterns
- **Api**: FastAPI + Pydantic + SQLAlchemy
- **Scraping**: 段階処理 + Bot対策
- **Error Handling**: 全体書き直し方式

### Important Notes
- Mac環境（macOS）で開発
- プロジェクトパス: /Users/yaguchimakoto/my_programing/REA
- Python仮想環境: ./venv
- ポート: API=8005, DB=5432