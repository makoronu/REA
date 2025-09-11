"""
便利なデコレータ集
リトライ、キャッシュ、エラーハンドリング、パフォーマンス測定など
"""
import functools
import hashlib
import json
import pickle
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Type, Union

import redis
from loguru import logger
from src.config.settings import settings

# キャッシュ用Redisクライアント（オプション）
try:
    redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Using file-based cache.")
    redis_client = None


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_errors: bool = True,
) -> Callable:
    """
    リトライデコレータ

    Args:
        max_attempts: 最大試行回数
        delay: 初回リトライまでの待機時間（秒）
        backoff: リトライごとの待機時間倍率
        exceptions: リトライ対象の例外タプル
        log_errors: エラーをログに記録するか
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts:
                        if log_errors:
                            logger.error(
                                f"{func.__name__} failed after {max_attempts} attempts: {e}"
                            )
                        raise

                    if log_errors:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )

                    # ジッターを追加（同時リトライを避ける）
                    jitter = random.uniform(0, current_delay * 0.1)
                    time.sleep(current_delay + jitter)

                    current_delay *= backoff
                    attempt += 1

            return None

        return wrapper

    return decorator


def measure_time(func: Callable) -> Callable:
    """実行時間を測定するデコレータ"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            logger.debug(f"{func.__name__} completed in {execution_time:.2f} seconds")

            # 実行時間を結果に付加（辞書の場合）
            if isinstance(result, dict):
                result["_execution_time"] = execution_time

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {e}"
            )
            raise

    return wrapper


def cache(
    expire_seconds: int = 3600, cache_key_prefix: str = None, use_redis: bool = True
) -> Callable:
    """
    結果をキャッシュするデコレータ

    Args:
        expire_seconds: キャッシュ有効期限（秒）
        cache_key_prefix: キャッシュキーのプレフィックス
        use_redis: Redisを使用するか（Falseの場合はファイルキャッシュ）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # キャッシュキーを生成
            cache_key = _generate_cache_key(
                func.__name__, args, kwargs, prefix=cache_key_prefix
            )

            # キャッシュから取得を試みる
            cached_result = _get_from_cache(cache_key, use_redis)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # 関数を実行
            result = func(*args, **kwargs)

            # 結果をキャッシュに保存
            _save_to_cache(cache_key, result, expire_seconds, use_redis)
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper

    return decorator


def handle_errors(
    default_return: Any = None, log_traceback: bool = True, reraise: bool = False
) -> Callable:
    """
    エラーをハンドリングするデコレータ

    Args:
        default_return: エラー時のデフォルト戻り値
        log_traceback: トレースバックをログに記録するか
        reraise: エラーを再発生させるか
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                error_msg = f"Error in {func.__name__}: {e}"

                if log_traceback:
                    logger.exception(error_msg)
                else:
                    logger.error(error_msg)

                if reraise:
                    raise

                return default_return

        return wrapper

    return decorator


def rate_limit(
    calls: int = 1, period: float = 1.0, raise_on_limit: bool = False
) -> Callable:
    """
    レート制限デコレータ

    Args:
        calls: 期間内の最大呼び出し回数
        period: 期間（秒）
        raise_on_limit: 制限超過時に例外を発生させるか
    """

    def decorator(func: Callable) -> Callable:
        # 呼び出し履歴
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal call_times

            now = time.time()

            # 古い呼び出し履歴を削除
            call_times = [t for t in call_times if now - t < period]

            # レート制限チェック
            if len(call_times) >= calls:
                wait_time = period - (now - call_times[0])

                if raise_on_limit:
                    raise Exception(
                        f"Rate limit exceeded. Please wait {wait_time:.1f} seconds."
                    )

                logger.warning(
                    f"Rate limit reached for {func.__name__}. "
                    f"Waiting {wait_time:.1f} seconds..."
                )
                time.sleep(wait_time)

                # 再度古い履歴を削除
                now = time.time()
                call_times = [t for t in call_times if now - t < period]

            # 呼び出しを記録
            call_times.append(now)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_args(
    log_level: str = "DEBUG", log_return: bool = True, max_length: int = 200
) -> Callable:
    """
    関数の引数と戻り値をログに記録するデコレータ

    Args:
        log_level: ログレベル
        log_return: 戻り値もログに記録するか
        max_length: ログの最大文字数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 引数をログ
            args_str = _truncate_str(str(args), max_length)
            kwargs_str = _truncate_str(str(kwargs), max_length)

            logger.log(
                log_level,
                f"Calling {func.__name__} with args={args_str}, kwargs={kwargs_str}",
            )

            # 関数を実行
            result = func(*args, **kwargs)

            # 戻り値をログ
            if log_return:
                result_str = _truncate_str(str(result), max_length)
                logger.log(log_level, f"{func.__name__} returned: {result_str}")

            return result

        return wrapper

    return decorator


def timeout(seconds: int = 30) -> Callable:
    """
    タイムアウトデコレータ（Unix系OSのみ）

    Args:
        seconds: タイムアウト時間（秒）
    """
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Function timed out after {seconds} seconds")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Windowsでは使用不可
            if not hasattr(signal, "SIGALRM"):
                logger.warning("Timeout decorator is not supported on this platform")
                return func(*args, **kwargs)

            # タイムアウトを設定
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # タイムアウトを解除
                signal.alarm(0)

            return result

        return wrapper

    return decorator


def singleton(cls):
    """シングルトンパターンを実装するクラスデコレータ"""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


# ヘルパー関数
def _generate_cache_key(
    func_name: str, args: tuple, kwargs: dict, prefix: Optional[str] = None
) -> str:
    """キャッシュキーを生成"""
    # シリアライズ可能な形式に変換
    key_data = {
        "func": func_name,
        "args": str(args),
        "kwargs": str(sorted(kwargs.items())),
    }

    # ハッシュ化
    key_str = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()

    # プレフィックスを追加
    if prefix:
        return f"{prefix}:{key_hash}"
    return f"cache:{func_name}:{key_hash}"


def _get_from_cache(key: str, use_redis: bool = True) -> Optional[Any]:
    """キャッシュから値を取得"""
    try:
        if use_redis and redis_client:
            # Redisから取得
            data = redis_client.get(key)
            if data:
                return pickle.loads(data)
        else:
            # ファイルキャッシュから取得
            cache_dir = Path(settings.BASE_DIR) / ".cache"
            cache_file = cache_dir / f"{key}.pkl"

            if cache_file.exists():
                # 有効期限チェック
                if time.time() - cache_file.stat().st_mtime < 3600:  # 1時間
                    with open(cache_file, "rb") as f:
                        return pickle.load(f)
                else:
                    cache_file.unlink()  # 期限切れファイルを削除

    except Exception as e:
        logger.debug(f"Cache retrieval failed: {e}")

    return None


def _save_to_cache(key: str, value: Any, expire_seconds: int, use_redis: bool = True):
    """値をキャッシュに保存"""
    try:
        if use_redis and redis_client:
            # Redisに保存
            redis_client.setex(key, expire_seconds, pickle.dumps(value))
        else:
            # ファイルキャッシュに保存
            cache_dir = Path(settings.BASE_DIR) / ".cache"
            cache_dir.mkdir(exist_ok=True)

            cache_file = cache_dir / f"{key}.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(value, f)

    except Exception as e:
        logger.debug(f"Cache save failed: {e}")


def _truncate_str(s: str, max_length: int) -> str:
    """文字列を指定長で切り詰める"""
    if len(s) <= max_length:
        return s
    return s[: max_length - 3] + "..."


# テスト用関数
if __name__ == "__main__":
    # リトライのテスト
    @retry(max_attempts=3, delay=0.5)
    def unstable_function():
        import random

        if random.random() < 0.7:
            raise Exception("Random error")
        return "Success!"

    # 実行時間測定のテスト
    @measure_time
    def slow_function():
        time.sleep(0.5)
        return "Done"

    # キャッシュのテスト
    @cache(expire_seconds=10)
    def expensive_function(x, y):
        time.sleep(1)
        return x + y

    print("Testing decorators...")

    try:
        result = unstable_function()
        print(f"✓ Retry test: {result}")
    except:
        print("✗ Retry test failed")

    result = slow_function()
    print(f"✓ Timer test: {result}")

    # キャッシュテスト
    start = time.time()
    result1 = expensive_function(1, 2)
    time1 = time.time() - start

    start = time.time()
    result2 = expensive_function(1, 2)  # キャッシュから取得
    time2 = time.time() - start

    print(f"✓ Cache test: First call: {time1:.2f}s, Second call: {time2:.2f}s")
