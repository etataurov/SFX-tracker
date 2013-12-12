from datetime import datetime, timedelta
import asyncio
from asyncio_redis import Connection
from .checker import Checker
from .config import *

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)


class Tracker:
    # TODO need tests
    # TODO transactions
    def __init__(self, url_timeout=60*60, timeout=10*60):
        self.connection_params = dict(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, poolsize=5)
        self.connection = None
        self.url_timeout = url_timeout
        self.timeout = timeout

    @asyncio.coroutine
    def add_task(self, url, email):
        log.info('new task added: {} {}'.format(url, email))
        self.connection = self.connection or (yield from Connection.create(**self.connection_params))

        # TODO check if url exists, maybe use sorted set

        yield from self.connection.hset(url, 'email', email)

        yield from self.connection.lpush('data', [url])

        yield from self.set_timeout(self.connection, url)

    @asyncio.coroutine
    def check_status(self):
        log.info('Checking status')
        self.connection = self.connection or (yield from Connection.create(**self.connection_params))
        url = yield from self.connection.lindex('data', 0)
        log.debug('get first from list: {}'.format(url))
        if url is not None:
            when = yield from self.connection.hget(url, 'when')
            if float(when) <= datetime.now().timestamp():
                log.debug('ready')
                yield from self.connection.lpop('data')
                email = yield from self.connection.hget(url, 'email')
                last_date = yield from self.connection.hget(url, 'last_date')
                log.info('started checking for {} {}'.format(url, email))

                try:
                    new_date = self.do_check(url, email, last_date)  # TODO do in thread
                except Exception as exc:
                    log.error(str(exc))
                else:
                    if new_date is not None:
                        yield from self.connection.hset(url, 'last_date', new_date)

                yield from self.connection.lpush('data', [url])
                yield from self.set_timeout(self.connection, url)
            else:
                log.debug('not ready yet {}'.format(datetime.fromtimestamp(float(when))))
        loop = asyncio.get_event_loop()
        loop.call_later(self.timeout, self.run)

    def do_check(self, url, email, last_event_date):
        checker = Checker(url, email, last_event_date)
        return checker.check_status()

    def set_timeout(self, connection, url):
        when = datetime.now() + timedelta(seconds=self.url_timeout)
        return connection.hset(url, 'when', str(when.timestamp()))

    def run(self):
        asyncio.Task(self.check_status())
