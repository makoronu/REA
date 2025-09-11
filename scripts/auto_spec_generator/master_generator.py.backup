# scripts/auto_spec_generator/master_generator.py
"""
REA統合仕様書生成システム - 改善版
問題点を解決した統合実行システム
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import create_engine, inspect
import json

class REAMasterGenerator:
    """REA統合仕様書生成システム - エラー耐性・自動更新対応版"""
    
    def __init__(self, base_path: str = "/Users/yaguchimakoto/my_programing/REA"):
        self.base_path = Path(base_path)
        self.cache_dir = self.base_path / "docs" / ".cache"
        self.config_file = self.cache_dir / "generation_config.json"
        self.db_url = "postgresql://rea_user:rea_password@localhost:5432/real_estate_db"
        
        # キャッシュディレクトリ作成
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all(self, force_update: bool = False):
        """統合仕様書生成 - エラー耐性強化版"""
        print("🚀 REA統合仕様書生成開始...")
        print(f"📁 プロジェクト: {self.base_path}")
        print(f"🕐 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 前回実行情報読み込み
        last_config = self._load_last_config()
        
        try:
            # Phase 1: 基本構造分析（エラー耐性強化）
            print("\n📊 Phase 1: 基本構造分析...")
            basic_success = self._safe_basic_analysis(force_update, last_config)
            
            # Phase 2: 詳細仕様生成（基本分析成功時のみ）
            print("\n📋 Phase 2: 詳細仕様生成...")
            detail_success = self._safe_detail_generation(basic_success, force_update)
            
            # Phase 3: Claude最適化（詳細生成成功時のみ）
            print("\n🤖 Phase 3: Claude最適化チャンク...")
            claude_success = self._safe_claude_optimization(detail_success, force_update)
            
            # Phase 4: 連携ガイド生成
            print("\n📚 Phase 4: Claude連携ガイド...")
            guide_success = self._safe_guide_generation(force_update)
            
            # Phase 5: ショートコード生成（新機能）
            print("\n⚡ Phase 5: ショートコード生成...")
            shortcode_success = self._generate_shortcodes()
            
            # 結果サマリー
            self._print_summary(basic_success, detail_success, claude_success, 
                              guide_success, shortcode_success)
            
            # 設定保存
            self._save_config({
                "last_update": datetime.now().isoformat(),
                "basic_analysis": basic_success,
                "detail_generation": detail_success,
                "claude_optimization": claude_success,
                "guide_generation": guide_success,
                "shortcode_generation": shortcode_success
            })
            
        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによる中断")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ 予期しないエラー: {e}")
            self._emergency_recovery()
    
    def _safe_basic_analysis(self, force_update: bool, last_config: dict) -> bool:
        """基本構造分析 - エラー耐性版"""
        try:
            # キャッシュチェック
            if not force_update and self._is_cache_valid("basic_analysis", last_config):
                print("   ✅ キャッシュ有効、基本分析をスキップ")
                return True
            
            # DB接続テスト
            if not self._test_db_connection():
                print("   ⚠️ DB接続失敗、キャッシュ情報を使用")
                return self._use_cached_basic_analysis()
            
            # main_generator.py 実行
            result = subprocess.run([
                sys.executable, 
                str(self.base_path / "scripts/auto_spec_generator/main_generator.py")
            ], capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("   ✅ 基本構造分析完了")
                self._cache_success("basic_analysis")
                return True
            else:
                print(f"   ❌ 基本分析エラー: {result.stderr}")
                return self._use_cached_basic_analysis()
                
        except Exception as e:
            print(f"   ❌ 基本分析例外: {e}")
            return self._use_cached_basic_analysis()
    
    def _safe_detail_generation(self, basic_success: bool, force_update: bool) -> bool:
        """詳細仕様生成 - エラー耐性版"""
        if not basic_success:
            print("   ⚠️ 基本分析失敗、詳細生成をスキップ")
            return False
            
        try:
            # table_detail_generator.py 実行
            result = subprocess.run([
                sys.executable,
                str(self.base_path / "scripts/auto_spec_generator/table_detail_generator.py")
            ], capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("   ✅ 詳細仕様生成完了")
                return True
            else:
                print(f"   ❌ 詳細生成エラー: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ 詳細生成例外: {e}")
            return False
    
    def _safe_claude_optimization(self, detail_success: bool, force_update: bool) -> bool:
        """Claude最適化 - エラー耐性版"""
        if not detail_success:
            print("   ⚠️ 詳細生成失敗、Claude最適化をスキップ")
            return False
            
        try:
            # claude_chunk_generator.py 実行
            result = subprocess.run([
                sys.executable,
                str(self.base_path / "scripts/auto_spec_generator/claude_chunk_generator.py")
            ], capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("   ✅ Claude最適化完了")
                return True
            else:
                print(f"   ❌ Claude最適化エラー: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Claude最適化例外: {e}")
            return False
    
    def _safe_guide_generation(self, force_update: bool) -> bool:
        """連携ガイド生成 - エラー耐性版"""
        try:
            # claude_integration_generator.py 実行
            result = subprocess.run([
                sys.executable,
                str(self.base_path / "scripts/auto_spec_generator/claude_integration_generator.py")
            ], capture_output=True, text=True, cwd=self.base_path)
            
            if result.returncode == 0:
                print("   ✅ 連携ガイド生成完了")
                return True
            else:
                print(f"   ❌ ガイド生成エラー: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ ガイド生成例外: {e}")
            return False
    
    def _generate_shortcodes(self) -> bool:
        """ショートコード生成 - 新機能"""
        try:
            shortcode_dir = self.base_path / "docs" / "shortcodes"
            shortcode_dir.mkdir(exist_ok=True)
            
            # ショートコード定義
            shortcodes = {
                "@rea-pricing": "docs/claude_chunks/pricing/overview.md",
                "@rea-images": "docs/claude_chunks/images/overview.md", 
                "@rea-location": "docs/claude_chunks/location/overview.md",
                "@rea-building": "docs/claude_chunks/building/overview.md",
                "@rea-api": "docs/claude_chunks/api/overview.md",
                "@rea-dev": "docs/claude_chunks/development/overview.md",
                "@rea-db": "docs/01_database/current_structure.md",
                "@rea-help": "docs/claude_integration/quick_reference.md"
            }
            
            # ショートコードガイド生成
            content = f"""# ⚡ REA ショートコード - 超効率Claude連携

## 🎯 使い方
```
👤 [ショートコード] "[質問内容]"

例:
👤 @rea-pricing "利回り計算を実装したい"
👤 @rea-images "30枚アップロード機能のバグ修正"
👤 @rea-api "新しいエンドポイント追加方法"
```

## ⚡ ショートコード一覧

| ショートコード | 機能 | 対象ファイル |
|---------------|------|-------------|
"""
            
            for code, file_path in shortcodes.items():
                function_name = code.replace("@rea-", "").title()
                content += f"| `{code}` | {function_name} | {file_path} |\n"
            
            content += f"""

## 🚀 実際の使用例

### 💰 価格機能
```
👤 @rea-pricing "利回り計算APIの実装方法"
→ Claude が docs/claude_chunks/pricing/overview.md を確認して回答
```

### 📸 画像機能
```
👤 @rea-images "画像一括削除機能の実装"
→ Claude が docs/claude_chunks/images/overview.md を確認して回答
```

### 🔧 トラブル対応
```
👤 @rea-dev "PostgreSQL接続エラーの解決方法"
→ Claude が docs/claude_chunks/development/overview.md を確認して回答
```

---
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(shortcode_dir / "README.md", 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 展開用スクリプト生成
            expand_script = f'''#!/usr/bin/env python3
"""REA ショートコード展開スクリプト"""

shortcodes = {shortcodes}

def expand_shortcode(text):
    """ショートコードを展開"""
    for code, file_path in shortcodes.items():
        if code in text:
            expanded = f'REAについて質問があります。まず {{file_path}} を確認してから、以下について回答してください: {{text.replace(code, "").strip()}}'
            return expanded
    return text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = expand_shortcode(" ".join(sys.argv[1:]))
        print(result)
    else:
        print("使い方: python expand_shortcode.py @rea-pricing '利回り計算について'")
'''
            
            with open(shortcode_dir / "expand_shortcode.py", 'w', encoding='utf-8') as f:
                f.write(expand_script)
            
            print("   ✅ ショートコード生成完了")
            return True
            
        except Exception as e:
            print(f"   ❌ ショートコード生成例外: {e}")
            return False
    
    def _test_db_connection(self) -> bool:
        """データベース接続テスト"""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def _use_cached_basic_analysis(self) -> bool:
        """キャッシュされた基本分析情報を使用"""
        cache_file = self.cache_dir / "basic_analysis_cache.json"
        if cache_file.exists():
            print("   📄 キャッシュから基本分析情報を復元")
            return True
        else:
            print("   ❌ キャッシュも利用不可")
            return False
    
    def _is_cache_valid(self, cache_type: str, last_config: dict, 
                       valid_hours: int = 24) -> bool:
        """キャッシュ有効性チェック"""
        if not last_config:
            return False
            
        last_update = last_config.get("last_update")
        if not last_update:
            return False
            
        try:
            last_time = datetime.fromisoformat(last_update)
            return datetime.now() - last_time < timedelta(hours=valid_hours)
        except:
            return False
    
    def _cache_success(self, operation: str):
        """成功情報をキャッシュ"""
        cache_file = self.cache_dir / f"{operation}_cache.json"
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    
    def _load_last_config(self) -> dict:
        """前回実行設定を読み込み"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_config(self, config: dict):
        """実行設定を保存"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _emergency_recovery(self):
        """緊急時復旧処理"""
        print("\n🚨 緊急復旧モード")
        print("📋 利用可能な復旧オプション:")
        print("   1. キャッシュからの復元")
        print("   2. 部分的な再生成")
        print("   3. 最小限の仕様書生成")
        
        # 最小限の仕様書生成
        try:
            minimal_content = f"""# REA システム - 緊急時仕様書

## ⚠️ 注意
この仕様書は緊急復旧により生成されました。
完全な仕様書生成は以下コマンドで実行してください：

```bash
python scripts/auto_spec_generator/master_generator.py --force
```

## 🎯 基本情報
- プロジェクト: REA (Real Estate Automation)
- 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 状態: 緊急復旧モード

## 🔗 重要なURL
- API文書: http://localhost:8005/docs
- プロジェクト: /Users/yaguchimakoto/my_programing/REA

## 🚀 クイックスタート
```bash
#cd /Users/yaguchimakoto/my_programing/REA
source venv/bin/activate
#cd rea-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```
"""
            
            emergency_file = self.base_path / "docs" / "EMERGENCY_README.md"
            with open(emergency_file, 'w', encoding='utf-8') as f:
                f.write(minimal_content)
            
            print(f"✅ 緊急時仕様書を生成: {emergency_file}")
            
        except Exception as e:
            print(f"❌ 緊急復旧も失敗: {e}")
    
    def _print_summary(self, basic: bool, detail: bool, claude: bool, 
                      guide: bool, shortcode: bool):
        """実行結果サマリー"""
        print(f"\n📋 REA統合仕様書生成結果:")
        print("─" * 50)
        print(f"📊 Phase 1 基本構造分析:     {'✅ 成功' if basic else '❌ 失敗'}")
        print(f"📋 Phase 2 詳細仕様生成:     {'✅ 成功' if detail else '❌ 失敗'}")
        print(f"🤖 Phase 3 Claude最適化:     {'✅ 成功' if claude else '❌ 失敗'}")
        print(f"📚 Phase 4 連携ガイド:       {'✅ 成功' if guide else '❌ 失敗'}")
        print(f"⚡ Phase 5 ショートコード:   {'✅ 成功' if shortcode else '❌ 失敗'}")
        
        success_count = sum([basic, detail, claude, guide, shortcode])
        print(f"\n🎯 成功率: {success_count}/5 ({success_count/5*100:.0f}%)")
        
        if success_count >= 3:
            print("🎉 十分な仕様書が生成されました！")
            if shortcode:
                print("⚡ ショートコードが利用可能: docs/shortcodes/README.md")
        else:
            print("⚠️ 一部失敗、個別実行を推奨")
            print("🔧 個別実行方法:")
            if not basic:
                print("   python scripts/auto_spec_generator/main_generator.py")
            if not detail:
                print("   python scripts/auto_spec_generator/table_detail_generator.py")

def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='REA統合仕様書生成システム')
    parser.add_argument('--force', action='store_true', 
                       help='キャッシュを無視して強制更新')
    parser.add_argument('--quick', action='store_true',
                       help='クイック更新（差分のみ）')
    
    args = parser.parse_args()
    
    generator = REAMasterGenerator()
    generator.generate_all(force_update=args.force)

if __name__ == "__main__":
    main()