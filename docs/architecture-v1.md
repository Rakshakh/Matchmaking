# Matchmaking Architecture v1

## 1) Chosen stack

### Frontend
- **Framework:** React + TypeScript (Vite)
- **State/data:** TanStack Query for server state, local component state for UI
- **UI approach:** Feature-first views (`onboarding`, `recommendations`, `chat`) aligned to the product funnel

### Backend
- **Framework:** Python FastAPI
- **Module layout:**
  - `api/` for HTTP surface
  - `matching/` for candidate ranking logic
  - `messaging/` for chat/session logic

### Database
- **Primary DB:** PostgreSQL
- **Rationale:** strong relational modeling for profiles, interactions, and auditability; JSONB for flexible preference payloads

### Auth
- **Approach:** JWT-based auth with external identity provider (e.g., Auth0/Clerk/Supabase Auth)
- **Boundary:** frontend obtains access token; backend validates JWT and derives `user_id` from claims

---

## 2) API boundaries and endpoint conventions

## Service boundaries
- **Client-facing API (`backend/api`)**
  - Owns request validation, auth context, and response shaping.
  - Calls matching and messaging modules as internal domain services.
- **Matching module (`backend/matching`)**
  - Pure domain logic for ranking candidates.
  - No direct web concerns.
- **Messaging module (`backend/messaging`)**
  - Owns conversation threads, message writes, and read models.

## Endpoint conventions
- Base path: `/api/v1`
- Resource naming: plural nouns, kebab-case where needed (`/recommendations`, `/chat-threads`)
- JSON only
- Idempotency:
  - `GET` for reads
  - `POST` for commands/creation
  - `PATCH` for partial updates
- Standard envelope for errors:

```json
{
  "error": {
    "code": "string_code",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Initial vertical-slice endpoints
- `POST /api/v1/profiles/me/onboarding`
  - Save or update onboarding profile + preferences.
- `GET /api/v1/recommendations`
  - Return ranked candidates for authenticated user.
- `POST /api/v1/chat-threads`
  - Create (or fetch existing) chat thread between matched users.
- `GET /api/v1/chat-threads/{thread_id}/messages`
  - Fetch thread messages.
- `POST /api/v1/chat-threads/{thread_id}/messages`
  - Send message.

---

## 3) Matching service contract

## Contract

`input profile + preferences -> ranked candidates`

### Input model (service-level)
```json
{
  "request_user": {
    "user_id": "uuid",
    "profile": {
      "age": 29,
      "location": "NYC",
      "interests": ["running", "coffee", "tech"],
      "intent": "long_term"
    }
  },
  "preferences": {
    "age_range": [26, 34],
    "distance_km": 25,
    "required_interests": ["coffee"],
    "dealbreakers": ["smoking"],
    "intent": "long_term"
  },
  "context": {
    "exclude_user_ids": ["uuid-1", "uuid-2"],
    "limit": 20
  }
}
```

### Output model
```json
{
  "candidates": [
    {
      "user_id": "uuid",
      "score": 0.91,
      "reasons": ["shared_interest:coffee", "intent_match", "distance_close"]
    }
  ],
  "metadata": {
    "model_version": "v1",
    "generated_at": "2026-01-01T00:00:00Z"
  }
}
```

### Rules
- Filter first (hard constraints), rank second (soft signals).
- Deterministic tie-breaker (`score DESC`, then `candidate_user_id ASC`).
- Log score components for explainability and offline evaluation.

---

## 4) Data storage approach

## Compatibility signals
Store decomposed and aggregate signals:

- `compatibility_features`
  - `(viewer_user_id, candidate_user_id, feature_name, feature_value, computed_at)`
  - Examples: `interest_overlap_count`, `distance_km`, `intent_match`.
- `compatibility_scores`
  - `(viewer_user_id, candidate_user_id, total_score, score_breakdown_json, model_version, computed_at)`

This enables:
- fast recommendation reads from precomputed score tables,
- transparent score breakdowns,
- model iteration with versioned records.

## Interaction history
Event-sourced interaction log:

- `interaction_events`
  - `(event_id, actor_user_id, target_user_id, event_type, event_payload_json, created_at)`
  - Event types: `profile_view`, `like`, `pass`, `match_created`, `message_sent`.

Derived read models/materialized views:
- `user_interaction_state`
  - last action per pair to enforce exclusion rules and ranking freshness.
- `thread_message_counts` / `recent_activity`
  - support chat/recommendation UI latency targets.

## End-to-end v1 path (prioritized)
1. User completes onboarding profile/preferences.
2. Backend persists profile/preferences and triggers score computation.
3. Recommendations endpoint returns ranked candidates.
4. User opens chat with a matched candidate and sends a first message.

All scaffolding below optimizes this path first; secondary domains are deferred.
