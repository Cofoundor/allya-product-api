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
| GET | `/brain` | `BrainPage` — the whole memory page: its words, its floors and counts, and the joined company view |
| GET | `/brain/nodes/{nid}` | `BrainNodeDetail` — what one node is, what hangs off it, where it may be moved, and what may be said about it; **404** unknown |
| GET | `/brain/search?q=` | `BrainSearch` — matches anywhere in the brain, each with the scope it opens in; **422** under 2 characters |
| GET | `/brain/suggestions` | `BrainSuggestionList` — what the founder has asked her to change, newest first |
| POST | `/brain/suggestions` | `BrainSuggestionAck` — body `{nodeId, kind, text?, toParent?, why?}`; **201**, **404** unknown node, **422** if the kind's payload is missing or the change is a no-op |
| DELETE | `/brain/suggestions/{sgid}` | **204**; **409** once something has acted on it |
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
| GET | `/profile` | `Profile` — you, as Allya holds you; **401** signed out |
| PATCH | `/profile` | `Profile` — body `{name?, role?, company?}`; name and company write back to the account |
| PATCH | `/profile/habits/{hid}` | `Profile` — body `{value}`; **422** if the habit has `options` and this isn't one |
| PATCH | `/profile/trust/{sid}` | `Profile` — body `{level}`; one floor's leash |
| POST | `/profile/knows` | `Profile` — body `{text}`; **201**, lands at the top marked `told` |
| DELETE | `/profile/knows/{kid}` | `Profile` — forget one; **404** if it isn't held |
| GET | `/profile/answers` | `AnswerBook` — every onboarding answer; **401** signed out |
| PATCH | `/profile/answers/{gid}/{key}` | `AnswerBook` — body `{value}`; **409** if that onboarding was never run, **422** on a blank or a bad option |
| POST | `/profile/answers/company` | `AnswerBook` — body `{answers}`; **201**, what the company onboarding heard on its way past |

Status codes: `200` on success, `404` unknown surface / work / fact,
`409` approving something already shipped or undoing something that never
shipped, `422` on a malformed body, `month` or `date`.

`surface_id` is one of `workspace`, `marketing`, `hiring`, `pr`, `sales`, `ops`.
The workspace's `/work` and `/calendar` return every service's items; a service
returns only its own.

### `/brain` — the whole memory

`product-next`'s `/brain` page draws nothing it invents, so five things that
would otherwise be frontend logic are decided here:

- **The join.** `GET /brain` returns the *company view*: the hub, its floors,
  and the shape of each — a floor's directions, plus any thought that exists
  only on the company ring. Not every thought in the company: the canvas lays
  out a hub, its departments and their direct children, so a floor's leaves
  cannot be placed in the same pass, and eighty labelled dots would be a
  hairball nobody reads. You walk into a floor for its thoughts, and that is
  the floor's own `GET /surfaces/{sid}/brain`, unchanged.
- **Every string on the page**, in `copy`. Same reason every surface's words
  come from the server: Allya's voice belongs in one place, and re-wording the
  page shouldn't need a frontend deploy.
- **What a node is.** `kindWord` is decided by where the node was found, not
  by its tier — the company graph's tier 2 is a leaf thought while a floor's
  tier 2 is a direction with thoughts under it, so reading the word off the
  tier alone called "Own fast, not cheap" a direction.
- **What may be said about it.** `verbs` is a rule about the graph: your
  company is not a belief to be corrected, a floor can only be told something
  under it is missing, and a direction or thought is fair game. `moveTargets`
  is every place a thought could legally go — never inside itself, never where
  it already is. Adding a fifth verb is a backend change alone.
- **Where a match lives.** `/brain/search` answers with the `scope` the client
  must be in to open each hit, because whether a node is reachable on the ring
  or only inside its floor is a fact about the join.

`nodeId` on a suggestion is the thought itself for `reword` / `remove` /
`move`, and the **parent** the new thought should hang under for `add`.
`surfaceId`, `nodeLabel`, `kindWord`, `summary` and `stateWord` are the
server's, so the drawer maps nothing; `POST` answers with a `toast` in her
words rather than the client's.

**Nothing is applied.** A suggestion is stored `pending` and the graph does not
move — deciding what a correction should do to the graph is the real work, and
it belongs behind a model, not in a dummy. `applied` and `declined` exist in
the contract so the client can render them; nothing here produces them yet.
`BRAIN_SUGGESTIONS` in `data.py` is seeded empty on purpose: everything else in
that file is invented content, and these are supposed to be the founder's own
words about their own company.

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

### You

`/profile` is the founder half of the record — the company has a brain, this is
who it answers to. Three things live on it, and only one of them is a setting:

- **`knows`** — what Allya holds about *you*, not about the company. The
  company's own facts are `/surfaces/{sid}/knowledge`; these never mix. Each
  entry carries a `source`: `told` is something you said, `learned` is
  something she inferred — and only `learned` carries a `note`, which is the
  evidence. Anything you add is `told` with no note, because inventing one
  would be the one lie this seam exists to prevent.
- **`habits`** — how you work. A habit with a non-empty `options` only accepts
  one of them; an empty `options` is free text.
- **`trust`** — one leash per service floor, at `ask`, `brief` or `trusted`.
  `ui.levels` is what the three rungs mean in general; each row's `note` is what
  the *current* rung means on *that* floor. The note is derived on read, never
  stored — a stored one goes stale the moment the rung moves.

Every write returns the whole `Profile` rather than the piece that changed,
because moving a rung rewrites the sentence under it and the client shouldn't
have to reassemble that itself.

Profiles are seeded per user id on first read, so editing the demo account
doesn't rewrite the founder's.

Three figures live on `stats` and earn the top of the page; the rest are on
`statGroups`, grouped by the question they answer. `ui.lenses` names the three
ways of reading the left-hand pane — the leash is not one of them, deliberately.

**The vocabulary belongs here, not to the view.** `ui.sourceLabels` and
`ui.connectionLabels` are what this API's enums are called on screen, the same
idea as `/crm/lexicon`; `ui.identity` names the editable fields on the identity
card the way a `Habit` carries its own `label`; `ui.actions` holds the words on
the controls that act on this page's nouns (forgetting a memory, loosening a
leash). `summaries` is the line each section puts in its own header —
`"6 things · 2 you told me"`, `"2 want you"` — recomputed on every read so a
write can never leave a stale count.

None of that is decoration. A frontend that keeps its own copy of "you told me"
has forked the contract: the server can change what `told` means and the screen
will keep saying the old thing. The order of `ui.levels` matters for the same
reason — it is what tells the interface which direction is *looser*, so adding
a rung here cannot silently skip the confirmation the UI puts in front of it.

### The answer book

`/profile/answers` is every onboarding answer, readable and changeable. These
used to be write-only: a floor's four went into `ANSWERS` and were never read
back, and the company's six never left the browser at all. A founder who
mistyped their revenue in week one had no way to correct it short of starting
over, and everything downstream had already been built on it.

One `AnswerGroup` per onboarding — `company`, then one per service floor. A
floor nobody has set up is **`new`**, not a group of empty answers: it has not
been asked yet, so the book says so and offers `href`/`cta` rather than a form
inventing questions. Finish that floor's onboarding and its group turns
`complete` and becomes editable, because `POST /surfaces/{sid}/onboarding`
writes to the same `ANSWERS`. Which drawer opens (`open`), what its status is
called (`statusLabel`) and what an unasked group says instead (`empty`) are all
decided here too.

An answer can be **changed but not emptied** (**422**), and a `choice` only
takes one of its `options`. `learned` is the ledger line the answer added —
the reason the question was worth asking, and what makes changing one read as
a decision rather than editing a field.

`COMPANY_ONBOARDING` in `data.py` mirrors `product-next/src/lib/onboarding-data.ts`
rather than replacing it: the live flow still asks the questions client-side
because it also owns the acks, the clusters and the showcase reading, none of
which are the API's business yet. Keep `key`, `q` and `type` in step across the
two. `POST /profile/answers/company` is how a real run's answers get here — the
flow calls it once at the end, partial on purpose, so a founder who skipped a
question still keeps the ones they gave.

Like `ONBOARDED`, `ANSWERS` is global to the process rather than per user.

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
