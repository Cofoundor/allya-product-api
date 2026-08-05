"""Dummy API for the Allya product brain surfaces.

It exists to pin down the contract, nothing more: in-memory state, static
seeds, no auth, no database. Replace the bodies with real logic and the
frontend should not need to change.

    uvicorn main:app --reload --port 8000
"""

import calendar as pycal
import datetime
import os
import secrets
from typing import Annotated, Optional

from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

import data
import models as m

app = FastAPI(title="Allya Product API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:4322").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

V1 = "/api/v1"


# ---- helpers -----------------------------------------------------------

def _surface(sid: str) -> dict:
    s = data.SURFACES.get(sid)
    if not s:
        raise HTTPException(404, f"unknown surface '{sid}'")
    return s


def _work(wid: str) -> dict:
    for w in data.WORK:
        if w["id"] == wid:
            return w
    raise HTTPException(404, f"unknown work item '{wid}'")


def _fact(fid: str) -> dict:
    for f in data.FACTS:
        if f["id"] == fid:
            return f
    raise HTTPException(404, f"unknown fact '{fid}'")


def _reply(text: str, mid: str) -> m.Reply:
    return m.Reply(messages=[m.Message(id=mid, speaker="allya", text=text)])


def _events(sid: str) -> list[dict]:
    """The workspace's calendar is every floor's; a floor sees only its own."""
    return data.CALENDAR if sid == "workspace" else [e for e in data.CALENDAR if e["surface_id"] == sid]


def _needs_you(ev: dict) -> bool:
    """An entry is yours to decide only while the work behind it still is —
    approve the item and the accent dot leaves the grid with it."""
    wid = ev.get("work_id")
    return bool(wid) and any(w["id"] == wid and w["status"] == "needs-you" for w in data.WORK)


# ---- surfaces ----------------------------------------------------------

@app.get(f"{V1}/surfaces", response_model=list[m.SurfaceSummary])
def list_surfaces():
    """The page switcher and the workspace's service links."""
    return [
        m.SurfaceSummary(id="workspace", label="Workspace", note="the whole company", href="/"),
        *[
            m.SurfaceSummary(
                id=s,
                label=data.SURFACES[s]["label"],
                note=data.SURFACES[s]["brain"]["subtitle"],
                href=f"/{s}",
                node_id=s,
            )
            for s in data.SERVICE_IDS
        ],
    ]


@app.get(f"{V1}/surfaces/{{sid}}", response_model=m.Surface)
def get_surface(sid: str):
    s = _surface(sid)
    done = data.ONBOARDED.get(sid, True)
    return m.Surface(**s, onboarded=done, lock=None if done else data.LOCKS.get(sid))


@app.get(f"{V1}/surfaces/{{sid}}/brain", response_model=m.BrainGraph)
def get_brain(sid: str):
    _surface(sid)
    graph = data.BRAINS[sid]
    if data.ONBOARDED.get(sid, True):
        return m.BrainGraph(**graph)
    # semi-complete: the floor's shape is there, but what hangs off it is only
    # what live work already proves. The rest arrives with the onboarding.
    kept = []
    for n in graph["nodes"]:
        if n["tier"] < 3:
            kept.append({**n, "provisional": n["tier"] == 2})
        elif n.get("work"):
            kept.append(n)
    ids = {n["id"] for n in kept}
    links = [l for l in graph["links"] if l[0] in ids and l[1] in ids]
    return m.BrainGraph(**{**graph, "nodes": kept, "links": links})


@app.get(f"{V1}/surfaces/{{sid}}/work", response_model=m.WorkList)
def get_work(sid: str):
    """The workspace sees every service's work; a service sees only its own."""
    _surface(sid)
    items = data.WORK if sid == "workspace" else [w for w in data.WORK if w["surface_id"] == sid]
    order = {"needs-you": 0, "running": 1, "shipped": 2}
    items = sorted(items, key=lambda w: order[w["status"]])
    return m.WorkList(items=items, summary=data.SUMMARY[sid])


@app.get(f"{V1}/surfaces/{{sid}}/schedule", response_model=m.Schedule)
def get_schedule(sid: str):
    _surface(sid)
    return m.Schedule(entries=data.SCHEDULES.get(sid, []))


@app.get(f"{V1}/surfaces/{{sid}}/calendar", response_model=m.CalendarMonth)
def get_calendar(
    sid: str,
    month: str | None = Query(None, description="YYYY-MM; defaults to the current month"),
):
    """One month of the grid. Only the days that hold something come back —
    the client already knows how to draw the empty ones."""
    _surface(sid)
    today = datetime.date.today()
    if month:
        try:
            first = datetime.date.fromisoformat(f"{month}-01")
        except ValueError:
            raise HTTPException(422, "month must be YYYY-MM")
    else:
        first = today.replace(day=1)
    prefix = first.strftime("%Y-%m")

    buckets: dict[str, list[dict]] = {}
    for e in _events(sid):
        if e["date"].startswith(prefix):
            buckets.setdefault(e["date"], []).append(e)

    days = [
        m.CalendarDay(
            date=d,
            count=len(evs),
            needs_you=sum(1 for e in evs if _needs_you(e)),
            kinds=sorted({e["kind"] for e in evs}),
        )
        for d, evs in sorted(buckets.items())
    ]

    if today.strftime("%Y-%m") == prefix:
        selected = today.isoformat()
    elif days:
        selected = days[0].date
    else:
        selected = first.isoformat()

    return m.CalendarMonth(
        surface_id=sid,
        month=prefix,
        label=first.strftime("%B %Y"),
        today=today.isoformat(),
        first_weekday=first.weekday(),
        days_in_month=pycal.monthrange(first.year, first.month)[1],
        days=days,
        selected=selected,
    )


@app.get(f"{V1}/surfaces/{{sid}}/calendar/{{date}}", response_model=m.DayAgenda)
def get_calendar_day(sid: str, date: str):
    """Everything on one day, all-day entries first, then by clock."""
    _surface(sid)
    try:
        d = datetime.date.fromisoformat(date)
    except ValueError:
        raise HTTPException(422, "date must be YYYY-MM-DD")
    events = sorted((e for e in _events(sid) if e["date"] == date), key=lambda e: e["start_minute"])
    return m.DayAgenda(
        surface_id=sid,
        date=date,
        label=f"{d.strftime('%A')} {d.day} {d.strftime('%B')}",
        events=events,
        note=None if events else data.EMPTY_DAY,
    )


@app.get(f"{V1}/surfaces/{{sid}}/knowledge", response_model=m.FactList)
def get_knowledge(
    sid: str,
    period: m.Period | None = None,
    date: str | None = Query(None, description="YYYY-MM-DD; overrides period"),
):
    _surface(sid)
    facts = [f for f in data.FACTS if f["surface_id"] == sid and not f.get("removed")]
    if date:
        try:
            d = datetime.date.fromisoformat(date)
        except ValueError:
            raise HTTPException(422, "date must be YYYY-MM-DD")
        start = int(
            datetime.datetime.combine(d, datetime.time.min).timestamp()
        )
        facts = [f for f in facts if start <= f["ts"] < start + data.DAY]
    elif period:
        facts = [f for f in facts if f["period"] == period]
    return m.FactList(facts=facts)


@app.get(f"{V1}/surfaces/{{sid}}/conversation", response_model=m.Reply)
def get_conversation(sid: str):
    """The beats Allya opens with on this surface."""
    _surface(sid)
    return m.Reply(**data.CONVERSATIONS[sid]["opening"])


@app.post(f"{V1}/surfaces/{{sid}}/conversation/messages", response_model=m.Reply)
def post_message(sid: str, body: m.MessageIn):
    _surface(sid)
    convo = data.CONVERSATIONS[sid]
    text = body.text.lower()
    for keywords, reply in convo["scripts"]:
        if any(k in text for k in keywords):
            return m.Reply(**reply)
    return m.Reply(**convo["fallback"])


@app.get(f"{V1}/surfaces/{{sid}}/onboarding", response_model=m.ServiceOnboarding)
def get_service_onboarding(sid: str):
    """The four questions that make this floor usable."""
    _surface(sid)
    spec = data.SERVICE_ONBOARDING.get(sid)
    if not spec:
        raise HTTPException(404, f"'{sid}' has no onboarding of its own")
    return m.ServiceOnboarding(
        surface_id=sid,
        label=data.SURFACES[sid]["label"],
        status="complete" if data.ONBOARDED.get(sid) else "new",
        **spec,
    )


@app.post(f"{V1}/surfaces/{{sid}}/onboarding", response_model=m.OnboardingResult)
def complete_service_onboarding(sid: str, body: m.AnswersIn):
    _surface(sid)
    spec = data.SERVICE_ONBOARDING.get(sid)
    if not spec:
        raise HTTPException(404, f"'{sid}' has no onboarding of its own")
    missing = [q["key"] for q in spec["questions"] if not body.answers.get(q["key"], "").strip()]
    if missing:
        raise HTTPException(422, f"still unanswered: {', '.join(missing)}")
    data.ANSWERS[sid] = body.answers
    data.ONBOARDED[sid] = True
    return m.OnboardingResult(
        surface_id=sid,
        status="complete",
        learned=[q["learned"] for q in spec["questions"]],
    )


@app.get(f"{V1}/surfaces/{{sid}}/instrument", response_model=m.Instrument)
def get_instrument(sid: str):
    """The floor's own geometry — where a thing sits is the information."""
    _surface(sid)
    inst = data.INSTRUMENTS.get(sid)
    if not inst:
        raise HTTPException(404, f"'{sid}' has no instrument")
    return m.Instrument(surface_id=sid, **inst)


def _direction(did: str) -> dict:
    page = data.DIRECTIONS.get(did)
    if not page:
        raise HTTPException(404, f"no direction '{did}'")
    return page


@app.get(f"{V1}/directions/{{did}}", response_model=m.EmailPage)
def get_direction(did: str):
    """One job inside a floor, at the depth a founder works at. Email and
    WhatsApp are the same shape with their own words, health and limits."""
    return m.EmailPage(**_direction(did))


# ---- a direction's campaigns -------------------------------------------

@app.get(f"{V1}/directions/{{did}}/campaigns", response_model=list[m.Send])
def list_campaigns(did: str):
    """Every campaign on this channel, newest intent first. The page splits
    them into active and past by `state` — that's a rendering decision, not
    two collections."""
    return [m.Send(**c) for c in _direction(did)["campaigns"]]


@app.get(f"{V1}/directions/{{did}}/campaigns/{{cid}}", response_model=m.Campaign)
def get_campaign(did: str, cid: str):
    """One campaign, opened: what it said as well as what it did."""
    page = _direction(did)
    for c in page["campaigns"]:
        if c["id"] == cid:
            return m.Campaign(**data.campaign_detail(page, c))
    raise HTTPException(404, f"no campaign '{cid}'")


@app.post(f"{V1}/directions/{{did}}/campaigns/draft", response_model=m.Draft)
def draft_campaign(did: str, answers: m.Answers):
    """Write the campaign. This is the one piece of real business logic on
    this page — replace this body with a generator and nothing on the
    frontend has to move."""
    return data.compose(_direction(did), answers.model_dump())


@app.post(f"{V1}/directions/{{did}}/campaigns", response_model=m.Send, status_code=201)
def create_campaign(did: str, answers: m.Answers, subject: str | None = None):
    """Queue a campaign for review. In-memory: it joins the list the pane
    reads, in the state a thing waiting on a human should be."""
    page = _direction(did)
    draft = data.compose(page, answers.model_dump())
    return m.Send(**data.add_campaign(page, draft, subject))


@app.get(f"{V1}/directions/{{did}}/questions", response_model=list[m.Question])
def list_questions(did: str):
    """The interview. Options quote live numbers, so they're built here
    rather than stitched together in the client."""
    return [m.Question(**q) for q in data.questions_for(_direction(did))]


@app.post(f"{V1}/directions/{{did}}/questions/{{key}}/ack", response_model=m.Ack)
def ack_answer(did: str, key: str, answer: m.Ack):
    """What Allya says back when an answer lands — hers to say, not the
    client's to invent."""
    _direction(did)
    return m.Ack(text=data.ack_for(key, answer.text))


@app.get(f"{V1}/directions/{{did}}/ideas", response_model=list[m.Idea])
def list_ideas(did: str):
    """The thoughts on this channel's brain: what runs, what's drafted, and
    what nobody has started."""
    return [m.Idea(**i) for i in data.ideas_for(_direction(did))]


@app.get(f"{V1}/directions/{{did}}/work", response_model=list[m.WorkItem])
def direction_work(did: str):
    """The work items that belong to this channel — which the channel
    decides, not a regular expression in the browser."""
    page = _direction(did)
    ids = set(page["work_ids"])
    return [m.WorkItem(**w) for w in data.WORK if w["id"] in ids]


# ---- work actions ------------------------------------------------------

@app.get(f"{V1}/work/{{wid}}/review", response_model=m.Review)
def get_review(wid: str):
    _work(wid)
    review = data.REVIEWS.get(wid)
    if not review:
        raise HTTPException(404, f"no review sheet for '{wid}'")
    return m.Review(work_id=wid, **review)


@app.post(f"{V1}/work/{{wid}}/approve", response_model=m.WorkAction)
def approve_work(wid: str):
    w = _work(wid)
    if w["status"] == "shipped":
        raise HTTPException(409, f"'{wid}' has already shipped")
    out = data.OUTCOMES.get(wid, {})
    w["status"] = "shipped"
    w["undoable"] = True
    w["title"] = out.get("title", w.get("title") or "Approved")
    w["meta"] = out.get("meta", "just now")
    w["say"] = None
    return m.WorkAction(
        item=w,
        toast=out.get("toast", "Approved."),
        reply=_reply(out.get("reply", "Done — it’s moving."), f"{wid}-approved"),
    )


@app.post(f"{V1}/work/{{wid}}/undo", response_model=m.WorkAction)
def undo_work(wid: str):
    w = _work(wid)
    if w["status"] != "shipped":
        raise HTTPException(409, f"'{wid}' is not shipped, nothing to undo")
    seed = data.WORK_SEED[wid]
    w.update({k: seed.get(k) for k in ("title", "meta", "say", "who", "who_name", "who_role")})
    w["status"] = seed["status"]
    w["undoable"] = False
    return m.WorkAction(item=w, toast="Held. Nothing went out.", reply=_reply(data.UNDO_REPLY, f"{wid}-undone"))


@app.post(f"{V1}/work/{{wid}}/revision", response_model=m.Reply)
def request_revision(wid: str):
    """"Ask for a change" — the item stays put, Allya answers."""
    _work(wid)
    return _reply(data.REVISION_REPLY, f"{wid}-revision")


# ---- knowledge ---------------------------------------------------------

@app.patch(f"{V1}/knowledge/{{fid}}", response_model=m.Fact)
def patch_fact(fid: str, body: m.FactPatch):
    f = _fact(fid)
    if body.flagged is not None:
        f["flagged"] = body.flagged
    if body.text is not None:
        f.update({"text": body.text, "flagged": False, "mismatch": False, "source": "corrected"})
    return m.Fact(**f)


# ---- the gate ----------------------------------------------------------

def _bearer(authorization: Optional[str]) -> dict:
    """The signed-in user, or 401. No expiry, no refresh — a dummy session."""
    token = (authorization or "").removeprefix("Bearer ").strip()
    email = data.TOKENS.get(token)
    if not email:
        raise HTTPException(401, "Not signed in")
    return data.USERS[email]


@app.get(f"{V1}/gate", response_model=m.Gate)
def get_gate():
    """Everything the sign-in page renders, graph included."""
    return m.Gate(**data.GATE)


@app.post(f"{V1}/session", response_model=m.Session, status_code=201)
def sign_in(body: m.Credentials):
    user = data.USERS.get(body.email.strip().lower())
    if not user or body.password != data.DEMO_PASSWORD:
        # one message for both cases — never reveal which half was wrong
        raise HTTPException(401, "That email and password don’t match an account.")
    token = secrets.token_urlsafe(24)
    data.TOKENS[token] = user["email"]
    return m.Session(token=token, user=user)


@app.get(f"{V1}/session", response_model=m.User)
def whoami(authorization: Annotated[Optional[str], Header()] = None):
    return m.User(**_bearer(authorization))


@app.delete(f"{V1}/session", status_code=204)
def sign_out(authorization: Annotated[Optional[str], Header()] = None):
    token = (authorization or "").removeprefix("Bearer ").strip()
    data.TOKENS.pop(token, None)  # signing out twice is not an error
    return Response(status_code=204)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
