"""Core matchmaking logic used by the API and tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Preferences:
    age: int
    intent: str
    interests: set[str]


def _age_score(preferred_age: int, candidate_age: int) -> float:
    gap = abs(preferred_age - candidate_age)
    return max(0.0, 1.0 - (gap / 20.0))


def _intent_score(preferred_intent: str, candidate_intent: str) -> float:
    return 1.0 if preferred_intent == candidate_intent else 0.25


def _interest_score(preferred_interests: set[str], candidate_interests: Iterable[str]) -> float:
    if not preferred_interests:
        return 0.5
    candidate_set = set(candidate_interests)
    overlap = preferred_interests.intersection(candidate_set)
    return len(overlap) / len(preferred_interests)


def compatibility_score(preferences: Preferences, candidate: dict) -> int:
    age = _age_score(preferences.age, int(candidate["age"]))
    intent = _intent_score(preferences.intent, str(candidate["intent"]))
    interests = _interest_score(preferences.interests, candidate["interests"])

    raw = (age * 0.35) + (intent * 0.30) + (interests * 0.35)
    return max(0, min(99, round(raw * 100)))


def find_best_match(preferences: Preferences, candidates: list[dict]) -> dict:
    ranked = sorted(
        (
            {
                **candidate,
                "score": compatibility_score(preferences, candidate),
            }
            for candidate in candidates
        ),
        key=lambda candidate: candidate["score"],
        reverse=True,
    )
    return ranked[0]
