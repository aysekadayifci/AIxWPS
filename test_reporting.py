import tempfile
import unittest
from pathlib import Path
from ai_wps_engine import Game, ROUNDS
from reporting import export_report

class ReportingTests(unittest.TestCase):
    def test_report_outputs_and_six_rounds(self):
        game=Game(seed=17)
        for i in range(len(ROUNDS)):
            game.start_round()
            game.decide([1,1,1,1,2,1][i])
        with tempfile.TemporaryDirectory() as tmp:
            html_path,csv_path,json_path=export_report(game,tmp)
            for path in (html_path,csv_path,json_path):
                self.assertTrue(Path(path).exists())
            page=html_path.read_text(encoding='utf-8')
            self.assertIn('WPS pillar analysis',page)
            self.assertIn('<svg',page)
            self.assertIn('Full causal audit',page)
            self.assertIn('Round 6:',page)
    def test_incomplete_game_cannot_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                export_report(Game(),tmp)

if __name__=='__main__': unittest.main()
