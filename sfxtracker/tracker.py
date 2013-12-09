from datetime import datetime, timedelta
import asyncio
from asyncio_redis import Connection
from .checker import Checker
from .config import *


class Tracker:
    # TODO need tests
    # TODO logging
    # TODO transactions
    def __init__(self, url_timeout=60*60, timeout=10*60):
        self.connection_params = dict(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, poolsize=5)
        self.connection = None
        self.url_timeout = url_timeout
        self.timeout = timeout

    @asyncio.coroutine
    def add_task(self, url, email):
        connection = self.connection or (yield from Connection.create(**self.connection_params))

        yield from connection.hset(url, 'email', email)

        yield from connection.lpush('data', [url])

        yield from self.set_timeout(connection, url)

    @asyncio.coroutine
    def check_status(self):
        connection = self.connection or (yield from Connection.create(**self.connection_params))
        url = yield from connection.lindex('data', 0)
        if url is not None:
            when = yield from connection.hget(url, 'when')
            if float(when) <= datetime.now().timestamp():
                yield from connection.lpop('data')
                email = yield from connection.hget(url, 'email')
                self.do_check(url, email)  # TODO do in thread
                yield from connection.lpush('data', [url])
                yield from self.set_timeout(connection, url)
            else:
                return
        loop = asyncio.get_event_loop()
        loop.call_later(self.timeout, self.run)

    def do_check(self, url, email):
        checker = Checker(url, email)
        checker.start()

    def set_timeout(self, connection, url):
        when = datetime.now() + timedelta(seconds=self.url_timeout)
        return connection.hset(url, 'when', str(when.timestamp()))

    def run(self):
        asyncio.Task(self.check_status())
