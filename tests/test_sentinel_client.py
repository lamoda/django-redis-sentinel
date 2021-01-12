# -*- coding: utf-8 -*-
import pytest
import time
from datetime import datetime
from django.core.cache import caches

from django_redis.serializers import json as json_serializer
from django_redis.serializers import msgpack as msgpack_serializer


class TestDjangoSentinelCache():
    @pytest.fixture()
    def cache(self):
        yield caches["default"]
        caches["default"].clear()

    def test_setnx(self, cache):
        # we should ensure there is no test_key_nx in redis
        cache.delete("test_key_nx")
        res = cache.get("test_key_nx", None)
        assert res is None

        res = cache.set("test_key_nx", 1, nx=True)
        assert res
        # test that second set will have
        res = cache.set("test_key_nx", 2, nx=True)
        assert not res
        res = cache.get("test_key_nx")
        assert res == 1

        cache.delete("test_key_nx")
        res = cache.get("test_key_nx", None)
        assert res is None

    def test_setnx_timeout(self, cache):
        # test that timeout still works for nx=True
        res = cache.set("test_key_nx", 1, timeout=2, nx=True)
        assert res
        time.sleep(3)
        res = cache.get("test_key_nx", None)
        assert res is None

        # test that timeout will not affect key, if it was there
        cache.set("test_key_nx", 1)
        res = cache.set("test_key_nx", 2, timeout=2, nx=True)
        assert not res
        time.sleep(3)
        res = cache.get("test_key_nx", None)
        assert res == 1

        cache.delete("test_key_nx")
        res = cache.get("test_key_nx", None)
        assert res is None

    def test_save_and_integer(self, cache):
        cache.set("test_key", 2)
        res = cache.get("test_key", "Foo")

        assert isinstance(res, int)
        assert res == 2

    def test_save_string(self, cache):
        cache.set("test_key", "hello" * 1000)
        res = cache.get("test_key")

        assert isinstance(res, str)
        assert res == "hello" * 1000

        cache.set("test_key", "2")
        res = cache.get("test_key")

        assert isinstance(res, str)
        assert res == "2"

    def test_save_unicode(self, cache):
        cache.set("test_key", "heló")
        res = cache.get("test_key")

        assert isinstance(res, str)
        assert res == "heló"

    def test_save_dict(self, cache):
        if isinstance(cache.client._serializer,
                      json_serializer.JSONSerializer):
            self.skipTest("Datetimes are not JSON serializable")

        if isinstance(cache.client._serializer,
                      msgpack_serializer.MSGPackSerializer):
            # MSGPackSerializer serializers use the isoformat for datetimes
            # https://github.com/msgpack/msgpack-python/issues/12
            now_dt = datetime.now().isoformat()
        else:
            now_dt = datetime.now()

        test_dict = {"id": 1, "date": now_dt, "name": "Foo"}

        cache.set("test_key", test_dict)
        res = cache.get("test_key")

        assert isinstance(res, dict)
        assert res["id"] == 1
        assert res["name"] == "Foo"
        assert res["date"] == now_dt

    def test_save_float(self, cache):
        float_val = 1.345620002

        cache.set("test_key", float_val)
        res = cache.get("test_key")

        assert isinstance(res, float)
        assert res == float_val

    def test_timeout(self, cache):
        cache.set("test_key", 222, timeout=3)
        time.sleep(4)

        res = cache.get("test_key", None)
        assert res is None

    def test_timeout_0(self, cache):
        cache.set("test_key", 222, timeout=0)
        res = cache.get("test_key", None)
        assert res is None

    def test_set_add(self, cache):
        cache.set("add_key", "Initial value")
        cache.add("add_key", "New value")
        res = cache.get("add_key")

        assert res == "Initial value"

    def test_get_many(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        res = cache.get_many(["a", "b", "c"])
        assert res == {"a": 1, "b": 2, "c": 3}

    def test_get_many_unicode(self, cache):
        cache.set("a", "1")
        cache.set("b", "2")
        cache.set("c", "3")

        res = cache.get_many(["a", "b", "c"])
        assert res == {"a": "1", "b": "2", "c": "3"}

    def test_set_many(self, cache):
        cache.set_many({"a": 1, "b": 2, "c": 3})
        res = cache.get_many(["a", "b", "c"])
        assert res == {"a": 1, "b": 2, "c": 3}

    def test_delete(self, cache):
        cache.set_many({"a": 1, "b": 2, "c": 3})
        res = cache.delete("a")
        assert bool(res)

        res = cache.get_many(["a", "b", "c"])
        assert res == {"b": 2, "c": 3}

        res = cache.delete("a")
        assert not bool(res)

    def test_delete_many(self, cache):
        cache.set_many({"a": 1, "b": 2, "c": 3})
        res = cache.delete_many(["a", "b"])
        assert bool(res)

        res = cache.get_many(["a", "b", "c"])
        assert res == {"c": 3}

        res = cache.delete_many(["a", "b"])
        assert not bool(res)

    def test_delete_many_generator(self, cache):
        cache.set_many({"a": 1, "b": 2, "c": 3})
        res = cache.delete_many(key for key in ["a", "b"])
        assert bool(res)

        res = cache.get_many(["a", "b", "c"])
        assert res == {"c": 3}

        res = cache.delete_many(["a", "b"])
        assert not bool(res)

    def test_delete_many_empty_generator(self, cache):
        res = cache.delete_many(key for key in [])
        assert not bool(res)

    def test_incr(self, cache):
        cache.set("num", 1)

        cache.incr("num")
        res = cache.get("num")
        assert res == 2

        cache.incr("num", 10)
        res = cache.get("num")
        assert res == 12

        # max 64 bit signed int
        cache.set("num", 9223372036854775807)

        cache.incr("num")
        res = cache.get("num")
        assert res == 9223372036854775808

        cache.incr("num", 2)
        res = cache.get("num")
        assert res == 9223372036854775810

        cache.set("num", 3)

        cache.incr("num", 2)
        res = cache.get("num")
        assert res == 5

    def test_incr_error(self, cache):
        with pytest.raises(ValueError):
            # key not exists
            cache.incr('numnum')

    def test_get_set_bool(self, cache):
        cache.set("bool", True)
        res = cache.get("bool")

        assert isinstance(res, bool)
        assert res is True

        cache.set("bool", False)
        res = cache.get("bool")

        assert isinstance(res, bool)
        assert res is False

    def test_decr(self, cache):
        cache.set("num", 20)

        cache.decr("num")
        res = cache.get("num")
        assert res == 19

        cache.decr("num", 20)
        res = cache.get("num")
        assert res == -1

        cache.decr("num", 2)
        res = cache.get("num")
        assert res == -3

        cache.set("num", 20)

        cache.decr("num")
        res = cache.get("num")
        assert res == 19

        # max 64 bit signed int + 1
        cache.set("num", 9223372036854775808)

        cache.decr("num")
        res = cache.get("num")
        assert res == 9223372036854775807

        cache.decr("num", 2)
        res = cache.get("num")
        assert res == 9223372036854775805

    def test_version(self, cache):
        cache.set("keytest", 2, version=2)
        res = cache.get("keytest")
        assert res is None

        res = cache.get("keytest", version=2)
        assert res == 2

    def test_incr_version(self, cache):
        cache.set("keytest", 2)
        cache.incr_version("keytest")

        res = cache.get("keytest")
        assert res is None

        res = cache.get("keytest", version=2)
        assert res == 2

    def test_delete_pattern(self, cache):
        for key in ["foo-aa", "foo-ab", "foo-bb", "foo-bc"]:
            cache.set(key, "foo")

        res = cache.delete_pattern("*foo-a*")
        assert bool(res)

        keys = cache.keys("foo*")
        assert set(keys) == {"foo-bb", "foo-bc"}

        res = cache.delete_pattern("*foo-a*")
        assert not bool(res)

    def test_close(self, cache):
        cache.set("f", "1")
        cache.close()

    def test_ttl(self, cache):
        # Test ttl
        cache.set("foo", "bar", 10)
        ttl = cache.ttl("foo")
        assert ttl + 0.5 > 10

        # Test ttl None
        cache.set("foo", "foo", timeout=None)
        ttl = cache.ttl("foo")
        assert ttl is None

        # Test ttl with expired key
        cache.set("foo", "foo", timeout=-1)
        ttl = cache.ttl("foo")
        assert ttl == 0

        # Test ttl with not existent key
        ttl = cache.ttl("not-existent-key")
        assert ttl == 0

    def test_persist(self, cache):
        cache.set("foo", "bar", timeout=20)
        cache.persist("foo")

        ttl = cache.ttl("foo")
        assert ttl is None

    def test_expire(self, cache):
        cache.set("foo", "bar", timeout=None)
        cache.expire("foo", 20)
        ttl = cache.ttl("foo")
        assert ttl + 0.5 > 20

    def test_lock(self, cache):
        lock = cache.lock("foobar")
        lock.acquire(blocking=True)

        assert cache.has_key("foobar")
        lock.release()
        assert not cache.has_key("foobar")

    def test_iter_keys(self, cache):
        cache.set("foo1", 1)
        cache.set("foo2", 1)
        cache.set("foo3", 1)

        # Test simple result
        result = set(cache.iter_keys("foo*"))
        assert result == {"foo1", "foo2", "foo3"}

        # Test limited result
        result = list(cache.iter_keys("foo*", itersize=2))
        assert len(result) == 3

        # Test generator object
        result = cache.iter_keys("foo*")
        assert next(result) is not None


class TestDjangoSentinelCacheWithPrefixedCache(TestDjangoSentinelCache):
    @pytest.fixture()
    def cache(self):
        yield caches["with_prefix"]
        caches["with_prefix"].clear()


class TestDjangoSentinelCacheWithBlockingConnectionPool(TestDjangoSentinelCache):
    @pytest.fixture()
    def cache(self):
        yield caches["with_blocking_connection_pool"]
        caches["with_blocking_connection_pool"].clear()
