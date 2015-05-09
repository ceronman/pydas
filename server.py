
from time import time
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty
from itertools import count
from json import dumps, loads


DART = '/opt/google/dartsdk/bin/dart'
DAS = '/opt/google/dartsdk/bin/snapshots/analysis_server.dart.snapshot'


class QueueEventLoop:
    def __init__(self):
        self.queue = Queue()

    def run_forever(self):
        self.running = True
        callbacks = []

        while self.running:
            try:
                item = self.queue.get(True, 0.01)
                callbacks.append(item)
            except Empty:
                pass

            new_callbacks = []
            for added_at, delay, callback, args in callbacks:
                if time() - added_at >= delay:
                    callback(*args)
                else:
                    new_callbacks.append((added_at, delay, callback, args))
            callbacks = new_callbacks

    def stop(self):
        self.running = False

    def call_soon_threadsafe(self, callback, *args):
        self.queue.put((time(), 0, callback, args))

    def call_later(self, delay, callback, *args):
        self.queue.put((time(), delay, callback, args))


class DASServer:
    def __init__(self, event_loop):
        self._event_loop = event_loop
        self._counter = count()
        self._request_callbacks = {}
        self._event_callbacks = {}

    def start(self):
        self._process = Popen([DART, DAS], stdin=PIPE, stdout=PIPE, bufsize=1)

        reader_thread = Thread(target=self._read_thread)
        # reader_thread.daemon = True
        reader_thread.start()

    def server_get_version(self, callback):
        self._request('server.getVersion', params=None, callback=callback)

    def server_shutdown(self, callback):
        self._request('server.shutdown', params=None, callback=callback)

    def on_server_connected(self, callback):
        self._on_event('server.connected', callback=callback)

    def on_server_error(self, callback):
        self._on_event('server.error', callback=callback)

    def _read_thread(self):
        for line in self._process.stdout:
            line = line.decode('utf-8')
            body = loads(line)
            if 'id' in body:
                method, callback = self._request_callbacks[body['id']]
                params = [method]
                if 'result' in body:
                    params.append(body['result'])
            elif 'event' in body:
                event, callback = self._event_callbacks[body['event']]
                assert event == body['event']
                params = (event, body['params'])
            else:
                raise

            self._event_loop.call_soon_threadsafe(callback, *params)

    def _next_id(self):
        return str(next(self._counter))

    def _request(self, method, params=None, callback=None):
        request_id = self._next_id()
        body = {
            'id': request_id,
            'clientRequestTime': int(time() * 1000),
            'method': method,
        }
        if params is not None:
            body['params'] = params

        self._request_callbacks[request_id] = (method, callback)

        self._process.stdin.write(dumps(body).encode('utf-8') + b'\n')
        self._process.stdin.flush()

    def _on_event(self, event, callback):
        self._event_callbacks[event] = (event, callback)


if __name__ == '__main__':
    loop = QueueEventLoop()
    das = DASServer(loop)

    def event(event, params):
        print('event:', event, 'data:', repr(params))

    def request(method, params):
        print('method:', method, 'data:', repr(params))

    def shutdown(method):
        print('good bye')
        loop.stop()

    das.on_server_connected(event)
    das.on_server_error(event)

    loop.call_later(2, lambda: das.server_get_version(request))
    loop.call_later(3, lambda: das.server_shutdown(shutdown))

    das.start()
    loop.run_forever()
