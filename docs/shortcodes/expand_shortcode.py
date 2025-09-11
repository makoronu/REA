#!/usr/bin/env python3
"""REA ショートコード展開スクリプト"""

shortcodes = {
    "@rea-pricing": "docs/claude_chunks/pricing/overview.md",
    "@rea-images": "docs/claude_chunks/images/overview.md",
    "@rea-location": "docs/claude_chunks/location/overview.md",
    "@rea-building": "docs/claude_chunks/building/overview.md",
    "@rea-api": "docs/claude_chunks/api/overview.md",
    "@rea-dev": "docs/claude_chunks/development/overview.md",
    "@rea-db": "docs/01_database/current_structure.md",
    "@rea-help": "docs/claude_integration/quick_reference.md",
}


def expand_shortcode(text):
    """ショートコードを展開"""
    for code, file_path in shortcodes.items():
        if code in text:
            expanded = f'REAについて質問があります。まず {file_path} を確認してから、以下について回答してください: {text.replace(code, "").strip()}'
            return expanded
    return text


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = expand_shortcode(" ".join(sys.argv[1:]))
        print(result)
    else:
        print("使い方: python expand_shortcode.py @rea-pricing '利回り計算について'")
