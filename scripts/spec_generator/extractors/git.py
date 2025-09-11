"""
Git情報抽出モジュール
"""
import subprocess
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config

class GitExtractor:
    def __init__(self):
        self.config = Config()
    
    def extract(self):
        """Git情報を抽出"""
        return {
            'recent_commits': self._get_recent_commits(),
            'branch': self._get_current_branch(),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'stats': self._get_git_stats()
        }
    
    def _get_recent_commits(self, limit=10):
        """最近のコミットを取得"""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '-n', str(limit)],
                capture_output=True,
                text=True,
                cwd=self.config.PROJECT_ROOT
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                return [commit for commit in commits if commit]
            else:
                return []
        except Exception as e:
            print(f"Git情報取得エラー: {e}")
            return []
    
    def _get_current_branch(self):
        """現在のブランチを取得"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                cwd=self.config.PROJECT_ROOT
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _get_git_stats(self):
        """Git統計情報を取得"""
        stats = {
            'total_commits': 0,
            'contributors': [],
            'files_changed': 0
        }
        
        try:
            # コミット総数
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.config.PROJECT_ROOT
            )
            if result.returncode == 0:
                stats['total_commits'] = int(result.stdout.strip())
            
            # コントリビューター
            result = subprocess.run(
                ['git', 'shortlog', '-sn'],
                capture_output=True,
                text=True,
                cwd=self.config.PROJECT_ROOT
            )
            if result.returncode == 0:
                contributors = []
                for line in result.stdout.strip().split('\n')[:5]:  # 上位5人
                    if line:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            contributors.append({
                                'commits': int(parts[0]),
                                'name': parts[1]
                            })
                stats['contributors'] = contributors
            
            # 変更されたファイル数
            result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True,
                text=True,
                cwd=self.config.PROJECT_ROOT
            )
            if result.returncode == 0:
                stats['files_changed'] = len(result.stdout.strip().split('\n'))
            
        except Exception as e:
            print(f"Git統計取得エラー: {e}")
        
        return stats