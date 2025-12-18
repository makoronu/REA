"""
Claude API 基本使用例

使い方:
1. 環境変数 ANTHROPIC_API_KEY を設定
   export ANTHROPIC_API_KEY="sk-ant-xxxxx"

2. 実行
   python3 scripts/claude_api_example.py
"""

import os
import anthropic


def simple_chat(prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    シンプルなチャット

    model options:
    - claude-opus-4-20250514 (最高性能、高コスト)
    - claude-sonnet-4-20250514 (バランス型、推奨)
    - claude-3-5-haiku-20241022 (高速、低コスト)
    """
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY 環境変数から自動読み込み

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def chat_with_system(prompt: str, system: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    システムプロンプト付きチャット
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def streaming_chat(prompt: str, model: str = "claude-sonnet-4-20250514"):
    """
    ストリーミング出力（リアルタイム表示）
    """
    client = anthropic.Anthropic()

    with client.messages.stream(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print()  # 改行


def multi_turn_chat():
    """
    複数ターンの会話
    """
    client = anthropic.Anthropic()
    messages = []

    print("会話を開始します。'quit'で終了。\n")

    while True:
        user_input = input("あなた: ")
        if user_input.lower() == 'quit':
            break

        messages.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=messages
        )

        assistant_message = response.content[0].text
        messages.append({"role": "assistant", "content": assistant_message})

        print(f"Claude: {assistant_message}\n")


if __name__ == "__main__":
    # APIキー確認
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY 環境変数を設定してください")
        print("例: export ANTHROPIC_API_KEY='sk-ant-xxxxx'")
        exit(1)

    print("=== Claude API テスト ===\n")

    # 1. シンプルな呼び出し
    print("1. シンプルチャット:")
    response = simple_chat("こんにちは。一言で自己紹介して。")
    print(f"   {response}\n")

    # 2. システムプロンプト付き
    print("2. システムプロンプト付き:")
    response = chat_with_system(
        prompt="東京の天気は？",
        system="あなたは関西弁で話す気象予報士です。"
    )
    print(f"   {response}\n")

    # 3. ストリーミング
    print("3. ストリーミング出力:")
    streaming_chat("Pythonでfizzbuzzを書いて")
