# Product Vision v1

## 1) Problem Statement and Target Users

### Problem statement
People looking for meaningful connections are often overwhelmed by low-signal profiles, inconsistent matching quality, and unsafe interactions. Existing experiences can create friction between discovery and genuine conversation, resulting in low confidence and poor follow-through.

### Target users
- **Primary:** Adults (18+) seeking romantic connections in their local region through a simple, mobile-friendly matching flow.
- **Secondary:** New-to-online-dating users who need clear guidance and low-friction onboarding to start confidently.
- **Tertiary:** Time-constrained users who want fast profile setup, relevant matches, and lightweight safety controls.

## 2) Core v1 Jobs-to-be-Done

1. **Set up a profile quickly and credibly** so others can understand who I am and what I’m looking for.
2. **Discover relevant people efficiently** without scrolling through obviously incompatible options.
3. **Express interest or decline clearly** with minimal cognitive load.
4. **Start a conversation after a mutual match** in a straightforward, low-pressure chat experience.
5. **Feel reasonably safe while using the product** via basic reporting, blocking, and platform guardrails.

## 3) In-Scope v1 Features

### Profile
- Account creation and onboarding flow.
- Editable profile with core fields (photos, bio, age range/preferences, location radius).
- Basic profile completeness indicator to encourage minimum viable quality.

### Matching
- Candidate feed generated from basic compatibility filters (location, age preferences, mutual intent fields).
- Deterministic ranking/selection suitable for v1 (no advanced ML required).

### Likes / Passes
- Swipe or tap controls for **Like** and **Pass** decisions.
- Persistent decision state to avoid repeat surfaces of passed profiles within a reasonable window.
- Mutual-like detection that creates a match record.

### Messaging
- 1:1 text messaging enabled only after mutual match.
- Simple conversation list and thread view.
- Basic abuse controls in-message (block/report entry points).

### Safety Basics
- Report user flow with categorized reasons.
- Block user flow preventing further interaction.
- Lightweight trust controls (rate-limiting / anti-spam basics and visible community guidelines).

## 4) Out-of-Scope for v1

- Advanced AI dating coach, personalized prompt generation, or AI-led relationship advice.
- Video dates, voice calls, or live-stream interactions.
- Premium monetization (subscriptions, boosts, super likes, à la carte purchases).
- Deep social graph integrations and external friend-of-friend discovery.
- Complex verification systems (e.g., full KYC), beyond basic account integrity checks.
- Enterprise analytics tooling beyond core product KPIs.

## 5) Measurable v1 Success Metrics

1. **Activation rate:** % of new signups who complete profile and perform at least one Like/Pass within 24 hours.
2. **Match rate:** % of active users who receive at least one mutual match per 7-day period.
3. **Conversation start rate:** % of new matches where at least one message is sent within 24 hours of matching.
4. **Conversation continuation rate:** % of matched conversations that reach 3+ messages in 48 hours.
5. **Safety report rate:** # of reports per 1,000 active users (tracked with severity mix and response SLA).

---

## v1 North Star

**North Star:** Increase the number of safe, meaningful conversations started per active user each week.

Supporting assumptions:
- Better profile quality improves match relevance.
- Faster decision loops (Like/Pass) improve discovery throughput.
- Strong baseline safety controls increase trust and retention.
