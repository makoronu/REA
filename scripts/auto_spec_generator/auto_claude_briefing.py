#!/usr/bin/env python3
# auto_claude_briefing.py - Claude記憶システム完全自動実行
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import pyperclip  # クリップボード操作用

class AutoClaudeBriefing:
    """Claude記憶システム完全自動実行クラス"""
    
    def __init__(self):
        self.base_path = Path("/Users/yaguchimakoto/my_programing/REA")
        self.script_path = self.base_path / "scripts" / "auto_spec_generator"
        
    def run_full_automation(self):
        """完全自動実行"""
        print("🚀 Claude記憶システム完全自動実行開始...")
        
        try:
            # Step 1: 最新記憶データ生成
            self._update_memory_system()
            
            # Step 2: 記憶ファイル確認・検証
            memory_content = self._verify_memory_files()
            
            # Step 3: Claude用ブリーフィング生成
            briefing = self._generate_claude_briefing(memory_content)
            
            # Step 4: クリップボードに自動コピー
            self._copy_to_clipboard(briefing)
            
            # Step 5: 完了報告
            self._print_completion_report()
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            sys.exit(1)
    
    def _update_memory_system(self):
        """記憶システム更新"""
        print("📊 最新記憶データ生成中...")
        
        # main.py 実行
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=self.script_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"記憶システム更新失敗: {result.stderr}")
        
        print("   ✅ 記憶システム更新完了")
    
    def _verify_memory_files(self):
        """記憶ファイル確認・検証"""
        print("🔍 記憶ファイル確認中...")
        
        memory_dir = self.base_path / "docs" / "claude_memory"
        required_files = [
            "INSTANT_CONTEXT.md",
            "PROJECT_STATUS.md", 
            "QUICK_COMMANDS.md"
        ]
        
        memory_content = {}
        
        for file_name in required_files:
            file_path = memory_dir / file_name
            if not file_path.exists():
                raise Exception(f"記憶ファイル未生成: {file_name}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                memory_content[file_name] = f.read()
        
        print(f"   ✅ 記憶ファイル確認完了: {len(required_files)}ファイル")
        return memory_content
    
    def _generate_claude_briefing(self, memory_content):
        """Claude用ブリーフィング生成"""
        print("🤖 Claude用ブリーフィング生成中...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 最重要情報抽出
        instant_context = memory_content["INSTANT_CONTEXT.md"]
        
        # 簡潔なサマリー生成
        briefing = f"""🧠 Claude自動復活ブリーフィング ({timestamp})

REAプロジェクトについて質問があります。
まず以下の最新コンテキストで現在の状況を把握してください：

{instant_context}

📋 追加情報:
- プロジェクト記憶システム: 完全自動更新済み
- 最終更新: {timestamp}
- 自動生成: auto_claude_briefing.py

---
この情報で現状把握後、作業を開始してください。🚀
"""
        
        print("   ✅ Claude用ブリーフィング生成完了")
        return briefing
    
    def _copy_to_clipboard(self, briefing):
        """クリップボードに自動コピー"""
        print("📋 クリップボードに自動コピー中...")
        
        try:
            pyperclip.copy(briefing)
            print("   ✅ クリップボードコピー完了")
        except Exception as e:
            print(f"   ⚠️ クリップボードコピー失敗: {e}")
            print("   💡 手動で以下をコピーしてください:")
            print("-" * 50)
            print(briefing)
            print("-" * 50)
    
    def _print_completion_report(self):
        """完了報告"""
        print("\n🎉 Claude記憶システム完全自動実行完了！")
        print("─" * 50)
        print("✅ 記憶システム更新: 最新状況反映")
        print("✅ 記憶ファイル確認: 3ファイル検証済み")
        print("✅ ブリーフィング生成: Claude用最適化")
        print("✅ クリップボードコピー: 即座貼り付け可能")
        print("\n🚀 次のアクション:")
        print("   1. 新しいClaude会話を開始")
        print("   2. Cmd+V でブリーフィング貼り付け")
        print("   3. Claude自動復活完了！")
        print("\n⚡ ワンコマンド実行: python auto_claude_briefing.py")

def main():
    """メイン実行"""
    briefing = AutoClaudeBriefing()
    briefing.run_full_automation()

if __name__ == "__main__":
    main()