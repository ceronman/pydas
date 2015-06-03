import unittest
import os

from das.server import DartAnalysisServer
from test.event_loop import DummyEventLoop


class DASServerTest(unittest.TestCase):

    def setUp(self):
        dart_sdk_path = os.environ['DART_SDK_PATH']
        dart_path = os.path.join(dart_sdk_path, 'bin', 'dart')
        das_path = os.path.join(dart_sdk_path, 'bin', 'snapshots',
                                'analysis_server.dart.snapshot')
        self.loop = DummyEventLoop()
        self.das = DartAnalysisServer(dart_path, das_path, self.loop)

        def on_timeout():
            self.das.stop()
            self.loop.stop()
            self.fail('Test timeout')

        self.loop.call_later(1, on_timeout)

    def test_on_connected(self):

        def on_connected(event, version):
            self.assertEqual(event, 'server.connected')
            self.das.request('server.shutdown', None)
            self.loop.stop()

        self.das.notification('server.connected', callback=on_connected)
        self.das.start()

        self.loop.run_forever()
        self.das.stop()

    def test_on_get_version(self):

        def on_version(method, version):
            self.assertEqual(method, 'server.getVersion')
            self.assertEqual(version, '1.6.0')
            self.das.request('server.shutdown')
            self.loop.stop()

        def on_connected(event, version):
            self.das.request('server.getVersion', callback=on_version)

        self.das.notification('server.connected', callback=on_connected)
        self.das.start()

        self.loop.run_forever()
        self.das.stop()

    def test_request_error(self):

        def on_success(method):
            self.fail('method should fail')
            self.das.request('server.shutdown')
            self.loop.stop()

        def on_error(method, error):
            self.assertEqual(error.code, 'INVALID_PARAMETER')
            self.das.request('server.shutdown')
            self.loop.stop()

        def on_connected(event, version):
            self.das.request('server.setSubscriptions',
                             callback=on_success, errback=on_error)

        self.das.notification('server.connected', callback=on_connected)
        self.das.start()

        self.loop.run_forever()
        self.das.stop()
