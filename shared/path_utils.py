"""
REAプロジェクトパス自動設定ユーティリティ
"""
from pathlib import Path
import sys
from typing import Tuple

def setup_project_paths() -> Tuple[Path, Path]:
    """
    プロジェクトパスを自動設定
    
    Returns:
        tuple: (project_root, rea_scraper_root)
    """
    current = Path(__file__).resolve()
    
    # REAプロジェクトルートを探す
    while current.name != "REA" and current.parent != current:
        current = current.parent
    
    if current.name != "REA":
        raise ValueError("REAプロジェクトルートが見つかりません")
    
    project_root = current
    rea_scraper_root = project_root / "rea-scraper"
    
    # パスを追加
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(rea_scraper_root) not in sys.path:
        sys.path.insert(1, str(rea_scraper_root))
    
    return project_root, rea_scraper_root

def print_path_debug():
    """パス設定のデバッグ情報を表示"""
    project_root, rea_scraper_root = setup_project_paths()
    print(f"🔍 Project root: {project_root}")
    print(f"🔍 Rea-scraper root: {rea_scraper_root}")
    print(f"🔍 Shared exists: {(project_root / 'shared').exists()}")
    
    shared_dir = project_root / 'shared'
    if shared_dir.exists():
        print(f"✅ Shared files found: {len(list(shared_dir.glob('*.py')))} files")