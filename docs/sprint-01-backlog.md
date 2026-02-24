# Sprint 01 Backlog: Build Toward Vision v1

## Sprint Goal
Deliver a measurable MVP matchmaking pipeline with queueing, ranking, and match commit observability.

## Scope

### 1) Event Instrumentation Contract
- [ ] Define core events and payload schema.
- [ ] Add event naming conventions.
- [ ] Define KPI dashboard requirements.

**Acceptance criteria**
- Event schema includes queue entry, candidate retrieval, candidate scored, match proposed, match committed, and queue exit.
- Each event includes traceable IDs (`user_id`, `session_id`, `match_id`, `request_id`, timestamp).

### 2) Queue Service (MVP)
- [ ] Implement enqueue/dequeue lifecycle states.
- [ ] Add TTL handling for stale entries.
- [ ] Add retries with bounded attempts.

**Acceptance criteria**
- Users can enter and exit queue reliably.
- Stale users are cleaned up within configured TTL.

### 3) Candidate Retrieval
- [ ] Implement baseline eligibility filters.
- [ ] Add configurable candidate window size.
- [ ] Log retrieval diagnostics for misses.

**Acceptance criteria**
- Retrieval returns only eligible candidates.
- Empty retrievals generate diagnostic events.

### 4) Ranking + Match Commit
- [ ] Implement simple weighted scoring.
- [ ] Select top candidate pair.
- [ ] Atomically commit match and remove queue entries.

**Acceptance criteria**
- Match commits are idempotent and auditable.
- Conflicts from stale candidates are retried safely.

### 5) KPI Dashboard Starter
- [ ] Wire core metrics from event stream.
- [ ] Publish first cut dashboard with P50/P95 time-to-match and acceptance rate.

**Acceptance criteria**
- Dashboard updates from live/test events.
- Team can inspect regressions by day and segment.

## Risks
- Thin early traffic may distort quality metrics.
- Missing event coverage can block tuning.
- Queue contention may affect P95 latency.

## Definition of Done
- Feature is shipped behind a flag (if applicable).
- Events are emitted and visible in dashboard.
- Basic happy path and failure path are manually validated.
