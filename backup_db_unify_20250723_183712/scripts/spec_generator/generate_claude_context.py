#!/usr/bin/env python3
"""
REA仕様書自動生成ツール メインスクリプト
シンプルで分かりやすい構成に改良
"""
import argparse
from datetime import datetime
from pathlib import Path

from config import Config
from extractors import APIExtractor, DatabaseExtractor, GitExtractor, ProjectExtractor
from formatters import MarkdownFormatter


class REASpecGenerator:
    def __init__(self, mode="auto"):
        self.mode = mode
        self.config = Config()
        self.output_dir = self.config.OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate(self):
        """仕様書を生成"""
        print("🚀 REA仕様書生成を開始します...")

        # モード判定
        if self.mode == "auto":
            self.mode = "live" if self._check_live_env() else "static"

        print(f"📋 モード: {self.mode}")

        # 各種情報を収集
        spec_data = {
            "generated_at": datetime.now().isoformat(),
            "mode": self.mode,
            "database": DatabaseExtractor().extract() if self.mode == "live" else {},
            "api": APIExtractor().extract() if self.mode == "live" else {},
            "project": ProjectExtractor().extract(),
            "git": GitExtractor().extract(),
        }

        # Markdown生成
        formatter = MarkdownFormatter()
        output = formatter.format(spec_data)

        # ファイル保存
        filename = f"REA_specification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename
        filepath.write_text(output, encoding="utf-8")

        # 最新版のシンボリックリンク
        latest = self.output_dir / "latest.md"
        if latest.exists():
            latest.unlink()
        latest.symlink_to(filename)

        print(f"✅ 生成完了: {filepath}")
        print(f"📎 Claude.aiに {latest} をアップロードしてください")

        return filepath

    def _check_live_env(self):
        """ライブ環境が利用可能かチェック"""
        try:
            # DB接続テスト
            import psycopg2

            conn = psycopg2.connect(
                dbname=self.config.DB_NAME,
                user=self.config.DB_USER,
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
            )
            conn.close()

            # API稼働チェック
            import requests

            requests.get(f"{self.config.API_URL}/docs", timeout=2)

            return True
        except:
            return False


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="REA仕様書を生成")
    parser.add_argument(
        "--mode", choices=["auto", "live", "static"], default="auto", help="実行モード"
    )
    parser.add_argument("--static", action="store_true", help="静的モードで実行")

    args = parser.parse_args()
    mode = "static" if args.static else args.mode

    generator = REASpecGenerator(mode=mode)
    generator.generate()


if __name__ == "__main__":
    main()
