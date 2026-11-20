import unittest
from ai_wps_engine import Game, ACTORS

class RoleScenarios(unittest.TestCase):
    def test_all_roles_six_decisions(self):
        for role in ACTORS:
            with self.subTest(role=role):
                game=Game(role=role)
                for r in range(6):
                    game.start_round()
                    options=game.available_choices()
                    self.assertEqual(len(options),3)
                    self.assertTrue(all(title and context for title,context in options))
                    game.decide(r%3)
                    self.assertEqual(game.history[-1]['choice'],options[r%3][0])
                    self.assertEqual(game.history[-1]['role'],role)
                self.assertEqual(len(game.history),6)

    def test_role_choices_distinct(self):
        names=[]
        for role in ACTORS:
            game=Game(role=role);game.start_round()
            names.append(tuple(x[0] for x in game.available_choices()))
        self.assertEqual(len(set(names)),len(ACTORS))

    def test_adaptive_context_reflects_previous_choice(self):
        game=Game(role='community');game.start_round();chosen=game.available_choices()[1][0]
        game.decide(1);game.start_round()
        self.assertIn(chosen,game.adaptive_context())
        self.assertIn('Other actors responded',game.adaptive_context())

if __name__=='__main__': unittest.main()
