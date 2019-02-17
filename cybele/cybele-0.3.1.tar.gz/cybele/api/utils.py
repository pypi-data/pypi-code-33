from functools import wraps
import time

import pyperclip
from tqdm import tqdm


def flush_clipboard(after=10):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                for _ in tqdm(range(after * 10), desc="Copied to clipboard", bar_format="{l_bar}|{bar}|"):
                    time.sleep(1 / 10)
                pyperclip.copy("")
                return result
            finally:
                pyperclip.copy("")

        return wrapper

    return decorator
