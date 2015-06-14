import unittest
import os

from das.api import DartAnalysisServer
from test.tools import DummyEventLoop, on_connected


class DASServerTest(unittest.TestCase):

    def setUp(self):
        dart_sdk_path = os.environ['DART_SDK_PATH']
        dart_path = os.path.join(dart_sdk_path, 'bin', 'dart')
        das_path = os.path.join(dart_sdk_path, 'bin', 'snapshots',
                                'analysis_server.dart.snapshot')
        self.loop = DummyEventLoop()
        self.das = DartAnalysisServer(dart_path, das_path, self.loop)

    def tearDown(self):
        self.das.stop()

    def _run_loop(self):
        def on_timeout():
            self.loop.stop()
            self.das.stop()
            self.fail('Test timeout')
        self.loop.call_later(2, on_timeout)

        try:
            self.loop.run_forever()
        except Exception as e:
            self.fail('Error during callback: {}'.format(e))

    def test_on_connected(self):

        def on_connected(event, version):
            self.assertEqual(event, 'server.connected')
            self.loop.stop()

        self.das.notification('server.connected', callback=on_connected)
        self.das.start()

        self._run_loop()

    def test_on_callback_error(self):

        def on_connected(event, version):
            raise RuntimeError('runtime error')

        self.das.notification('server.connected', callback=on_connected)
        self.das.start()

        try:
            self.loop.run_forever()
        except Exception as e:
            self.assertEqual(str(e), 'runtime error')
        self.das.stop()

    @on_connected
    def test_on_get_version(self):
        def on_version(method, version):
            self.assertEqual(method, 'server.getVersion')
            self.assertTrue(version.startswith('1.7'))
            self.loop.stop()

        self.das.request('server.getVersion', callback=on_version)

    @on_connected
    def test_request_error(self):
        def on_success(method):
            self.fail('method should fail')
            self.das.request('server.shutdown')
            self.loop.stop()

        def on_error(method, error):
            self.assertEqual(error.code, 'INVALID_PARAMETER')
            self.loop.stop()

        self.das.request('server.setSubscriptions',
                         callback=on_success, errback=on_error)

    @on_connected
    def test_generated_method(self):
        def on_version(method, version):
            self.assertEqual(method, 'server.getVersion')
            self.assertTrue(version.startswith('1.7'))
            self.loop.stop()

        self.das.server.get_version(callback=on_version)
