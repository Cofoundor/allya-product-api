# product-api — the Allya product API contract

> **Status:** dummy backend. It exists to pin down the API contract for
> `product-next/`, not to implement business logic. In-memory state, static
> seeds, no auth, no database. Replace the route bodies with real logic and the
> frontend should not need to change.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Docs at http://localhost:8000/docs. The frontend expects
`NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

CORS allows `http://localhost:4322` (the Next dev server); override with
`ALLOWED_ORIGINS` (comma-separated).

## Contract

All paths are under `/api/v1`. Field names are **camelCase on the wire**
(snake_case in Python — see `Base` in `models.py`).

| Method | Path | Returns |
|---|---|---|
| GET | `/surfaces` | `SurfaceSummary[]` — the page switcher |
| GET | `/surfaces/{sid}` | `Surface` — greeting, placeholder, suggestions, brain header, node copy |
| GET | `/surfaces/{sid}/brain` | `BrainGraph` — `{layout, anchorId, nodes[], links[]}` |
| GET | `/surfaces/{sid}/work` | `WorkList` — `{items[], summary}` |
| GET | `/surfaces/{sid}/schedule` | `Schedule` |
| GET | `/surfaces/{sid}/knowledge?period=&date=` | `FactList` |
| GET | `/surfaces/{sid}/conversation` | `Reply` — the opening beats |
| POST | `/surfaces/{sid}/conversation/messages` | `Reply` — body `{text}` |
| GET | `/work/{wid}/review` | `Review` — the approval sheet |
| POST | `/work/{wid}/approve` | `WorkAction` — `{item, toast, reply}` |
| POST | `/work/{wid}/undo` | `WorkAction` |
| POST | `/work/{wid}/revision` | `Reply` |
| PATCH | `/knowledge/{fid}` | `Fact` — body `{flagged?, text?}` |

Status codes: `200` on success, `404` unknown surface / work / fact,
`409` approving something already shipped or undoing something that never
shipped, `422` on a malformed body or `date`.

`surface_id` is one of `workspace`, `marketing`, `hiring`, `pr`, `sales`, `ops`.
The workspace's `/work` returns every service's items; a service returns only
its own.

## Files

- `main.py` — the app and every route
- `models.py` — the Pydantic schemas (the actual contract)
- `data.py` — in-memory seed: surfaces, brain graphs, work, reviews, facts,
  schedules, conversation scripts

Mutations (`approve`, `undo`, `patch`) edit the in-memory dicts, so state
resets on restart. That is deliberate.
