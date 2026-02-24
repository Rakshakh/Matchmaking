import unittest

from matchmaking import MatchmakingService


class MatchmakingFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = MatchmakingService()

    def _seed_user(self, email: str, gender: str, interested_in: list[str], location: str, interests: list[str], age: int, lifestyle_score: float, password: str = "pw") -> int:
        user_id = self.service.sign_up(email=email, password=password)
        self.service.login(email=email, password=password)
        self.service.create_profile(
            user_id,
            {
                "age": age,
                "gender": gender,
                "interested_in": interested_in,
                "location": location,
                "interests": interests,
                "lifestyle_score": lifestyle_score,
            },
        )
        return user_id

    def test_end_to_end_path(self) -> None:
        alex = self._seed_user(
            "alex@example.com", "man", ["woman"], "NYC", ["hiking", "coffee", "books"], 30, 7
        )
        sam = self._seed_user(
            "sam@example.com", "woman", ["man"], "NYC", ["coffee", "travel", "books"], 29, 6
        )
        taylor = self._seed_user(
            "taylor@example.com", "woman", ["man"], "SF", ["gaming", "music"], 30, 3
        )

        recs = self.service.get_recommendations(alex)
        recommended_ids = [item["user_id"] for item in recs]
        self.assertEqual(recommended_ids[0], sam)

        self.service.pass_user(alex, taylor)
        matched_after_alex_like = self.service.like_user(alex, sam)
        self.assertFalse(matched_after_alex_like)
        matched_after_sam_like = self.service.like_user(sam, alex)
        self.assertTrue(matched_after_sam_like)

        self.assertEqual(self.service.get_matches(alex), [sam])
        self.assertEqual(self.service.get_matches(sam), [alex])

        self.service.send_message(alex, sam, "Hi Sam!")
        self.service.send_message(sam, alex, "Hi Alex!")
        history = self.service.get_chat_history(alex, sam)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["text"], "Hi Sam!")

        event_names = [event.name for event in self.service.get_events()]
        for required in [
            "user_signed_up",
            "user_logged_in",
            "profile_created",
            "recommendations_requested",
            "interaction_recorded",
            "match_created",
            "chat_message_sent",
            "chat_history_viewed",
        ]:
            self.assertIn(required, event_names)

    def test_chat_requires_match(self) -> None:
        a = self._seed_user("a@example.com", "man", ["woman"], "NYC", ["a"], 20, 1)
        b = self._seed_user("b@example.com", "woman", ["man"], "NYC", ["a"], 20, 1)

        with self.assertRaises(ValueError):
            self.service.send_message(a, b, "hello")

    def test_recommendations_return_profile_snapshots(self) -> None:
        alex = self._seed_user("alex@example.com", "man", ["woman"], "NYC", ["hiking"], 30, 7)
        sam = self._seed_user("sam@example.com", "woman", ["man"], "NYC", ["coffee"], 29, 6)

        recommendations = self.service.get_recommendations(alex)
        recommendations[0]["profile"]["location"] = "LA"
        recommendations[0]["profile"]["interests"].append("mutated")

        self.assertEqual(self.service._profiles[sam]["location"], "NYC")
        self.assertEqual(self.service._profiles[sam]["interests"], ["coffee"])

    def test_chat_apis_return_message_snapshots(self) -> None:
        alex = self._seed_user("alex@example.com", "man", ["woman"], "NYC", ["hiking"], 30, 7)
        sam = self._seed_user("sam@example.com", "woman", ["man"], "NYC", ["coffee"], 29, 6)
        self.service.like_user(alex, sam)
        self.service.like_user(sam, alex)

        sent = self.service.send_message(alex, sam, "Hi Sam!")
        sent["text"] = "tampered"

        history = self.service.get_chat_history(alex, sam)
        history[0]["text"] = "changed"

        self.assertEqual(self.service._chat_messages[self.service._chat_key(alex, sam)][0]["text"], "Hi Sam!")



if __name__ == "__main__":
    unittest.main()
