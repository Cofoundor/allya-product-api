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
`ALLOWED_ORIGINS` (comma-separated, no trailing slash).

> `--reload` has been seen to log "detected changes… Reloading" and carry on
> serving the old module. If an edit to `data.py` doesn't show up, restart the
> process rather than trusting the reloader.

## Deploy

`render.yaml` is a ready blueprint (Render → New → Blueprint → this repo).
Any host works — it only needs to bind `$PORT`:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Two things must line up or the browser gets a CORS error and the frontend
shows its offline state everywhere:

| Where | Variable | Value |
| --- | --- | --- |
| this service | `ALLOWED_ORIGINS` | the frontend's origin, e.g. `https://allyafn.netlify.app` |
| the frontend | `NEXT_PUBLIC_API_URL` | this service's origin **+ `/api/v1`** |

`NEXT_PUBLIC_*` is baked into the client bundle at build time, so changing it
needs a redeploy of the frontend, not just a restart.

**State resets on every restart, and free tiers sleep.** That's fine for a
contract stand-in; it is not a production backend.

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
| GET | `/surfaces/{sid}/calendar?month=` | `CalendarMonth` — one month of the grid; **422** if `month` isn't `YYYY-MM` |
| GET | `/surfaces/{sid}/calendar/{date}` | `DayAgenda` — one day's entries; **422** if `date` isn't `YYYY-MM-DD` |
| GET | `/surfaces/{sid}/knowledge?period=&date=` | `FactList` |
| GET | `/surfaces/{sid}/conversation` | `Reply` — the opening beats |
| POST | `/surfaces/{sid}/conversation/messages` | `Reply` — body `{text}` |
| GET | `/surfaces/{sid}/onboarding` | `ServiceOnboarding` — the four questions that make a floor usable |
| POST | `/surfaces/{sid}/onboarding` | `OnboardingResult` — body `{answers}`; unlocks the floor, **422** if any are blank |
| GET | `/gate` | `Gate` — the sign-in page's copy and the graph behind it |
| POST | `/session` | `Session` — body `{email, password}`; **201**, or **401** |
| GET | `/session` | `User` — who the bearer token belongs to, or **401** |
| DELETE | `/session` | **204**; signing out twice is not an error |
| GET | `/work/{wid}/review` | `Review` — the approval sheet |
| POST | `/work/{wid}/approve` | `WorkAction` — `{item, toast, reply}` |
| POST | `/work/{wid}/undo` | `WorkAction` |
| POST | `/work/{wid}/revision` | `Reply` |
| PATCH | `/knowledge/{fid}` | `Fact` — body `{flagged?, text?}` |

Status codes: `200` on success, `404` unknown surface / work / fact,
`409` approving something already shipped or undoing something that never
shipped, `422` on a malformed body, `month` or `date`.

`surface_id` is one of `workspace`, `marketing`, `hiring`, `pr`, `sales`, `ops`.
The workspace's `/work` and `/calendar` return every service's items; a service
returns only its own.

### The calendar

`/calendar` answers with the **current** month when `month` is omitted, and only
lists the days that hold something — the client draws the empty ones itself. Two
fields exist so it never has to guess: `firstWeekday` (Monday = 0) and
`daysInMonth`. `selected` is the day to open on — today when today is in this
month, otherwise the first day with anything on it.

A `CalendarEvent` carrying a `workId` is the same thing as the work item behind
it, so the UI opens that item's approval sheet from the calendar. `needsYou` on
a day counts only entries whose work item is *still* waiting on you — approve it
and the day's accent dot goes with it. All-day entries use `startMinute: -1`,
which is also what sorts them to the top of a day.

### Setting up a floor

Each service floor has its own short onboarding. Until it's done:

- `GET /surfaces/{sid}` returns `onboarded: false` and a `lock` (the copy the
  UI shows when you try to *act* on the floor — reading it is never blocked);
- `GET /surfaces/{sid}/brain` returns a **semi-complete** graph: the floor's
  shape and anything already proven by live work, with the branches marked
  `provisional`. Posting the answers fills it in.

`ONBOARDED` starts false for all five services and is global to the process,
not per user — a dummy, like the rest of this.

### Signing in

> **Not authentication.** Seeded accounts, one shared demo password, tokens in
> a dict until the process restarts. No hashing, no expiry, no sessions table.
> It exists so the sign-in page has a real 401 to render and the product can
> tell you who you are. Replace it wholesale before anything real.

| Email | Password |
| --- | --- |
| `sanshat@zeroto10.ai` | `allya` (override with `DEMO_PASSWORD`) |
| `demo@zeroto10.ai` | same |

Any other email, or the wrong password, returns 401 with a single message for
both cases — never reveal which half was wrong. The product is **not gated**:
`/` works signed out, and the topbar offers a way in.

## Files

- `main.py` — the app and every route
- `models.py` — the Pydantic schemas (the actual contract)
- `data.py` — in-memory seed: surfaces, brain graphs, work, reviews, facts,
  schedules, calendar, conversation scripts. Calendar dates are offsets from
  `date.today()`, so the month always has something in it whenever this runs

Mutations (`approve`, `undo`, `patch`) edit the in-memory dicts, so state
resets on restart. That is deliberate.
