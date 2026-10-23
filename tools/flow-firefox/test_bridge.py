"""Pruebas del límite de autorización y de entrega única, sin navegador ni Flow."""
import json
import threading
import unittest
import urllib.error
import urllib.request
import bridge

class BridgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = bridge.ThreadingHTTPServer(('127.0.0.1', 0), bridge.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        bridge.jobs.clear()
        bridge.last_seen = 0

    def call(self, path, data=None, token=bridge.TOKEN, origin=None):
        headers = {'Authorization':'Bearer '+token, 'Content-Type':'application/json'}
        if origin:
            headers['Origin'] = origin
        req = urllib.request.Request('http://127.0.0.1:'+str(self.server.server_port)+path,
            data=None if data is None else json.dumps(data).encode(), headers=headers)
        try:
            response = urllib.request.urlopen(req, timeout=3)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, json.load(response)

    def test_rejects_wrong_key(self):
        self.assertEqual(self.call('/next', token='wrong')[0], 401)

    def test_rejects_web_origin(self):
        self.assertEqual(self.call('/next', origin='https://example.com')[0], 403)

    def test_disconnected_does_not_queue(self):
        self.assertEqual(self.call('/command', {'op':'click','id':0})[0], 409)
        self.assertEqual(bridge.jobs, {})

    def test_no_jobs_on_connect(self):
        self.assertEqual(self.call('/next'), (200, {}))

    def test_delivers_only_once(self):
        self.call('/next')
        status, job = self.call('/command', {'op':'snapshot'})
        self.assertEqual(status, 200)
        self.assertEqual(self.call('/next')[1]['id'], job['id'])
        self.assertEqual(self.call('/next')[1], {})
        self.assertEqual(self.call('/command', {'op':'snapshot'})[0], 409)
        self.assertEqual(self.call('/result', {'id':job['id'],'result':'ok'})[0], 200)
        self.assertEqual(self.call('/result', {'id':job['id'],'result':'again'})[0], 409)

    def test_expires_undelivered_command(self):
        self.call('/next')
        ident = self.call('/command', {'op':'click','id':0})[1]['id']
        bridge.jobs[ident]['created'] -= 16
        self.assertEqual(self.call('/next')[1], {})
        self.assertEqual(bridge.jobs[ident]['state'], 'done')

    def test_rejects_arbitrary_code(self):
        self.call('/next')
        self.assertEqual(self.call('/command', {'op':'eval','code':'alert(1)'})[0], 400)

if __name__ == '__main__':
    unittest.main()
