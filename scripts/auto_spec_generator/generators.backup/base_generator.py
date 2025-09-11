# generators/base_generator.py
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class BaseGenerator(ABC):
    """生成クラスの基底クラス"""
    
    def __init__(self, base_path: Path, output_dir: Path):
        self.base_path = base_path
        self.output_dir = output_dir
        
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """生成処理（各サブクラスで実装）"""
        pass
        
    def get_output_dir(self, subdir: str) -> Path:
        """出力ディレクトリ取得・作成"""
        dir_path = self.output_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
        
    def save_content(self, content: str, filepath: Path) -> None:
        """コンテンツ保存"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def get_timestamp(self) -> str:
        """タイムスタンプ取得"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def print_status(self, message: str) -> None:
        """ステータス出力"""
        print(f"   {message}")