# analyzers/code_analyzer.py
import ast
import os
from pathlib import Path
from typing import Any, Dict, List


class CodeAnalyzer:
    """Python コード構造解析クラス"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Pythonファイルの構造を解析"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "imports": self._extract_imports(tree),
                "lines": len(content.splitlines()),
                "docstring": ast.get_docstring(tree),
                "complexity": self._calculate_complexity(tree),
            }
        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "error": str(e),
                "functions": [],
                "classes": [],
                "imports": [],
            }

    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """関数情報を抽出"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "decorators": [
                            d.id if isinstance(d, ast.Name) else str(d)
                            for d in node.decorator_list
                        ],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                )
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """クラス情報を抽出"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(
                            {
                                "name": item.name,
                                "line": item.lineno,
                                "args": [arg.arg for arg in item.args.args],
                            }
                        )

                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "bases": [
                            base.id if isinstance(base, ast.Name) else str(base)
                            for base in node.bases
                        ],
                        "methods": methods,
                    }
                )
        return classes

    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """import情報を抽出"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
        return imports

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """簡易的な複雑度計算"""
        complexity = 1  # 基本複雑度
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def scan_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """REAプロジェクトファイルを動的検出"""
        results = []

        # REAプロジェクトディレクトリを動的検出
        for item in directory.iterdir():
            if item.is_dir() and item.name.startswith("rea-"):
                # rea-api, rea-scraper, rea-admin等を自動検出
                for py_file in item.rglob("*.py"):
                    if "__pycache__" not in str(py_file) and "venv" not in str(py_file):
                        analysis = self.analyze_python_file(py_file)
                        results.append(analysis)

        # shared, scriptsも追加
        fixed_dirs = ["shared", "scripts/auto_spec_generator"]
        for fixed_dir in fixed_dirs:
            target_dir = directory / fixed_dir
            if target_dir.exists():
                for py_file in target_dir.rglob("*.py"):
                    if "__pycache__" not in str(py_file):
                        analysis = self.analyze_python_file(py_file)
                        results.append(analysis)

        return results

    def get_project_summary(self) -> Dict[str, Any]:
        """プロジェクト全体のサマリー"""
        all_files = self.scan_directory(self.project_root)

        total_functions = sum(len(f.get("functions", [])) for f in all_files)
        total_classes = sum(len(f.get("classes", [])) for f in all_files)
        total_lines = sum(f.get("lines", 0) for f in all_files)

        return {
            "total_files": len(all_files),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines": total_lines,
            "files": all_files,
        }
