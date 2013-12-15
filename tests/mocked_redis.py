from collections import defaultdict
from asyncio import Future
from functools import wraps


def as_future(func):
    def wrapper(*args, **kwargs):
        x = Future()
        res = func(*args, **kwargs)
        x.set_result(res)
        return x
    return wrapper


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)) and not attr.startswith('_'):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate

@for_all_methods(as_future)
class MockRedis(object):
    """Imitate a Redis object so unit tests can run on our Hudson CI server without needing a real
    Redis server."""

    # The 'Redis' store
    redis = defaultdict(dict)

    def __init__(self):
        """Initialize the object."""
        pass

    @classmethod
    def _reinit(cls):
        cls.redis = defaultdict(dict)


    def delete(self, key):  # pylint: disable=R0201
        """Emulate delete."""

        if key in MockRedis.redis:
            del MockRedis.redis[key]

    def exists(self, key):  # pylint: disable=R0201
        """Emulate get."""

        return key in MockRedis.redis

    def get(self, key):  # pylint: disable=R0201
        """Emulate get."""

        # Override the default dict
        result = None if key not in MockRedis.redis else MockRedis.redis[key]
        return result

    def hget(self, hashkey, attribute):  # pylint: disable=R0201
        """Emulate hget."""

        # Return '' if the attribute does not exist
        result = MockRedis.redis[hashkey][attribute] if attribute in MockRedis.redis[hashkey] \
                 else None
        return result

    def hgetall(self, hashkey):  # pylint: disable=R0201
        """Emulate hgetall."""

        return MockRedis.redis[hashkey]

    def hlen(self, hashkey):  # pylint: disable=R0201
        """Emulate hlen."""

        return len(MockRedis.redis[hashkey])

    def hmset(self, hashkey, value):  # pylint: disable=R0201
        """Emulate hmset."""

        # Iterate over every key:value in the value argument.
        for attributekey, attributevalue in value.items():
            MockRedis.redis[hashkey][attributekey] = attributevalue

    def hset(self, hashkey, attribute, value):  # pylint: disable=R0201
        """Emulate hset."""

        MockRedis.redis[hashkey][attribute] = value

    def keys(self, pattern):  # pylint: disable=R0201
        """Emulate keys."""
        import re

        # Make a regex out of pattern. The only special matching character we look for is '*'
        regex = '^' + pattern.replace('*', '.*') + '$'

        # Find every key that matches the pattern
        result = [key for key in MockRedis.redis.keys() if re.match(regex, key)]

        return result

    def sadd(self, key, value):  # pylint: disable=R0201
        """Emulate sadd."""

        # Does the set at this key already exist?
        if key in MockRedis.redis:
            # Yes, add this to the set
            MockRedis.redis[key].add(value)
        else:
            # No, override the defaultdict's default and create the set
            MockRedis.redis[key] = set([value])

    def smembers(self, key):  # pylint: disable=R0201
        """Emulate smembers."""

        return MockRedis.redis[key]

    def lindex(self, key, index):
        if key not in MockRedis.redis:
            return None
        else:
            data = MockRedis.redis[key]
            if not isinstance(data, list):
                return None
            else:
                if index > len(data) - 1:
                    return None
                else:
                    return data[index]

    def lpush(self, key, value):
        assert isinstance(value, list)
        if key in MockRedis.redis:
            MockRedis.redis[key] = value + MockRedis.redis[key]
        else:
            MockRedis.redis[key] = value

    def lpop(self, key):
        if key not in MockRedis.redis:
            return None
        elif len(MockRedis.redis[key]) < 1:
            return None
        else:
            return MockRedis.redis[key].pop(0)

    def rpush(self, key, value):
        assert isinstance(value, list)
        if key in MockRedis.redis:
            MockRedis.redis[key] += value
        else:
            MockRedis.redis[key] = value


@as_future
def mock_redis_connection(*args, **kwargs):
    return MockRedis()
