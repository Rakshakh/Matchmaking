# Matchmaking

A thin but working matchmaking service that covers a v1 path:

1. User sign-up/login.
2. Profile creation with required compatibility fields.
3. Recommendation list using a baseline ranking strategy.
4. Like/pass interactions with mutual match creation logic.
5. Basic 1:1 chat for matched users.

Instrumentation events are emitted at each step for basic product metrics.

## Quick start

```bash
python -m unittest -v
```

Core implementation is in `matchmaking/service.py`.
