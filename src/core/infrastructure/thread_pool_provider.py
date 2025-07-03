import os
import typing as t
from concurrent.futures import ThreadPoolExecutor

from src.settings import Settings


class ThreadPoolProvider:
    """Singleton Instance for ThreadPool"""

    _singleton: t.ClassVar[t.Optional["ThreadPoolExecutor"]] = None

    @classmethod
    def get(cls) -> "ThreadPoolExecutor":
        if cls._singleton is None:
            app_max_thread_pool_workers = Settings.get().app_max_thread_pool_workers
            singleton = ThreadPoolExecutor(
                max_workers=min(os.cpu_count(), app_max_thread_pool_workers)
            )
            cls._singleton = singleton
        return cls._singleton
