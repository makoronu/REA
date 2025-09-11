#!/usr/bin/env python3
"""
REA DB関連ファイルの内容を一括出力するスクリプト
"""
from pathlib import Path

def dump_db_files():
    """DB関連ファイルの内容を出力"""
    
    project_root = Path("/Users/yaguchimakoto/my_programing/REA")
    
    # 確認したいファイルのリスト
    files_to_check = [
        # 設定ファイル
        ".env",
        "docker-compose.yml",
        
        # spec_generator系
        "scripts/spec_generator/config.py",
        "scripts/spec_generator/generate_claude_context.py",
        
        # auto_spec_generator系
        "scripts/auto_spec_generator/.env",
        "scripts/auto_spec_generator/master_generator.py",
        "scripts/auto_spec_generator/table_detail_generator.py",
        "scripts/auto_spec_generator/generators/database_generator.py",
        
        # rea-api系
        "rea-api/.env",
        "rea-api/app/core/config.py",
        "rea-api/app/core/database.py",
        
        # rea-scraper系
        "rea-scraper/.env",
        "rea-scraper/src/config/settings.py",
        "rea-scraper/src/config/database.py",
        
        # shared
        "shared/database.py",
    ]
    
    print("=" * 80)
    print("REA DB関連ファイル内容ダンプ")
    print("=" * 80)
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        
        print(f"\n{'=' * 80}")
        print(f"📄 ファイル: {file_path}")
        print("=" * 80)
        
        if not full_path.exists():
            print("❌ ファイルが存在しません")
            continue
            
        try:
            content = full_path.read_text()
            
            # パスワードを含む行をマスク
            lines = content.split('\n')
            masked_lines = []
            
            for line in lines:
                if any(keyword in line.upper() for keyword in ['PASSWORD', 'POSTGRES_PASSWORD', 'DB_PASSWORD']):
                    # パスワード値をマスク
                    if '=' in line:
                        key, _ = line.split('=', 1)
                        masked_lines.append(f"{key}=***MASKED***")
                    elif ':' in line and 'password' in line.lower():
                        # YAMLやPythonの辞書形式
                        masked_lines.append(re.sub(r'(password["\']?\s*[:=]\s*["\']?)([^"\']+)(["\']?)', r'\1***MASKED***\3', line, flags=re.IGNORECASE))
                    else:
                        masked_lines.append(line)
                else:
                    masked_lines.append(line)
                    
            print('\n'.join(masked_lines))
            
        except Exception as e:
            print(f"❌ 読み込みエラー: {e}")
            
    print(f"\n{'=' * 80}")
    print("ダンプ完了")
    print("=" * 80)

if __name__ == "__main__":
    import re  # 正規表現用
    dump_db_files()
