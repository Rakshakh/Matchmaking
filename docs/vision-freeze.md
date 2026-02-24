# Matchmaking Vision Freeze (v1)

## Product Vision
Build a fast, fair, and trustworthy matchmaking experience that consistently gets users to a high-quality match in under 60 seconds.

## Product Principles
1. **Speed first**: reduce time-to-match from queue entry to committed match.
2. **Quality over volume**: optimize for accepted matches and post-match satisfaction.
3. **Fairness by default**: avoid systematic disadvantage across user segments.
4. **Trust through clarity**: users should always understand where they are in the process.

## Success Metrics

### Primary KPIs
- **P50 time-to-match**: <= 30 seconds.
- **P95 time-to-match**: <= 60 seconds.
- **Match acceptance rate**: >= 70%.
- **Day-1 post-match return rate**: >= 40%.

### Guardrail Metrics
- Queue abandonment rate.
- Match cancellation rate.
- Segment-level acceptance parity.
- Error rate in match commit pipeline.

## User Journey (MVP)
1. User enters queue with preferences and availability.
2. System continuously retrieves viable candidates.
3. Candidates are scored and ranked.
4. Top pair is proposed and committed if both are eligible.
5. Users receive immediate state updates (matched / still searching / retrying).

## Non-Goals (MVP)
- Social graph imports.
- Long-form compatibility questionnaires.
- Multi-party matching.
- Cross-region balancing beyond basic fallback.

## Release Strategy
- **Phase 1 (Weeks 1-2):** Instrumentation, queue service, candidate retrieval.
- **Phase 2 (Weeks 3-4):** Scoring/ranking, commit flow, retries/timeouts.
- **Phase 3 (Week 5):** Fairness and quality calibration, UX polish.

## Decision Filter
Any new task must improve at least one of: speed, quality, fairness, trust. If not, it is deprioritized.
