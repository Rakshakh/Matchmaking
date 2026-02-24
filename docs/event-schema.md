# Matchmaking Event Schema (MVP)

## Envelope
All events must include:
- `event_name` (string)
- `event_version` (string)
- `event_time` (ISO-8601)
- `request_id` (string)
- `session_id` (string)
- `user_id` (string)
- `match_id` (string, nullable)

## Events

### `queue.entered`
Fields:
- `queue_region` (string)
- `preferences` (object)
- `queue_priority` (number)

### `queue.exited`
Fields:
- `exit_reason` (`matched` | `cancelled` | `timeout` | `error`)
- `queue_duration_ms` (number)

### `candidate.retrieved`
Fields:
- `candidate_count` (number)
- `window_size` (number)
- `filter_reasons` (array<string>)

### `candidate.scored`
Fields:
- `candidate_user_id` (string)
- `score_total` (number)
- `score_components` (object)

### `match.proposed`
Fields:
- `candidate_user_id` (string)
- `proposal_rank` (number)
- `proposal_latency_ms` (number)

### `match.committed`
Fields:
- `counterparty_user_id` (string)
- `commit_latency_ms` (number)
- `idempotency_key` (string)

### `match.failed`
Fields:
- `failure_stage` (`retrieve` | `score` | `commit`)
- `failure_reason` (string)
- `retry_count` (number)

## Data Quality Rules
- Reject events missing required envelope fields.
- Ensure timestamp skew is less than 2 minutes.
- Enforce enum constraints on reason fields.
- Track schema drift by `event_version`.
