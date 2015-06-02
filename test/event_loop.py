import time
import queue


class DummyEventLoop:
    def __init__(self):
        self._queue = queue.Queue()

    def run_forever(self):
        self._running = True
        callbacks = []

        while True:
            try:
                item = self._queue.get(True, 0.01)
                callbacks.append(item)
            except queue.Empty:
                if not self._running:
                    break

            new_callbacks = []
            for added_at, delay, callback, args, kwargs in callbacks:
                if time.time() - added_at >= delay:
                    callback(*args, **kwargs)
                else:
                    new_callbacks.append((added_at, delay, callback, args, kwargs))
            callbacks = new_callbacks

    def stop(self):
        self._running = False

    def call_soon_threadsafe(self, callback, *args, **kwargs):
        self._queue.put((time.time(), 0, callback, args, kwargs))

    def call_later(self, delay, callback, *args, **kwargs):
        self._queue.put((time.time(), delay, callback, args, kwargs))
