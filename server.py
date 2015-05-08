from time import sleep
from random import random
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue, Empty


def main():
    DART = '/opt/google/dartsdk/bin/dart'
    DAS = '/opt/google/dartsdk/bin/snapshots/analysis_server.dart.snapshot'

    input_queue = Queue()
    output_queue = Queue()

    def write_thread(pipe, queue):
        while True:
            line = queue.get()
            pipe.write(line)
            pipe.flush()

    def read_thread(pipe, queue):
        while True:
            line = pipe.readline()
            queue.put(line)

    process = Popen([DART, DAS], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    reader_thread = Thread(target=read_thread,
                           args=(process.stdout, output_queue))
    reader_thread.daemon = True
    reader_thread.start()

    writer_thread = Thread(target=write_thread,
                           args=(process.stdin, input_queue))
    writer_thread.daemon = True
    writer_thread.start()

    def test_read():
        while True:
            try:
                value = output_queue.get(True, 0.1)
                print(value)
            except Empty:
                print('Empty')

    t2 = Thread(target=test_read)
    t2.daemon = True
    t2.start()

    def test_write():
        for i in range(10):
            input_queue.put(b'\n')
            sleep(random() * 5)

    t1 = Thread(target=test_write)
    t1.start()
    t1.join()


if __name__ == '__main__':
    main()
