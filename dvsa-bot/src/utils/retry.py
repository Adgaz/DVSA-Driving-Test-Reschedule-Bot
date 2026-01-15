import time
import functools
from typing import Callable
from .logger import get_logger

logger = get_logger(__name__)

def retry(max_attempts: int = 3, delay: float = 1, exponential_backoff: bool = False):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    wait_time = delay * (2 ** attempt) if exponential_backoff else delay
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
        
        return wrapper
    return decorator
