# Matchmaking Domain Model

This document defines the core entities, validation rules, lifecycle transitions, and privacy boundaries for a matchmaking platform.

## Entities

### 1) User

#### Required fields and validation rules
- `user_id` (UUID, required, immutable).
- `email` (required, unique, normalized lowercase, RFC-compliant format).
- `phone_number` (optional unless required by region policy, E.164 format).
- `auth_provider` (required, enum: `password`, `google`, `apple`, `phone_otp`).
- `password_hash` (required only when `auth_provider=password`, never plaintext).
- `status` (required, enum: `pending_verification`, `active`, `suspended`, `deleted`).
- `date_of_birth` (required, must satisfy minimum age policy, e.g., 18+).
- `created_at`, `updated_at` (required timestamps).

#### State transitions
- `pending_verification -> active` after successful email/phone verification and policy acceptance.
- `active -> suspended` when moderation action is applied.
- `suspended -> active` after successful appeal/review.
- `active|suspended -> deleted` on user deletion request or compliance purge.
- `deleted` is terminal (no reactivation; only new account creation).

#### Privacy constraints
- Email, phone number, and auth metadata are never visible to other users.
- Only trust-and-safety and authorized support roles may view account-level compliance data.
- Other users can only infer account existence through surfaced profile cards (if eligible).

---

### 2) Profile

#### Required fields and validation rules
- `profile_id` (UUID, required).
- `user_id` (required FK to `User`, unique one-to-one active profile).
- `display_name` (required, length 2-50, profanity/unsafe-content filter).
- `bio` (optional, max length e.g., 500 chars, content policy checks).
- `photos[]` (at least 1 required for discoverability; each photo must pass moderation).
- `gender_identity` (required if needed for recommendation filters; enum/free-text with policy limits).
- `location` (required for local matching; coarse geohash/city-level stored for sharing).
- `profile_completion_score` (derived numeric 0-100).
- `visibility_status` (required, enum: `hidden`, `discoverable`, `paused`).

#### State transitions
- `hidden -> discoverable` once minimum profile completeness and moderation checks pass.
- `discoverable -> paused` when user pauses dating mode.
- `paused -> discoverable` when user resumes.
- Any state -> `hidden` when policy violation, failed re-verification, or account suspension.

#### Privacy constraints
- Public card fields: display name, age (derived), photos, bio, high-level location.
- Exact coordinates, moderation flags, and internal scoring are never shown to other users.
- Profile visibility strictly follows `visibility_status` and block lists.

---

### 3) Preference

#### Required fields and validation rules
- `preference_id` (UUID, required).
- `user_id` (required FK to `User`, one active preference set per user).
- `age_range_min`, `age_range_max` (required, min <= max, both >= legal minimum).
- `distance_km` (required, numeric range e.g., 1-500).
- `interested_in[]` (required non-empty if filtering by gender/identity).
- `dealbreakers[]` (optional normalized tags).
- `updated_at` (required timestamp).

#### State transitions
- Preferences are versioned: update creates a new effective version.
- New version becomes active immediately or at next recommendation cycle.
- Invalid preferences (e.g., impossible range) are rejected and prior version remains active.

#### Privacy constraints
- Raw preference values are private to the owner and recommendation service.
- Other users must not infer explicit dealbreakers from ranking behavior.
- Analytics access must be aggregated/anonymized.

---

### 4) CompatibilityScore

#### Required fields and validation rules
- `score_id` (UUID, required).
- `user_id` (required FK; scorer/recipient direction must be explicit).
- `candidate_user_id` (required FK).
- `score` (required decimal 0.0-1.0 or 0-100 normalized).
- `feature_vector_version` (required model/schema version).
- `computed_at` (required timestamp, TTL policy enforced).
- Unique key on (`user_id`, `candidate_user_id`, `feature_vector_version`, `computed_at_bucket`) as needed.

#### State transitions
- `generated -> eligible` after exclusion filters (blocks, prior decisions, safety rules).
- `eligible -> expired` after TTL or model invalidation.
- `eligible -> consumed` when recommendation is surfaced.

#### Privacy constraints
- Score internals and model features are not user-visible.
- Users may receive only coarse explanations (e.g., "similar interests"), not raw scores.
- Access limited to recommendation pipeline and auditing roles.

---

### 5) SwipeDecision

#### Required fields and validation rules
- `decision_id` (UUID, required).
- `actor_user_id` (required FK to `User`).
- `target_user_id` (required FK to `User`, must differ from actor).
- `decision` (required enum: `like`, `pass`, `super_like` if enabled).
- `source_recommendation_id` (optional FK for attribution).
- `created_at` (required timestamp).
- Unique constraint on (`actor_user_id`, `target_user_id`) for active decision or explicit overwrite policy.

#### State transitions
- `recorded` on successful write.
- If `decision=like` and reciprocal like exists, emits `mutual_like` event.
- `pass` can be reversible only if product policy allows undo window.

#### Privacy constraints
- One-sided likes remain private until mutual like.
- Pass actions are never disclosed to targets.
- Decision history visible to user and internal systems only.

---

### 6) Match

#### Required fields and validation rules
- `match_id` (UUID, required).
- `user_a_id`, `user_b_id` (required FKs, canonical ordering to avoid duplicates).
- `created_reason` (required enum: `mutual_like`, `admin_restore`).
- `status` (required enum: `active`, `unmatched`, `blocked`, `expired`).
- `created_at`, `updated_at` (required).
- Unique active match per pair.

#### State transitions
- Created **only** when mutual positive intent exists (`like` + reciprocal `like`), unless admin restore path is used.
- `active -> unmatched` when either party unmatches.
- `active -> blocked` when either party blocks/reports with hard-hide.
- `active -> expired` after inactivity timeout (if product supports expiration).
- Terminal states prevent messaging unless restored by policy.

#### Privacy constraints
- Match existence is visible only to the two matched users and authorized internal roles.
- Unmatch/block reason visibility is restricted (typically not fully disclosed to peer).
- Matched state should not reveal who liked first.

---

### 7) Conversation

#### Required fields and validation rules
- `conversation_id` (UUID, required).
- `match_id` (required FK to `Match`, one-to-one unless product allows multiple threads).
- `participant_ids[]` (exactly two users for direct match chat).
- `status` (required enum: `open`, `archived`, `closed`).
- `last_message_at` (nullable until first message).
- `created_at` (required).

#### State transitions
- Auto-created when `Match` becomes `active` (or lazily on first message).
- `open -> archived` by user action (soft, user-specific if supported).
- `open|archived -> closed` on unmatch/block/compliance closure.

#### Privacy constraints
- Visible only to participants and authorized moderation tooling.
- Closed conversations are hidden from blocked users depending on legal retention policy.
- Metadata exposure in push notifications must avoid sensitive preview leaks.

---

### 8) Message

#### Required fields and validation rules
- `message_id` (UUID, required).
- `conversation_id` (required FK to `Conversation`).
- `sender_user_id` (required FK; must be participant of conversation).
- `body` (required unless media-only message allowed; length and policy checks).
- `media_attachments[]` (optional, scanned and signed URL protected).
- `sent_at` (required timestamp).
- `delivery_status` (required enum: `sent`, `delivered`, `read`, `failed`).

#### State transitions
- `sent -> delivered -> read` in normal flow.
- `sent -> failed` when transport/policy rejection occurs.
- Messages can become `redacted` by moderation; original retained per compliance rules.

#### Privacy constraints
- End-to-end or transport encryption in transit; encrypted at rest.
- Read receipts and typing indicators must honor user privacy settings.
- Only participants and authorized safety reviewers can access message content.

---

### 9) SafetyReport

#### Required fields and validation rules
- `report_id` (UUID, required).
- `reporter_user_id` (required FK).
- `reported_user_id` (required FK).
- `context_type` (required enum: `profile`, `message`, `conversation`, `offline_incident`).
- `context_id` (optional/required depending on `context_type`).
- `reason_code` (required enum/taxonomy, e.g., harassment, spam, impersonation).
- `description` (optional free text with max length).
- `evidence_refs[]` (optional attachments or message IDs).
- `status` (required enum: `submitted`, `triaged`, `actioned`, `closed`).
- `created_at`, `updated_at` (required).

#### State transitions
- `submitted -> triaged` by safety operations queue.
- `triaged -> actioned` when enforcement decision is executed.
- `actioned -> closed` after notifier/audit completion.
- Severe reports may trigger immediate protective actions (temporary hide/block) before full triage.

#### Privacy constraints
- Reporter identity is never disclosed to the reported user.
- Only need-to-know safety staff can access full report contents.
- Enforcement outcomes shared with reporter in limited, policy-safe form.

---

## Relationship Summary

- `User 1:1 Profile`
- `User 1:1 Preference` (active version)
- `User 1:N SwipeDecision` (as actor) and `User 1:N SwipeDecision` (as target)
- `User 1:N CompatibilityScore` (viewer-centric)
- `User N:N User` via `Match` (pairwise unique)
- `Match 1:1 Conversation`
- `Conversation 1:N Message`
- `User 1:N SafetyReport` (as reporter) and `User 1:N SafetyReport` (as reported)

## Cross-Entity Invariants

1. A `Message` cannot be sent unless corresponding `Match.status = active` and conversation is open.
2. A `Match` cannot exist without reciprocal positive `SwipeDecision` (unless explicit admin restore path).
3. Block/suspension immediately removes discoverability and recommendation eligibility.
4. Deletion and retention workflows must preserve legal audit artifacts while removing user-visible data.

## Sequence Diagrams (text-based)

### A) Onboarding

```text
User -> AuthService: Sign up (email/phone/provider)
AuthService -> User: Verification challenge
User -> AuthService: Submit verification
AuthService -> UserService: Create User(status=active)
User -> ProfileService: Submit profile details + photos
ProfileService -> ModerationService: Scan text/images
ModerationService -> ProfileService: Pass/flag
ProfileService -> PreferenceService: Save preferences
ProfileService -> RecommendationService: Mark profile discoverable
RecommendationService -> User: Ready for recommendations
```

### B) Recommendations

```text
User -> RecommendationService: Request next candidates
RecommendationService -> PreferenceService: Load user preferences
RecommendationService -> GraphStore: Exclude blocked/passed/matched users
RecommendationService -> ScoringService: Compute compatibility scores
ScoringService -> RecommendationService: Ranked candidates
RecommendationService -> User: Return profile cards
User -> SwipeService: Submit like/pass
SwipeService -> EventBus: Publish SwipeDecisionRecorded
```

### C) Mutual match

```text
User A -> SwipeService: Like User B
SwipeService -> DecisionStore: Persist A->B like
User B -> SwipeService: Like User A
SwipeService -> DecisionStore: Persist B->A like
SwipeService -> MatchService: Detect reciprocal likes
MatchService -> MatchStore: Create Match(status=active)
MatchService -> ConversationService: Create conversation
ConversationService -> NotificationService: Notify both users
NotificationService -> User A/User B: "It's a match"
```

### D) Messaging

```text
User A -> MessagingService: Send message(conversation_id, body)
MessagingService -> MatchService: Validate match active
MessagingService -> PolicyService: Run safety/content checks
PolicyService -> MessagingService: Allow/deny
MessagingService -> MessageStore: Persist message(status=sent)
MessagingService -> RealtimeGateway: Deliver to User B
RealtimeGateway -> User B: New message event
User B -> MessagingService: Read receipt
MessagingService -> MessageStore: Update delivery_status=read
```
