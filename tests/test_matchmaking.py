import unittest

from matchmaking import Preferences, compatibility_score, find_best_match


class MatchmakingTests(unittest.TestCase):
    def test_compatibility_score_bounds(self):
        pref = Preferences(age=30, intent='long-term', interests={'hiking', 'music'})
        candidate = {'age': 30, 'intent': 'long-term', 'interests': ['hiking', 'music']}
        score = compatibility_score(pref, candidate)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 99)

    def test_best_match_prefers_intent_and_interests(self):
        pref = Preferences(age=29, intent='long-term', interests={'travel', 'coffee'})
        candidates = [
            {'name': 'A', 'age': 29, 'intent': 'casual', 'interests': ['travel']},
            {'name': 'B', 'age': 31, 'intent': 'long-term', 'interests': ['travel', 'coffee']}
        ]
        best = find_best_match(pref, candidates)
        self.assertEqual(best['name'], 'B')


if __name__ == '__main__':
    unittest.main()
