
import itertools
import json
import time
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread


DART = '/opt/google/dartsdk/bin/darts'
DAS = '/opt/google/dartsdk/bin/snapshots/analysis_server.dart.snapshot'


class DartAnalysisException(Exception):
    pass


class RequestError(Exception):
    def __init__(self, raw_error):
        self.code = raw_error['code']
        self.message = raw_error['message']
        self.stacktrace = raw_error.get('stackTrace', None)


class DartAnalysisServer:
    _domains = {}

    def __init__(self, dart_path, das_path, event_loop):
        self._path = [dart_path, das_path]
        self._event_loop = event_loop
        self._id_counter = itertools.count()
        self._request_callbacks = {}
        self._event_callbacks = {}

        for name, domain_class in self._domains.items():
            domain = domain_class()
            domain.server = self
            setattr(self, name, domain)

    def start(self):
        self._process = Popen(self._path, stdin=PIPE, stdout=PIPE, bufsize=1)

        reader_thread = Thread(target=self._read_thread)
        reader_thread.start()

    def stop(self, timeout=0):
        self._process.stdin.close()
        self._process.stdout.close()
        try:
            self._process.wait(timeout=timeout)
        except TimeoutExpired:
            self._process.kill()

    def _read_thread(self):
        while True:
            try:
                line = self._process.stdout.readline().decode('utf-8')
            except ValueError:
                break
            if not line:
                break
            body = json.loads(line)
            if 'id' in body:
                self._send_request(body)
            elif 'event' in body:
                self._send_event(body)
            else:
                raise DartAnalysisException('Unknown message: ' + line)

    def _send_request(self, body):
        if self._process is None:
            raise DartAnalysisException('Server not started')

        try:
            method, callback, errback = self._request_callbacks[body['id']]
        except KeyError:
            raise DartAnalysisException('Response without an ID')

        if 'error' in body and errback is not None:
            self._event_loop.call_soon_threadsafe(errback, method,
                                                  RequestError(body['error']))
        elif callback is not None:
            kwargs = body.get('result', {})
            self._event_loop.call_soon_threadsafe(callback, method, **kwargs)

    def _send_event(self, body):
        if self._process is None:
            raise DartAnalysisException('Server not started')

        try:
            event, callback = self._event_callbacks[body['event']]
        except KeyError:
            return
        params = (event, body['params'])
        self._event_loop.call_soon_threadsafe(callback, *params)

    def _next_id(self):
        return str(next(self._id_counter))

    def request(self, method, params=None, *, callback=None, errback=None):
        request_id = self._next_id()
        body = {
            'id': request_id,
            'clientRequestTime': int(time.time() * 1000),
            'method': method,
        }
        if params is not None:
            body['params'] = params

        self._request_callbacks[request_id] = (method, callback, errback)

        self._process.stdin.write(json.dumps(body).encode('utf-8') + b'\n')
        self._process.stdin.flush()

    def notification(self, event, *, callback):
        self._event_callbacks[event] = (event, callback)

    @classmethod
    def register_domain(cls, name):

        def decorator(domain):
            cls._domains[name] = domain

        return decorator

    def check_version(self, version):
        if isinstance(version, str):
            version = [int(p) for p in version.strip().split('.')]

        that_major, that_minor, that_patch = version
        this_major, this_minor, this_patch = self.api_version
        return (that_major == this_major and that_minor >= this_minor)
