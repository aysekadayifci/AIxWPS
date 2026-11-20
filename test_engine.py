"""Run with python -m unittest test_engine.py (no extra dependencies)."""
import unittest
from ai_wps_engine import Game, ROUNDS


class EngineTests(unittest.TestCase):
    def test_six_rounds_and_bounded_metrics(self):
        game = Game(seed=17)
        for _ in ROUNDS:
            game.start_round()
            game.decide(1)
        self.assertEqual(len(game.history), 6)
        self.assertTrue(all(0 <= value <= 100 for value in game.metrics.values()))
        self.assertTrue(all(0 <= value <= 100 for value in game.groups.values()))

    def test_deterministic_seed(self):
        def run():
            game = Game(seed=19)
            for _ in ROUNDS:
                game.start_round()
                game.decide(1)
            return game.metrics, game.groups, game.hidden_threat
        self.assertEqual(run(), run())

    def test_delayed_effect(self):
        game = Game()
        game.start_round()
        game.decide(0)  # creates round-3 delayed trust penalty
        game.start_round()
        game.decide(2)
        before = game.metrics['trust']
        game.start_round()
        self.assertEqual(game.metrics['trust'], max(0, before - 5))

    def test_reject_duplicate_decision(self):
        game = Game()
        game.start_round()
        game.decide(1)
        with self.assertRaises(RuntimeError):
            game.decide(1)

    def test_role_briefing_is_distinct(self):
        a = Game(role='women')
        b = Game(role='military')
        self.assertNotEqual(a.role_briefing(ROUNDS[0]), b.role_briefing(ROUNDS[0]))


if __name__ == '__main__':
    unittest.main()
