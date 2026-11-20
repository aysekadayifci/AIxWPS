import unittest, io, json, os
from unittest.mock import patch
from ai_wps_engine import Game
from ai_advisor import public_context, ask
class AdvisorTests(unittest.TestCase):
    def test_context(self):
        g=Game();g.start_round();c=public_context(g)
        self.assertNotIn('hidden_threat',c);self.assertNotIn('pending',c)
        self.assertEqual(len(c['options']),3)
        json.dumps(c)
    def test_request(self):
        def mock(req,timeout):
            p=json.loads(req.data);self.assertFalse(p['store']);self.assertEqual(p['model'],'test-model')
            return io.BytesIO(b'{"choices":[{"message":{"content":"Test analysis"}}]}')
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-key'}):
            self.assertEqual(ask({},'test',model='test-model',opener=mock),'Test analysis')
