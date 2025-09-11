# generators/shared_library_analyzer.py - 全関数完全検出版
import os
import re
from pathlib import Path
from typing import Any, Dict, List


class SharedLibraryAnalyzer:
    """shared/ ライブラリ完全分析クラス（全関数検出版）"""

    def __init__(self, base_path: Path, output_dir: Path):
        self.base_path = Path(base_path)
        self.output_dir = Path(output_dir)
        self.shared_dir = self.base_path / "shared"

    def generate(self) -> Dict[str, Any]:
        """shared/ライブラリ完全分析実行"""
        print("   📚 shared/ライブラリ完全分析中...")

        if not self.shared_dir.exists():
            print("   ❌ shared/ディレクトリが存在しません")
            return {"status": "error", "message": "shared directory not found"}

        # Python ファイル一覧取得
        python_files = list(self.shared_dir.glob("*.py"))
        python_files = [f for f in python_files if f.name != "__init__.py"]

        print(f"   🔍 分析対象: {len(python_files)}ファイル")

        analysis_results = {}

        # 各ファイルを詳細分析
        for file_path in python_files:
            print(f"\n   📁 {file_path.name}")

            try:
                file_analysis = self._analyze_python_file(file_path)
                analysis_results[file_path.name] = file_analysis

                # ファイルdocstring表示
                if file_analysis.get("file_docstring"):
                    doc_summary = file_analysis["file_docstring"].split("\n")[0][:60]
                    print(f"      📝 {doc_summary}")

                # インポート情報表示
                imports = file_analysis.get("imports", [])
                if imports:
                    print(f"      📦 インポート: {len(imports)}個")
                    for imp in imports[:3]:  # 最初の3個まで表示
                        print(f"      │   ├── {imp}")
                    if len(imports) > 3:
                        print(f"      │   └── ...他{len(imports) - 3}個")

                # クラス情報表示
                classes = file_analysis.get("classes", {})
                if classes:
                    for class_name, class_info in classes.items():
                        print(f"      ├── 🏗️ {class_name} クラス")
                        if class_info.get("docstring"):
                            doc_summary = class_info["docstring"].split("\n")[0][:50]
                            print(f"      │   └── 📝 {doc_summary}")

                        methods = class_info.get("methods", [])
                        if methods:
                            for method in methods[:5]:  # 最初の5個まで表示
                                print(
                                    f"      │   ├── {method['name']}({method['params']}) {method['return_type']}"
                                )
                                if method.get("docstring"):
                                    doc_summary = method["docstring"].split("\n")[0][
                                        :40
                                    ]
                                    print(f"      │   │   └── 📝 {doc_summary}")
                            if len(methods) > 5:
                                print(f"      │   └── ...他{len(methods) - 5}個メソッド")

                # 関数情報表示（全関数）
                functions = file_analysis.get("functions", {})
                if functions:
                    for func_name, func_info in functions.items():
                        params = func_info.get("params", "")
                        return_type = func_info.get("return_type", "")
                        print(f"      ├── ⚙️ {func_name}({params}) {return_type}")
                        if func_info.get("docstring"):
                            doc_summary = func_info["docstring"].split("\n")[0][:50]
                            print(f"      │   └── 📝 {doc_summary}")

                # 定数情報表示
                constants = file_analysis.get("constants", [])
                if constants:
                    print(f"      ├── 📊 定数: {len(constants)}個")
                    for const in constants[:3]:  # 最初の3個まで表示
                        print(f"      │   ├── {const}")
                    if len(constants) > 3:
                        print(f"      │   └── ...他{len(constants) - 3}個")

                # 統計情報表示
                line_count = file_analysis.get("line_count", 0)
                total_functions = (
                    len(classes.get(list(classes.keys())[0], {}).get("methods", []))
                    if classes
                    else 0
                )
                total_functions += len(functions)
                print(f"      └── 📊 総行数: {line_count}行, 総関数数: {total_functions}個")

            except Exception as e:
                print(f"      ❌ 分析エラー: {e}")
                analysis_results[file_path.name] = {"error": str(e)}

        # 分析結果をMarkdownファイルに出力
        self._generate_complete_reference(analysis_results)

        print(f"\n   ✅ shared/ライブラリ分析完了: {len(python_files)}ファイル")

        return {
            "status": "success",
            "files_analyzed": len(python_files),
            "analysis_results": analysis_results,
        }

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Pythonファイルの詳細分析（全関数検出版）"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # ファイルレベルのdocstring抽出
            file_docstring = self._extract_file_docstring(content)

            # クラス詳細分析
            classes = self._extract_classes_detailed(content)

            # 全関数詳細分析（クラス内外全て）
            functions = self._extract_all_functions_detailed(content)

            # インポート詳細分析
            imports = self._extract_imports_detailed(lines)

            # 定数検索（大文字の変数）
            constants = []
            for line in lines:
                match = re.match(r"^([A-Z_]+)\s*=", line.strip())
                if match:
                    constants.append(match.group(1))

            return {
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "line_count": len(lines),
                "file_docstring": file_docstring,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "constants": constants,
            }

        except Exception as e:
            return {"error": f"ファイル分析エラー: {e}"}

    def _extract_file_docstring(self, content: str) -> str:
        """ファイルレベルのdocstring抽出"""
        # ファイル先頭の三重クォート文字列を探す
        match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()

        match = re.search(r"^'''(.*?)'''", content, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()

        return ""

    def _extract_classes_detailed(self, content: str) -> Dict[str, Dict]:
        """クラスの詳細分析（docstring・メソッド込み）"""
        classes = {}

        # クラス定義を検索
        class_pattern = r"^class\s+(\w+).*?:\s*\n((?:.*\n)*?)(?=^class|\Z)"
        class_matches = re.finditer(class_pattern, content, re.MULTILINE)

        for match in class_matches:
            class_name = match.group(1)
            class_body = match.group(2)

            # クラスのdocstring抽出
            docstring = ""
            docstring_match = re.search(
                r'^\s*"""(.*?)"""', class_body, re.DOTALL | re.MULTILINE
            )
            if docstring_match:
                docstring = docstring_match.group(1).strip()

            # メソッド抽出
            methods = []
            method_pattern = r"^\s*def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*([^:]+?))?\s*:"
            method_matches = re.finditer(method_pattern, class_body, re.MULTILINE)

            for method_match in method_matches:
                method_name = method_match.group(1)
                params = method_match.group(2) if method_match.group(2) else ""
                return_type = (
                    f"-> {method_match.group(3).strip()}"
                    if method_match.group(3)
                    else ""
                )

                # メソッドのdocstring抽出
                method_docstring = ""
                method_start = method_match.end()
                remaining_body = class_body[method_start:]
                method_doc_match = re.search(
                    r'^\s*"""(.*?)"""', remaining_body, re.DOTALL | re.MULTILINE
                )
                if method_doc_match:
                    method_docstring = method_doc_match.group(1).strip()

                methods.append(
                    {
                        "name": method_name,
                        "params": params,
                        "return_type": return_type,
                        "docstring": method_docstring,
                    }
                )

            classes[class_name] = {"docstring": docstring, "methods": methods}

        return classes

    def _extract_all_functions_detailed(self, content: str) -> Dict[str, Dict]:
        """全関数の詳細分析（クラス内外全て対象）"""
        functions = {}

        lines = content.split("\n")

        for i, line in enumerate(lines):
            # def で始まる行を全て検出
            if re.match(r"\s*def\s+", line):
                match = re.match(
                    r"\s*def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*([^:]+?))?\s*:", line
                )
                if match:
                    func_name = match.group(1)
                    params = match.group(2) if match.group(2) else ""
                    return_type = (
                        f"-> {match.group(3).strip()}" if match.group(3) else ""
                    )

                    # docstring抽出（次の行から探す）
                    docstring = ""
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if j < len(lines):
                            next_line = lines[j].strip()
                            if next_line.startswith('"""') or next_line.startswith(
                                "'''"
                            ):
                                # docstring発見
                                if (
                                    next_line.count('"""') >= 2
                                    or next_line.count("'''") >= 2
                                ):
                                    # 同じ行で完結
                                    docstring = (
                                        next_line.strip('"""').strip("'''").strip()
                                    )
                                else:
                                    # 複数行docstring
                                    doc_lines = [next_line.strip('"""').strip("'''")]
                                    for k in range(j + 1, min(j + 5, len(lines))):
                                        if k < len(lines):
                                            doc_line = lines[k]
                                            if '"""' in doc_line or "'''" in doc_line:
                                                doc_lines.append(
                                                    doc_line.split('"""')[0].split(
                                                        "'''"
                                                    )[0]
                                                )
                                                break
                                            doc_lines.append(doc_line.strip())
                                    docstring = " ".join(doc_lines).strip()
                                break
                            elif next_line and not next_line.startswith("#"):
                                # docstringがない場合は終了
                                break

                    functions[func_name] = {
                        "params": params,
                        "return_type": return_type,
                        "docstring": docstring,
                    }

        return functions

    def _extract_imports_detailed(self, lines: List[str]) -> List[str]:
        """インポート文の詳細抽出"""
        imports = []

        for line in lines:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                # コメントを除去
                if "#" in line:
                    line = line[: line.index("#")].strip()
                imports.append(line)

        return imports

    def _generate_complete_reference(self, analysis_results: Dict[str, Any]):
        """完全リファレンスMarkdownファイル生成（全関数版）"""
        shared_dir = self.output_dir / "04_shared"
        shared_dir.mkdir(parents=True, exist_ok=True)

        reference_file = shared_dir / "complete_library_reference.md"

        content = []
        content.append("# 🔬 shared/ ライブラリ完全リファレンス（全関数検出版）")
        content.append("")
        content.append("**生成日時**: 自動生成")
        content.append(f"**分析ファイル数**: {len(analysis_results)}")
        content.append("")
        content.append("## 📋 ファイル一覧")
        content.append("")

        # ファイル一覧テーブル
        content.append("| No | ファイル名 | サイズ | クラス数 | 全関数数 | 行数 | 説明 |")
        content.append(
            "|----|------------|--------|----------|----------|------|------|"
        )

        for i, (filename, analysis) in enumerate(analysis_results.items(), 1):
            if "error" in analysis:
                content.append(f"| {i} | {filename} | - | - | - | - | ❌ エラー |")
            else:
                size_kb = analysis.get("file_size", 0) // 1024
                class_count = len(analysis.get("classes", {}))

                # 全関数数計算（クラス内メソッド + モジュールレベル関数）
                total_func_count = len(analysis.get("functions", {}))
                for class_info in analysis.get("classes", {}).values():
                    total_func_count += len(class_info.get("methods", []))

                line_count = analysis.get("line_count", 0)
                file_doc = analysis.get("file_docstring", "")
                doc_summary = file_doc.split("\n")[0][:30] if file_doc else "-"
                content.append(
                    f"| {i} | {filename} | {size_kb}KB | {class_count} | {total_func_count} | {line_count} | {doc_summary} |"
                )

        content.append("")

        # 各ファイルの詳細情報
        for filename, analysis in analysis_results.items():
            if "error" in analysis:
                content.append(f"## 📁 {filename}")
                content.append("")
                content.append(f"❌ 分析エラー: {analysis['error']}")
                content.append("")
                continue

            content.append(f"## 📁 {filename}")
            content.append("")

            # ファイル説明
            if analysis.get("file_docstring"):
                content.append("### 📝 ファイル説明")
                content.append("```")
                content.append(analysis["file_docstring"])
                content.append("```")
                content.append("")

            # 基本情報
            size_kb = analysis.get("file_size", 0) // 1024
            line_count = analysis.get("line_count", 0)

            # 全関数数計算
            total_func_count = len(analysis.get("functions", {}))
            for class_info in analysis.get("classes", {}).values():
                total_func_count += len(class_info.get("methods", []))

            content.append(f"- **サイズ**: {size_kb}KB")
            content.append(f"- **行数**: {line_count}行")
            content.append(f"- **総関数数**: {total_func_count}個")
            content.append("")

            # インポート詳細
            imports = analysis.get("imports", [])
            if imports:
                content.append("### 📦 インポート詳細")
                content.append("")
                for imp in imports:
                    content.append(f"- `{imp}`")
                content.append("")

            # クラス詳細
            classes = analysis.get("classes", {})
            if classes:
                content.append("### 🏗️ クラス詳細")
                content.append("")

                for class_name, class_info in classes.items():
                    content.append(f"#### `{class_name}` クラス")
                    content.append("")

                    if class_info.get("docstring"):
                        content.append("**説明**:")
                        content.append("```")
                        content.append(class_info["docstring"])
                        content.append("```")
                        content.append("")

                    methods = class_info.get("methods", [])
                    if methods:
                        content.append(f"**メソッド一覧**: {len(methods)}個")
                        content.append("")

                        for method in methods:
                            method_sig = f"`{method['name']}({method['params']}) {method['return_type']}`"
                            content.append(f"- {method_sig}")
                            if method.get("docstring"):
                                content.append(
                                    f"  - 📝 {method['docstring'].split(chr(10))[0]}"
                                )
                            content.append("")

            # モジュールレベル関数詳細
            functions = analysis.get("functions", {})
            if functions:
                content.append("### ⚙️ モジュールレベル関数")
                content.append("")

                for func_name, func_info in functions.items():
                    func_sig = f"`{func_name}({func_info['params']}) {func_info['return_type']}`"
                    content.append(f"#### {func_sig}")
                    content.append("")

                    if func_info.get("docstring"):
                        content.append("**説明**:")
                        content.append("```")
                        content.append(func_info["docstring"])
                        content.append("```")
                        content.append("")

            # 定数一覧
            constants = analysis.get("constants", [])
            if constants:
                content.append("### 📊 定数")
                content.append("")

                for const in constants:
                    content.append(f"- `{const}`")
                content.append("")

            content.append("---")
            content.append("")

        # サマリー
        total_classes = sum(
            len(a.get("classes", {}))
            for a in analysis_results.values()
            if "error" not in a
        )
        total_functions = 0
        total_lines = sum(
            a.get("line_count", 0)
            for a in analysis_results.values()
            if "error" not in a
        )

        for analysis in analysis_results.values():
            if "error" not in analysis:
                total_functions += len(analysis.get("functions", {}))
                for class_info in analysis.get("classes", {}).values():
                    total_functions += len(class_info.get("methods", []))

        content.append("## 📊 サマリー")
        content.append("")
        content.append(f"- **分析ファイル数**: {len(analysis_results)}")
        content.append(f"- **総クラス数**: {total_classes}")
        content.append(f"- **総関数数**: {total_functions}")
        content.append(f"- **総行数**: {total_lines}")
        content.append("")
        content.append("---")
        content.append("")
        content.append("*このドキュメントは自動生成されました（全関数検出版）*")

        # ファイル書き込み
        with open(reference_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        print(f"   ✅ 完全リファレンス生成: {reference_file}")
