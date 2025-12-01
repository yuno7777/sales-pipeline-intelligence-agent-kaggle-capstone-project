import time
import functools
from typing import Callable, Any
from utils import logger

def measure_time(tool_name: str) -> Callable:
    """
    Decorator to measure execution time of a function and log structured metadata.
    
    Args:
        tool_name: The name of the tool being measured.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                # Log the exception here if needed, or just let the caller handle it
                # We'll log the failure in the finally block
                raise e
            finally:
                duration = time.time() - start_time
                status = "success" if success else "failure"
                logger.info(
                    f"[observability] Tool: {tool_name} | Status: {status} | Duration: {duration:.4f}s"
                )
        return wrapper
    return decorator
