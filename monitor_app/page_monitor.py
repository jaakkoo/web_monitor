__author__ = 'Jaakko Aro'

import requests
import time
import logging
import threading
from requests.exceptions import RequestException

logger = logging.getLogger('web_monitor')


def synchronous(lock):
    # Python recipe http://code.activestate.com/recipes/465057-basic-synchronization-decorator/
    def wrapper(func):
        def locker(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()
        return locker
    return wrapper


class MonitoredPage(object):
    _lock = threading.RLock()

    def __init__(self, name, url, max_response_time, should_contain):
        self.name = name
        self.url = url
        self.max_response_time = max_response_time
        self.should_contain = should_contain
        self.request_maker = RequestedPage()
        self._page = None

    @synchronous(_lock)
    def __str__(self):
        base = 'Status of [%s] ' % self.name
        if self._page:
            return base + 'Response time: %.2fs (%s) Contains required content: %s' % \
                   (self.get_response_time(), 'Passed' if self.responds_fast_enough() else 'FAILED!',
                    self.contains_required_string())
        else:
            return base + 'Does not respond to requests!'

    def __cmp__(self, other):
        if self.name > other.name:
            return 1
        elif self.name < other.name:
            return -1
        return 0

    @synchronous(_lock)
    def get_status(self):
        if not self._page:
            raise NoResponse('%s is not responding!' % self.name)
        return self._page and self.responds_fast_enough() and self.contains_required_string()

    @synchronous(_lock)
    def responds_fast_enough(self):
        return self.get_response_time() <= self.max_response_time

    @synchronous(_lock)
    def get_response_time(self):
        return self._page.response_time

    @synchronous(_lock)
    def contains_required_string(self):
        return self.should_contain in self._page.content

    @synchronous(_lock)
    def refresh_status(self):
        try:
            self._page = self.request_maker.http_request(self.url)
        except RequestException:
            self._page = None


class RequestedPage(object):
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.status_code = None
        self.content = None

    @property
    def response_time(self):
        return self.stop_time - self.start_time

    def http_request(self, url):
        try:
            self.start_time = time.time()
            r = requests.get(url)
            self.stop_time = time.time()
            self.content = r.content
            self.status_code = r.status_code
        except KeyboardInterrupt:
            print r
        except RequestException:
            raise
        return self


class NoResponse(Exception):
    pass
