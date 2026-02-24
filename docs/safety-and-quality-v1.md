# Safety and Quality v1

## Scope and goals
This document defines the minimum safety, anti-abuse, and quality controls required before beta launch of Matchmaking v1.

Goals:
- Reduce user harm from harassment, scams, and explicit/abusive content.
- Provide clear in-product reporting and blocking capabilities.
- Detect and limit spam/automation abuse.
- Establish consistent human review and enforcement.
- Prevent launch until baseline reliability, privacy, and abuse controls are ready.

---

## 1) Report/block actions in recommendations and chat

### Product surfaces
Implement **Report** and **Block** on:
1. **Recommendations card/profile view** (before matching).
2. **Chat thread header / overflow menu** (after matching).
3. Optional: profile detail screen from chat.

### User actions and expected behavior

#### Report
- Entry points:
  - `Report profile` from recommendation card/profile.
  - `Report user` and `Report message` from chat.
- Report reasons (single-select + optional free text):
  - Harassment or hate
  - Sexual content
  - Spam or scam
  - Fake profile / impersonation
  - Underage concerns
  - Violence or threats
  - Other
- On submit:
  - Persist report with reporter ID, reported user ID, optional message ID, reason, details, timestamp, app version, and moderation signals snapshot.
  - Show confirmation: “Thanks — we’ll review this report.”
  - Keep reporter identity hidden from the reported user.

#### Block
- Entry points:
  - `Block` from recommendation card/profile.
  - `Block` from chat menu.
- On block:
  - Immediately prevent both users from messaging each other.
  - Remove each from recommendation/swipe pools for each other.
  - Hide existing chat thread from blocker by default (accessible in blocked list if needed).
  - Auto-unmatch if currently matched.
  - Offer optional “Block and report” combined action.

### Data and API requirements
- New/updated entities:
  - `reports`
  - `blocks`
  - `moderation_events` (audit trail)
- API endpoints (illustrative):
  - `POST /reports`
  - `POST /blocks`
  - `DELETE /blocks/:targetUserId` (unblock)
- Enforcement checks on every write path:
  - deny message send if either user blocked the other;
  - deny appearance in recommendation candidates when blocked relationship exists.

### UX and safeguards
- Require confirmation for Block (lightweight modal).
- Allow user to undo block via settings.
- Rate-limit report submissions per user to prevent report spam, but do not block legitimate repeated reports in severe cases.

---

## 2) Basic content moderation strategy for text messages

### Moderation model (v1)
Use a **hybrid rules + ML classifier** pipeline for every outbound message:
1. **Rules layer** (deterministic): keyword/regex detection for slurs, explicit solicitations, scam phrases, doxxing patterns, and obvious threats.
2. **ML layer**: toxicity/harassment/sexual/scam classifier that returns category scores.
3. **Decision layer** with thresholds:
   - **Allow**: low risk.
   - **Soft-intervene**: medium risk → show sender warning (“This may violate guidelines. Edit before sending?”).
   - **Block send**: high risk categories (e.g., explicit threats, severe hate, coercive sexual content, clear scam intent).

### Enforcement policy
- If blocked by moderation:
  - Message is not delivered.
  - Sender sees concise reason + link to community guidelines.
  - Event logged for abuse scoring.
- If soft intervention:
  - User can edit and resend.
  - Optionally allow override once, but log as elevated risk.

### False-positive handling
- Keep thresholds conservative during beta.
- Capture reviewer outcomes to tune thresholds weekly.
- Support appeal path via in-app support ticket for enforcement mistakes.

### Privacy and storage
- Store only required moderation metadata and minimal message excerpts for review.
- Limit full message retention for moderation queue to a defined TTL.
- Restrict moderation tooling access by role; audit all reviewer access.

---

## 3) Rate limits and anti-abuse constraints for swiping and messaging

### Swiping limits (starter values)
- Per-user cap:
  - `max 120` right-swipes per rolling 24h.
  - `max 40` right-swipes per rolling hour.
- Burst control:
  - no more than `20` swipe actions per minute sustained.
- Quality guard:
  - detect indiscriminate swiping (e.g., >95% right-swipes over large sample) and apply temporary friction:
    - cooldown,
    - captcha/verification challenge,
    - lower recommendation priority.

### Messaging limits
- New match safeguard:
  - max `3` unanswered messages to a new match within first 24h.
- Global messaging rate:
  - max `30` messages per 5 minutes.
  - max `200` messages per 24h.
- Content duplication checks:
  - detect high-volume repeated message templates across many recipients; throttle or block.

### Account and device abuse controls
- Progressive trust levels based on account age, verification status, and prior reports.
- Device/IP heuristics:
  - multiple account creation attempts from same device/IP in short windows;
  - rapid login/account cycling.
- Anti-automation:
  - challenge suspicious sessions with captcha or step-up verification.

### Penalty ladder
1. Warn user (in-product).
2. Temporary action cooldown.
3. Temporary feature suspension (swipe or messaging).
4. Account suspension pending review.
5. Permanent ban for severe/repeat abuse.

All penalties should create immutable moderation events for auditability.

---

## 4) Manual admin review workflow for reports

### Triage queue design
Create moderation queues sorted by severity and recency:
- **P0**: threats, underage, violent/extortion risk.
- **P1**: harassment/hate/sexual coercion/scam.
- **P2**: spam/fake profiles/other policy violations.

### Reviewer workflow
1. **Intake**: report enters queue with context (users involved, conversation snippet, prior reports, trust/risk score).
2. **Assignment**: auto-assign by severity and reviewer availability.
3. **Decision**: reviewer selects outcome:
   - no action,
   - warning,
   - temporary restriction,
   - suspension,
   - permanent ban,
   - escalate to safety lead/legal (if required).
4. **Documentation**: mandatory rationale + policy tag + evidence references.
5. **Notification**:
   - reporter: generic resolution message where appropriate.
   - reported user: enforcement notice and appeal option (except legal-sensitive cases).
6. **Appeals**: secondary reviewer handles appeal; SLA target defined.

### SLA targets (beta)
- P0: first response within 15 minutes, resolution within 2 hours.
- P1: first response within 4 hours, resolution within 24 hours.
- P2: first response within 24 hours, resolution within 72 hours.

### Admin tooling requirements
- Case timeline view (reports, messages, prior actions).
- One-click enforcement actions + reversible actions where allowed.
- Full audit logs of reviewer actions.
- Role-based access control and least-privilege permissions.

---

## Launch checklist (must pass before beta rollout)

### A. Reliability and operational readiness
- [ ] Error monitoring, alerting, and dashboards configured for moderation/report/block APIs.
- [ ] Backpressure/fallback behavior defined if moderation service is degraded.
- [ ] Queue processing retries + dead-letter queue enabled for report ingestion.
- [ ] On-call runbook for abuse spikes and moderation outages.
- [ ] Load test completed for peak messaging/swiping traffic.

### B. Privacy and data protection
- [ ] Data classification completed for chat/report/moderation data.
- [ ] Retention policy documented (raw message snippets, report evidence, audit logs).
- [ ] RBAC enforced for moderation/admin tools.
- [ ] Access logging and periodic access review process enabled.
- [ ] User-facing policy/legal copy updated (community guidelines, reporting, appeals).

### C. Abuse prevention and moderation readiness
- [ ] Report and block flows live in recommendations and chat.
- [ ] Message moderation pipeline enabled with tested thresholds.
- [ ] Rate limits active for swiping and messaging in production config.
- [ ] Manual review queue staffed with trained reviewers and escalation path.
- [ ] Appeal workflow documented and operational.
- [ ] Enforcement analytics dashboard live (report volume, action rate, false-positive trend, repeat-offender rate).

### D. Go/No-Go gate
- [ ] No critical-severity open bugs in report/block/moderation flows.
- [ ] P0/P1 moderation SLA dry run passed.
- [ ] Security/privacy sign-off completed.
- [ ] Product, engineering, and safety owner approvals recorded.

If any checkbox in sections A–D is incomplete, beta launch is blocked.
