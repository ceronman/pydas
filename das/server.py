
from time import time
from subprocess import Popen, PIPE
from threading import Thread
from itertools import count
from json import dumps, loads


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
    def __init__(self, dart_path, das_path, event_loop):
        self._path = [dart_path, das_path]
        self._event_loop = event_loop
        self._counter = count()
        self._request_callbacks = {}
        self._event_callbacks = {}

    def start(self):
        self._process = Popen(self._path, stdin=PIPE, stdout=PIPE, bufsize=1)

        reader_thread = Thread(target=self._read_thread)
        reader_thread.start()

    def stop(self):
        self._process.terminate()

    def _read_thread(self):
        for line in self._process.stdout:
            line = line.decode('utf-8')
            body = loads(line)
            if 'id' in body:
                self._send_request(body)
            elif 'event' in body:
                self._send_event(body)
            else:
                raise DartAnalysisException('Unrecognizable line: ' + line)

    def _send_request(self, body):
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
        try:
            event, callback = self._event_callbacks[body['event']]
        except KeyError:
            return
        params = (event, body['params'])
        self._event_loop.call_soon_threadsafe(callback, *params)

    def _next_id(self):
        return str(next(self._counter))

    def request(self, method, params=None, callback=None, errback=None):
        request_id = self._next_id()
        body = {
            'id': request_id,
            'clientRequestTime': int(time() * 1000),
            'method': method,
        }
        if params is not None:
            body['params'] = params

        self._request_callbacks[request_id] = (method, callback, errback)

        self._process.stdin.write(dumps(body).encode('utf-8') + b'\n')
        self._process.stdin.flush()

    def notification(self, event, callback):
        self._event_callbacks[event] = (event, callback)
