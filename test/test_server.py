import unittest
import os

from das.server import DASServer
from test.event_loop import DummyEventLoop


class DASServerTest(unittest.TestCase):

    def setUp(self):
        dart_sdk_path = os.environ['DART_SDK_PATH']
        dart_path = os.path.join(dart_sdk_path, 'bin', 'dart')
        das_path = os.path.join(dart_sdk_path, 'bin', 'snapshots',
                                'analysis_server.dart.snapshot')
        self.loop = DummyEventLoop()
        self.das = DASServer(dart_path, das_path, self.loop)

    def test_on_connected(self):

        def on_connected(event, data):
            self.assertEqual(event, 'server.connected')
            self.das._request('server.shutdown', None)
            self.loop.stop()

        self.das._on_event('server.connected', on_connected)
        self.das.start()

        self.loop.run_forever()
