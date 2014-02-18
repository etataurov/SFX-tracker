from unittest.mock import patch
from .mocked_redis import mock_redis_connection, MockRedis
from sfxtracker.tracker import Tracker
import asyncio


@patch('asyncio_redis.Connection.create', mock_redis_connection)
def test_tracker_add_task():
    url = 'http://example.com'
    email = 'me@example.com'
    tr = Tracker()
    loop = asyncio.get_event_loop()
    task = asyncio.Task(tr.add_task(url, email))
    loop.run_until_complete(task)
    assert MockRedis.redis['data'][0] == url
    assert MockRedis.redis[url]['email'] == email


@patch('asyncio_redis.Connection.create', mock_redis_connection)
def test_tracker_add_two_tasks():
    url1 = 'http://example.com/1'
    email1 = 'me1@example.com'
    url2 = 'http://example.com/2'
    email2 = 'me2@example.com'
    tr = Tracker()
    loop = asyncio.get_event_loop()
    task = asyncio.Task(tr.add_task(url1, email1))
    loop.run_until_complete(task)
    task = asyncio.Task(tr.add_task(url2, email2))
    loop.run_until_complete(task)

    assert MockRedis.redis['data'] == [url2, url1]
    assert MockRedis.redis[url1]['email'] == email1
    assert MockRedis.redis[url2]['email'] == email2


@patch('asyncio_redis.Connection.create', mock_redis_connection)
def test_tracker_add_second_email():
    url = 'http://example.com/1'
    email1 = 'me1@example.com'
    email2 = 'me2@example.com'
    tr = Tracker()
    loop = asyncio.get_event_loop()
    task = asyncio.Task(tr.add_task(url, email1))
    loop.run_until_complete(task)
    task = asyncio.Task(tr.add_task(url, email2))
    loop.run_until_complete(task)

    assert MockRedis.redis['data'] == [url]
    assert MockRedis.redis[url]['email'] == ','.join([email1, email2])


@patch('asyncio_redis.Connection.create', mock_redis_connection)
@patch('sfxtracker.tracker.Tracker.do_check', lambda *args, **kwargs: None)
def test_tracker_check_status():
    url = 'http://example.com'
    email = 'me@example.com'
    tr = Tracker()
    loop = asyncio.get_event_loop()
    task = asyncio.Task(tr.add_task(url, email))
    loop.run_until_complete(task)
    task = asyncio.Task(tr.check_status())
    loop.run_until_complete(task)
    assert isinstance(MockRedis.redis[url]['when'], str)


def teardown_function(function):
    MockRedis._reinit()
