"""
プロセス管理・監視機能
長時間実行のための安全対策
"""
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
from loguru import logger


class ProcessManager:
    """プロセス管理クラス"""

    def __init__(self, pid_file: str = "data/rea_scraper.pid"):
        self.pid_file = Path(pid_file)
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.start_time = datetime.now()
        self.max_runtime = timedelta(hours=12)  # 最大実行時間
        self.max_memory_mb = 2048  # 最大メモリ使用量(MB)

    def start(self) -> bool:
        """プロセス開始"""
        # 既存のプロセスをチェック
        if self.is_running():
            logger.warning("Another instance is already running")
            return False

        # PIDファイルに書き込み
        pid = os.getpid()
        self.pid_file.write_text(str(pid))
        logger.info(f"Process started with PID: {pid}")

        # シグナルハンドラー設定
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        return True

    def is_running(self) -> bool:
        """既存プロセスが実行中かチェック"""
        if not self.pid_file.exists():
            return False

        try:
            pid = int(self.pid_file.read_text().strip())
            # プロセスが存在するかチェック
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                # Pythonプロセスかチェック
                if "python" in process.name().lower():
                    return True
        except (ValueError, psutil.NoSuchProcess):
            pass

        # 古いPIDファイルを削除
        self.pid_file.unlink()
        return False

    def check_health(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        health = {"status": "healthy", "warnings": [], "metrics": {}}

        # メモリ使用量チェック
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        health["metrics"]["memory_mb"] = round(memory_mb, 2)

        if memory_mb > self.max_memory_mb:
            health["warnings"].append(f"High memory usage: {memory_mb:.0f}MB")
            health["status"] = "warning"

        # 実行時間チェック
        runtime = datetime.now() - self.start_time
        health["metrics"]["runtime_hours"] = round(runtime.total_seconds() / 3600, 2)

        if runtime > self.max_runtime:
            health["warnings"].append(f"Long runtime: {runtime}")
            health["status"] = "warning"

        # Chrome/ChromeDriverプロセスチェック
        chrome_count = self._count_chrome_processes()
        health["metrics"]["chrome_processes"] = chrome_count

        if chrome_count > 10:
            health["warnings"].append(f"Too many Chrome processes: {chrome_count}")
            health["status"] = "warning"

        # ディスク容量チェック
        disk_usage = psutil.disk_usage("/")
        health["metrics"]["disk_free_gb"] = round(
            disk_usage.free / 1024 / 1024 / 1024, 2
        )

        if disk_usage.percent > 90:
            health["warnings"].append(f"Low disk space: {disk_usage.percent}%")
            health["status"] = "critical"

        return health

    def cleanup_chrome_processes(self):
        """Chrome関連のプロセスをクリーンアップ"""
        killed = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if (
                    "chrome" in proc.info["name"].lower()
                    or "chromedriver" in proc.info["name"].lower()
                ):
                    # 親プロセスが存在しない場合はゾンビプロセス
                    if proc.ppid() == 1 or not psutil.pid_exists(proc.ppid()):
                        proc.kill()
                        killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed > 0:
            logger.info(f"Cleaned up {killed} zombie Chrome processes")

    def _count_chrome_processes(self) -> int:
        """Chrome関連プロセスをカウント"""
        count = 0
        for proc in psutil.process_iter(["name"]):
            try:
                if "chrome" in proc.info["name"].lower():
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return count

    def _handle_shutdown(self, signum, frame):
        """シャットダウン処理"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """クリーンアップ処理"""
        # PIDファイル削除
        if self.pid_file.exists():
            self.pid_file.unlink()

        # Chrome プロセスのクリーンアップ
        self.cleanup_chrome_processes()

        logger.info("Cleanup completed")


class ScraperMonitor:
    """スクレイパー監視・自動再起動"""

    def __init__(self, command: list, max_retries: int = 3):
        self.command = command
        self.max_retries = max_retries
        self.retry_count = 0
        self.process = None

    def start(self):
        """監視開始"""
        logger.info(f"Starting monitored process: {' '.join(self.command)}")

        while self.retry_count < self.max_retries:
            try:
                # プロセス開始
                self.process = subprocess.Popen(
                    self.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                logger.info(f"Process started with PID: {self.process.pid}")

                # プロセス監視
                while True:
                    # プロセスが終了したかチェック
                    retcode = self.process.poll()
                    if retcode is not None:
                        if retcode == 0:
                            logger.info("Process completed successfully")
                            return
                        else:
                            logger.error(f"Process exited with code: {retcode}")
                            self.retry_count += 1
                            break

                    # ヘルスチェック（1分ごと）
                    time.sleep(60)

                    # メモリチェック
                    try:
                        proc = psutil.Process(self.process.pid)
                        memory_mb = proc.memory_info().rss / 1024 / 1024
                        if memory_mb > 2048:
                            logger.warning(f"High memory usage: {memory_mb:.0f}MB")
                            # 必要なら再起動
                            if memory_mb > 3072:
                                logger.error("Memory limit exceeded, restarting...")
                                self.process.terminate()
                                self.retry_count += 1
                                break
                    except psutil.NoSuchProcess:
                        logger.error("Process disappeared")
                        self.retry_count += 1
                        break

            except Exception as e:
                logger.error(f"Error in monitor: {e}")
                self.retry_count += 1

            if self.retry_count < self.max_retries:
                wait_time = min(300 * self.retry_count, 1800)  # 最大30分待機
                logger.info(
                    f"Retrying in {wait_time} seconds... (attempt {self.retry_count}/{self.max_retries})"
                )
                time.sleep(wait_time)

        logger.error("Max retries exceeded")

    def stop(self):
        """プロセス停止"""
        if self.process:
            self.process.terminate()
            self.process.wait()


def create_systemd_service():
    """systemdサービスファイルを作成（Linux用）"""
    service_content = """[Unit]
Description=REA Property Scraper
After=network.target postgresql.service

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
Environment="PATH={venv_path}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart={venv_path}/bin/python -m src.main process-all --batch-size 10 --interval 300 --save
Restart=on-failure
RestartSec=300
StandardOutput=append:{log_dir}/rea_scraper.log
StandardError=append:{log_dir}/rea_scraper_error.log

# リソース制限
MemoryLimit=2G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
"""

    # 設定値
    config = {
        "user": os.getenv("USER"),
        "working_dir": os.getcwd(),
        "venv_path": "/Users/yaguchimakoto/my_programing/REA/venv",
        "log_dir": os.path.join(os.getcwd(), "logs"),
    }

    service_file = service_content.format(**config)

    logger.info("Systemd service file:")
    logger.info(service_file)
    logger.info("\nSave this to: /etc/systemd/system/rea-scraper.service")
    logger.info(
        "Then run: sudo systemctl enable rea-scraper && sudo systemctl start rea-scraper"
    )


def create_launchd_plist():
    """launchdプリストファイルを作成（Mac用）"""
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rea.scraper</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{venv_path}/bin/python</string>
        <string>-m</string>
        <string>src.main</string>
        <string>process-all</string>
        <string>--batch-size</string>
        <string>10</string>
        <string>--interval</string>
        <string>300</string>
        <string>--save</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>{working_dir}</string>
    
    <key>StandardOutPath</key>
    <string>{log_dir}/rea_scraper.log</string>
    
    <key>StandardErrorPath</key>
    <string>{log_dir}/rea_scraper_error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>300</integer>
</dict>
</plist>
"""

    config = {
        "working_dir": os.getcwd(),
        "venv_path": "/Users/yaguchimakoto/my_programing/REA/venv",
        "log_dir": os.path.join(os.getcwd(), "logs"),
    }

    plist_file = plist_content.format(**config)

    logger.info("Launchd plist file:")
    logger.info(plist_file)
    logger.info("\nSave this to: ~/Library/LaunchAgents/com.rea.scraper.plist")
    logger.info("Then run: launchctl load ~/Library/LaunchAgents/com.rea.scraper.plist")


if __name__ == "__main__":
    # プロセス管理のテスト
    pm = ProcessManager()

    if pm.start():
        health = pm.check_health()
        logger.info(f"Health check: {health}")

        # クリーンアップ
        pm.cleanup_chrome_processes()
        pm.cleanup()

    # サービス設定の表示
    if sys.platform == "darwin":
        create_launchd_plist()
    else:
        create_systemd_service()
