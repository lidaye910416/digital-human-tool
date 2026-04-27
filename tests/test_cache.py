import pytest
from src.middleware.cache import CacheMiddleware

def test_cache_set_get():
    cache = CacheMiddleware(ttl=60)
    cache.set("test_key", {"data": "test"})
    result = cache.get("test_key")
    assert result == {"data": "test"}

def test_cache_expiry():
    cache = CacheMiddleware(ttl=1)
    cache.set("expire_key", "value")
    import time
    time.sleep(2)
    result = cache.get("expire_key")
    assert result is None
