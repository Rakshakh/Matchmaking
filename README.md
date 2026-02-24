# Matchmaking

A production-ready minimal matchmaking app with:
- static web UI
- API-backed match scoring
- health endpoint for ops checks

## Run

```bash
python3 server.py
```

Then open: <http://localhost:4173>

## API

- `GET /api/health`
- `GET /api/match?age=29&intent=long-term&interests=hiking,music`

## Test

```bash
python3 -m unittest discover -s tests
```
