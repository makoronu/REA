# generators/program_structure_generator.py
import sys
from pathlib import Path
from typing import Dict, Any
from .base_generator import BaseGenerator

class ProgramStructureGenerator(BaseGenerator):
    """プログラム構造仕様生成クラス"""
    
    def generate(self) -> Dict[str, Any]:
        """プログラム構造仕様生成"""
        try:
            # Pythonパスにベースパスを追加
            sys.path.append(str(self.base_path))
            
            # コード解析器をインポート
            from analyzers.code_analyzer import CodeAnalyzer
            
            # プロジェクト全体を解析
            analyzer = CodeAnalyzer(self.base_path)
            summary = analyzer.get_project_summary()
            
            content = f"""# 🏗️ REAプログラム構造仕様

## 📋 生成情報
- **生成日時**: {self.get_timestamp()}
- **プロジェクトパス**: {self.base_path}
- **総ファイル数**: {summary['total_files']}
- **総関数数**: {summary['total_functions']}
- **総クラス数**: {summary['total_classes']}
- **総行数**: {summary['total_lines']:,}

## 📈 モジュール別構造

| No | ファイル | 行数 | 関数数 | クラス数 | 用途 |
|----|----------|------|--------|----------|------|
"""
            
            # ファイル別詳細
            for i, file_info in enumerate(summary['files'], 1):
                file_path = file_info['file_path']
                lines = file_info.get('lines', 0)
                func_count = len(file_info.get('functions', []))
                class_count = len(file_info.get('classes', []))
                purpose = self._classify_file_purpose(file_path, file_info)
                
                content += f"| {i} | `{file_path}` | {lines} | {func_count} | {class_count} | {purpose} |\n"
            
            content += f"""
## 📊 統計サマリー
- **平均ファイルサイズ**: {summary['total_lines'] // max(summary['total_files'], 1)}行
- **関数密度**: {summary['total_functions'] / max(summary['total_files'], 1):.1f}関数/ファイル
- **クラス密度**: {summary['total_classes'] / max(summary['total_files'], 1):.1f}クラス/ファイル

## 🎯 主要モジュール詳細

"""
            
            # 主要ファイルの詳細分析
            for file_info in summary['files']:
                if file_info.get('lines', 0) > 50 or len(file_info.get('classes', [])) > 0:
                    content += self._generate_file_detail(file_info)
            
            # 依存関係分析
            content += self._generate_dependency_analysis(summary['files'])
            
            # ファイル保存
            program_dir = self.get_output_dir("05_program_structure")
            self.save_content(content, program_dir / "current_structure.md")
            
            self.print_status(f"✅ プログラム構造: {summary['total_files']}ファイル分析完了")
            return {
                "success": True,
                "files": summary['total_files'],
                "functions": summary['total_functions'],
                "classes": summary['total_classes'],
                "lines": summary['total_lines']
            }
            
        except Exception as e:
            self.print_status(f"❌ プログラム構造分析エラー: {e}")
            # フォールバック用の最小限仕様書生成
            fallback_content = f"""# ❌ プログラム構造分析エラー

## 🚨 エラー内容
```
{e}
```

## 🔧 対処方法
1. プロジェクトパス確認: {self.base_path}
2. Python環境確認: venv有効化
3. analyzers モジュール確認

**エラー発生時刻**: {self.get_timestamp()}
"""
            
            program_dir = self.get_output_dir("05_program_structure")
            self.save_content(fallback_content, program_dir / "current_structure.md")
            
            return {"success": False, "error": str(e)}
    
    def _classify_file_purpose(self, file_path: str, file_info: Dict[str, Any]) -> str:
        """ファイルの用途を自動分類"""
        
        # パターンマッチング
        if "main.py" in file_path:
            return "メインエントリーポイント"
        elif "test" in file_path.lower():
            return "テストファイル"
        elif "config" in file_path.lower():
            return "設定ファイル"
        elif "generator" in file_path:
            return "仕様書生成器"
        elif "scraper" in file_path:
            return "スクレイピング機能"
        elif "api" in file_path:
            return "API関連"
        elif "database" in file_path:
            return "データベース操作"
        elif "analyzer" in file_path:
            return "分析・解析機能"
        elif "shared" in file_path:
            return "共通ライブラリ"
        elif "__init__.py" in file_path:
            return "モジュール初期化"
        
        # クラス・関数の内容による判定
        classes = file_info.get('classes', [])
        functions = file_info.get('functions', [])
        
        if len(classes) > len(functions):
            return "クラス中心モジュール"
        elif len(functions) > 5:
            return "ユーティリティモジュール"
        elif file_info.get('lines', 0) > 200:
            return "大規模モジュール"
        else:
            return "機能モジュール"
    
    def _generate_file_detail(self, file_info: Dict[str, Any]) -> str:
        """ファイル詳細情報生成"""
        file_path = file_info['file_path']
        content = f"\n### {file_path}\n"
        content += f"**行数**: {file_info.get('lines', 0)}  \n"
        content += f"**複雑度**: {file_info.get('complexity', 0)}  \n"
        
        # docstring
        if file_info.get('docstring'):
            content += f"**説明**: {file_info['docstring'][:100]}...  \n"
        
        # クラス一覧
        classes = file_info.get('classes', [])
        if classes:
            content += f"**クラス**: "
            class_names = [cls['name'] for cls in classes]
            content += ", ".join(class_names) + "  \n"
        
        # 主要関数
        functions = file_info.get('functions', [])
        if functions:
            content += f"**関数**: "
            func_names = [func['name'] for func in functions[:5]]
            content += ", ".join(func_names)
            if len(functions) > 5:
                content += f" ...他{len(functions)-5}関数"
            content += "  \n"
        
        return content
    
    def _generate_dependency_analysis(self, files: list) -> str:
        """依存関係分析"""
        content = "\n## 🔗 依存関係分析\n\n"
        
        # import統計
        all_imports = []
        internal_imports = []
        external_imports = []
        
        for file_info in files:
            imports = file_info.get('imports', [])
            for imp in imports:
                module = imp.get('module', '')
                all_imports.append(module)
                
                if any(keyword in module for keyword in ['rea', 'shared', 'generators', 'analyzers']):
                    internal_imports.append(module)
                else:
                    external_imports.append(module)
        
        # 外部ライブラリ使用状況
        content += "### 外部ライブラリ使用状況\n"
        external_counts = {}
        for lib in external_imports:
            if lib and not lib.startswith('.'):
                root_lib = lib.split('.')[0]
                external_counts[root_lib] = external_counts.get(root_lib, 0) + 1
        
        sorted_libs = sorted(external_counts.items(), key=lambda x: x[1], reverse=True)
        for lib, count in sorted_libs[:10]:
            content += f"- **{lib}**: {count}回使用  \n"
        
        # 内部モジュール依存
        content += "\n### 内部モジュール依存\n"
        internal_counts = {}
        for module in internal_imports:
            if module:
                internal_counts[module] = internal_counts.get(module, 0) + 1
        
        sorted_internal = sorted(internal_counts.items(), key=lambda x: x[1], reverse=True)
        for module, count in sorted_internal[:10]:
            content += f"- **{module}**: {count}回参照  \n"
        
        return content