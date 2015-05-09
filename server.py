from time import sleep, time
from random import random
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue
from itertools import count
from json import dumps


DART = '/opt/google/dartsdk/bin/dart'
DAS = '/opt/google/dartsdk/bin/snapshots/analysis_server.dart.snapshot'


class DASServer:

    def __init__(self):
        self._counter = count()
        self._input_queue = Queue()
        self._output_queue = Queue()
        self._requests = {}

        self._process = Popen([DART, DAS], stdin=PIPE, stdout=PIPE, bufsize=1)

        reader_thread = Thread(target=self._read_thread)
        reader_thread.daemon = True
        reader_thread.start()

    def server_get_version(self):
        self._request('server.getVersion')

    def _read_thread(self):
        while True:
            line = self._process.stdout.readline()
            self._output_queue.put(line)
            print(line)

    def _next_id(self):
        return str(next(self._counter))

    def _request(self, method, args=None):
        request_id = self._next_id()
        body = {
            'id': request_id,
            'clientRequestTime': int(time() * 1000),
            'method': method,
        }
        if args is not None:
            body['args'] = args

        self._process.stdin.write(dumps(body).encode('utf-8') + b'\n')
        self._process.stdin.flush()


if __name__ == '__main__':
    das = DASServer()

    sleep(1)

    def test_write():
        for i in range(10):
            das.server_get_version()
            sleep(random())

        sleep(1)
        print('write done')

    t1 = Thread(target=test_write)
    t1.start()
    t1.join()
