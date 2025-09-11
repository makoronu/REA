# scripts/auto_spec_generator/analyzers/code_analyzer.py

import ast
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class CodeAnalyzer:
    """Pythonコード解析クラス"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.files_data = []

    def get_project_summary(self) -> Dict[str, Any]:
        """プロジェクト全体のサマリーを取得"""
        # Pythonファイルを収集
        python_files = self._collect_python_files()

        # 各ファイルを解析
        total_lines = 0
        total_functions = 0
        total_classes = 0

        for py_file in python_files:
            file_info = self._analyze_file(py_file)
            self.files_data.append(file_info)

            total_lines += file_info.get("lines", 0)
            total_functions += len(file_info.get("functions", []))
            total_classes += len(file_info.get("classes", []))

        return {
            "total_files": len(self.files_data),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_lines": total_lines,
            "files": self.files_data,
        }

    def _collect_python_files(self) -> List[Path]:
        """Pythonファイルを収集"""
        python_files = []

        # 除外パターン
        exclude_patterns = [
            "venv/",
            "__pycache__/",
            "node_modules/",
            ".git/",
            "build/",
            "dist/",
            ".pytest_cache/",
            "migrations/",
            "alembic/versions/",
        ]

        # プロジェクト内の全Pythonファイルを検索
        for root, dirs, files in os.walk(self.base_path):
            # 除外ディレクトリをスキップ
            dirs[:] = [
                d
                for d in dirs
                if not any(pattern in f"{root}/{d}/" for pattern in exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.base_path)

                    # 除外パターンチェック
                    if not any(
                        pattern in str(relative_path) for pattern in exclude_patterns
                    ):
                        python_files.append(file_path)

        return sorted(python_files)

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """個別ファイルを解析"""
        relative_path = file_path.relative_to(self.base_path)

        result = {
            "file_path": str(relative_path),
            "lines": 0,
            "functions": [],
            "classes": [],
            "imports": [],
            "docstring": None,
            "complexity": 0,
        }

        try:
            # ファイル読み込み
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 行数カウント
            result["lines"] = len(content.splitlines())

            # 空ファイルチェック
            if not content.strip():
                return result

            # AST解析
            try:
                tree = ast.parse(content)

                # モジュールdocstring取得
                if (
                    isinstance(tree, ast.Module)
                    and tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, (ast.Str, ast.Constant))
                ):
                    if isinstance(tree.body[0].value, ast.Str):
                        result["docstring"] = tree.body[0].value.s.strip()
                    else:
                        result["docstring"] = str(tree.body[0].value.value).strip()

                # ノード解析
                for node in ast.walk(tree):
                    # 関数解析
                    if isinstance(node, ast.FunctionDef) or isinstance(
                        node, ast.AsyncFunctionDef
                    ):
                        func_info = {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [
                                self._get_decorator_name(d) for d in node.decorator_list
                            ],
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                        }

                        # docstring取得
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, (ast.Str, ast.Constant))
                        ):
                            if isinstance(node.body[0].value, ast.Str):
                                func_info["docstring"] = node.body[0].value.s.strip()
                            else:
                                func_info["docstring"] = str(
                                    node.body[0].value.value
                                ).strip()

                        result["functions"].append(func_info)

                        # 複雑度計算（簡易版）
                        for child in ast.walk(node):
                            if isinstance(
                                child,
                                (
                                    ast.If,
                                    ast.For,
                                    ast.While,
                                    ast.ExceptHandler,
                                    ast.With,
                                ),
                            ):
                                result["complexity"] += 1

                    # クラス解析
                    elif isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "bases": [],
                            "decorators": [
                                self._get_decorator_name(d) for d in node.decorator_list
                            ],
                            "methods": [],
                        }

                        # 基底クラス取得
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                class_info["bases"].append(base.id)
                            elif isinstance(base, ast.Attribute):
                                class_info["bases"].append(
                                    f"{base.value.id}.{base.attr}"
                                )

                        # メソッド数カウント
                        method_count = sum(
                            1
                            for n in node.body
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        )
                        class_info["method_count"] = method_count

                        result["classes"].append(class_info)

                    # インポート解析
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            result["imports"].append(
                                {"module": alias.name, "alias": alias.asname}
                            )
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            result["imports"].append(
                                {
                                    "module": f"{module}.{alias.name}"
                                    if module
                                    else alias.name,
                                    "alias": alias.asname,
                                    "from_import": True,
                                }
                            )

            except SyntaxError as e:
                result["syntax_error"] = str(e)

        except Exception as e:
            result["error"] = str(e)

        return result

    def _get_decorator_name(self, node) -> str:
        """デコレータ名を取得"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return node.func.attr
        elif isinstance(node, ast.Attribute):
            return node.attr
        return "unknown"

    def get_file_summary(self, file_path: Path) -> Dict[str, Any]:
        """特定ファイルのサマリーを取得"""
        return self._analyze_file(file_path)
