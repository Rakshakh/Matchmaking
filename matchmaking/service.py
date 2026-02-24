from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple


REQUIRED_PROFILE_FIELDS = {
    "age",
    "gender",
    "interested_in",
    "location",
    "interests",
    "lifestyle_score",
}


@dataclass
class InstrumentationEvent:
    name: str
    user_id: int | None
    metadata: Dict[str, object]
    timestamp: str


class MatchmakingService:
    """Thin in-memory matchmaking implementation for v1 flows."""

    def __init__(self) -> None:
        self._next_user_id = 1
        self._users: Dict[int, Dict[str, object]] = {}
        self._users_by_email: Dict[str, int] = {}
        self._profiles: Dict[int, Dict[str, object]] = {}
        self._likes: Set[Tuple[int, int]] = set()
        self._passes: Set[Tuple[int, int]] = set()
        self._matches: Set[frozenset[int]] = set()
        self._chat_messages: Dict[Tuple[int, int], List[Dict[str, object]]] = {}
        self._events: List[InstrumentationEvent] = []

    # -------- instrumentation --------
    def _record_event(self, name: str, user_id: int | None, **metadata: object) -> None:
        self._events.append(
            InstrumentationEvent(
                name=name,
                user_id=user_id,
                metadata=metadata,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )

    def get_events(self) -> List[InstrumentationEvent]:
        return list(self._events)

    # -------- auth --------
    def sign_up(self, email: str, password: str) -> int:
        if email in self._users_by_email:
            raise ValueError("email already registered")
        user_id = self._next_user_id
        self._next_user_id += 1

        self._users[user_id] = {"id": user_id, "email": email, "password": password}
        self._users_by_email[email] = user_id
        self._record_event("user_signed_up", user_id, email=email)
        return user_id

    def login(self, email: str, password: str) -> int:
        user_id = self._users_by_email.get(email)
        if not user_id:
            raise ValueError("invalid credentials")
        user = self._users[user_id]
        if user["password"] != password:
            raise ValueError("invalid credentials")
        self._record_event("user_logged_in", user_id, email=email)
        return user_id

    # -------- profile --------
    def create_profile(self, user_id: int, profile: Dict[str, object]) -> None:
        self._assert_user_exists(user_id)
        missing_fields = REQUIRED_PROFILE_FIELDS - set(profile.keys())
        if missing_fields:
            raise ValueError(f"missing required fields: {sorted(missing_fields)}")
        if not isinstance(profile["interested_in"], list) or not profile["interested_in"]:
            raise ValueError("interested_in must be a non-empty list")
        if not isinstance(profile["interests"], list) or not profile["interests"]:
            raise ValueError("interests must be a non-empty list")

        self._profiles[user_id] = dict(profile)
        self._record_event("profile_created", user_id)

    # -------- recommendation --------
    def get_recommendations(self, user_id: int, limit: int = 10) -> List[Dict[str, object]]:
        source_profile = self._profiles.get(user_id)
        if not source_profile:
            raise ValueError("profile not found")

        seen_users = {
            target for actor, target in self._likes.union(self._passes) if actor == user_id
        }
        candidates = []
        for candidate_id, candidate_profile in self._profiles.items():
            if candidate_id == user_id or candidate_id in seen_users:
                continue
            if not self._is_mutually_interested(source_profile, candidate_profile):
                continue
            score = self._compatibility_score(source_profile, candidate_profile)
            candidates.append(
                {
                    "user_id": candidate_id,
                    "score": round(score, 4),
                    "profile": candidate_profile,
                }
            )

        candidates.sort(key=lambda item: item["score"], reverse=True)
        output = candidates[:limit]
        self._record_event(
            "recommendations_requested",
            user_id,
            requested_limit=limit,
            returned=len(output),
        )
        return output

    # -------- interaction --------
    def like_user(self, actor_id: int, target_id: int) -> bool:
        self._assert_profile_exists(actor_id)
        self._assert_profile_exists(target_id)
        if actor_id == target_id:
            raise ValueError("cannot like yourself")

        self._likes.add((actor_id, target_id))
        self._record_event("interaction_recorded", actor_id, interaction="like", target_id=target_id)

        is_mutual = (target_id, actor_id) in self._likes
        if is_mutual:
            match_key = frozenset({actor_id, target_id})
            if match_key not in self._matches:
                self._matches.add(match_key)
                chat_key = self._chat_key(actor_id, target_id)
                self._chat_messages.setdefault(chat_key, [])
                self._record_event("match_created", actor_id, with_user=target_id)
            return True
        return False

    def pass_user(self, actor_id: int, target_id: int) -> None:
        self._assert_profile_exists(actor_id)
        self._assert_profile_exists(target_id)
        if actor_id == target_id:
            raise ValueError("cannot pass yourself")
        self._passes.add((actor_id, target_id))
        self._record_event("interaction_recorded", actor_id, interaction="pass", target_id=target_id)

    def get_matches(self, user_id: int) -> List[int]:
        self._assert_user_exists(user_id)
        matches = []
        for pair in self._matches:
            if user_id in pair:
                matches.extend(candidate for candidate in pair if candidate != user_id)
        return sorted(matches)

    # -------- chat --------
    def send_message(self, sender_id: int, receiver_id: int, text: str) -> Dict[str, object]:
        if not text.strip():
            raise ValueError("message text cannot be empty")
        if not self._are_matched(sender_id, receiver_id):
            raise ValueError("users are not matched")

        message = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._chat_messages[self._chat_key(sender_id, receiver_id)].append(message)
        self._record_event("chat_message_sent", sender_id, receiver_id=receiver_id)
        return message

    def get_chat_history(self, user_a: int, user_b: int) -> List[Dict[str, object]]:
        if not self._are_matched(user_a, user_b):
            raise ValueError("users are not matched")
        self._record_event("chat_history_viewed", user_a, with_user=user_b)
        return list(self._chat_messages[self._chat_key(user_a, user_b)])

    # -------- internals --------
    def _assert_user_exists(self, user_id: int) -> None:
        if user_id not in self._users:
            raise ValueError("user not found")

    def _assert_profile_exists(self, user_id: int) -> None:
        self._assert_user_exists(user_id)
        if user_id not in self._profiles:
            raise ValueError("profile not found")

    @staticmethod
    def _chat_key(user_a: int, user_b: int) -> Tuple[int, int]:
        return (min(user_a, user_b), max(user_a, user_b))

    def _are_matched(self, user_a: int, user_b: int) -> bool:
        return frozenset({user_a, user_b}) in self._matches

    @staticmethod
    def _is_mutually_interested(source: Dict[str, object], candidate: Dict[str, object]) -> bool:
        return (
            candidate["gender"] in source["interested_in"]
            and source["gender"] in candidate["interested_in"]
        )

    @staticmethod
    def _compatibility_score(source: Dict[str, object], candidate: Dict[str, object]) -> float:
        source_interests = set(source["interests"])
        candidate_interests = set(candidate["interests"])
        overlap = len(source_interests.intersection(candidate_interests))
        total = max(len(source_interests.union(candidate_interests)), 1)

        age_distance = abs(int(source["age"]) - int(candidate["age"]))
        age_score = max(0.0, 1 - min(age_distance, 20) / 20)

        location_score = 1.0 if source["location"] == candidate["location"] else 0.2

        lifestyle_distance = abs(float(source["lifestyle_score"]) - float(candidate["lifestyle_score"]))
        lifestyle_score = max(0.0, 1 - min(lifestyle_distance, 10) / 10)

        interests_score = overlap / total
        return (0.45 * interests_score) + (0.2 * age_score) + (0.2 * location_score) + (0.15 * lifestyle_score)
