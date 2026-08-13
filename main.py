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

import crm_query as q
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
    """The floor's own geometry — where a thing sits is the information.

    Sales, hiring and PR read theirs off the people book: the funnel, the
    ladder and the radar were always views of a person at a stage, so their
    numbers derive rather than being typed out. Marketing's timeline is left
    alone — it's about work, not people."""
    _surface(sid)
    live = q.instrument_for(sid)
    if live:
        return m.Instrument(**live)
    inst = data.INSTRUMENTS.get(sid)
    if not inst:
        raise HTTPException(404, f"'{sid}' has no instrument")
    return m.Instrument(surface_id=sid, **inst)


@app.get(f"{V1}/directions", response_model=list[m.DirectionSummary])
def list_directions():
    """Which directions are rooms rather than panels, and where they live.
    The floor's brain needs this to know which dots it can fly into."""
    out = [
        m.DirectionSummary(id=d["id"], label=d["label"], href=d["ui"]["floor_href"] + "/" + d["id"],
                           surface_id=d["surface_id"])
        for d in data.DIRECTIONS.values()
    ]
    # the people layer is the one room that isn't inside the floor it hangs
    # off: sales is the door, but the book behind it belongs to everyone
    out.append(m.DirectionSummary(id="crm", label="Pipeline", href="/people", surface_id="sales"))
    return out


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


# ---- the people layer --------------------------------------------------
#
# One book, read by every floor. A journalist, a candidate and a lead are the
# same record with a different kind — which is what lets PR, hiring and sales
# stop keeping three lists of the same humans.
#
# Nothing here stores a count. Stage totals and segment sizes are computed on
# every read, because a stored number that drifts from the people under it is
# worse than no number.

def _person(pid: str) -> dict:
    p = q.person(pid)
    if not p:
        raise HTTPException(404, f"unknown person '{pid}'")
    return p


def _out(p: dict) -> m.Person:
    return m.Person(**p)


@app.get(f"{V1}/crm", response_model=m.CrmPage)
def get_crm():
    """The layer, dressed. Same shape as a channel page on purpose — the
    studio shell reads both without knowing which it has."""
    return m.CrmPage(
        id="crm",
        label="People",
        blurb=data.CRM_BLURB,
        stats=[m.Stat(**s) for s in q.crm_stats()],
        progress=m.Progress(**q.crm_progress()),
        awaiting="leads",
        pipelines=[m.Pipeline(**p) for p in q.pipelines_out()],
        segments=[m.Segment(**q.segment_out(s)) for s in data.SEGMENTS],
        sources=[m.Source(**s) for s in q.sources_out()],
        notes=data.CRM_NOTES,
        nouns=m.Nouns(**data.CRM_NOUNS),
        ui=m.ChannelUi(**data.CRM_UI),
    )


@app.get(f"{V1}/crm/people", response_model=m.PersonList)
def list_people(
    kind: Optional[str] = None,
    stage: Optional[str] = None,
    segment: Optional[str] = None,
    pipeline: Optional[str] = None,
    warmth: Optional[str] = None,
    tag: Optional[str] = None,
    company: Optional[str] = None,
    source: Optional[str] = None,
    owes: bool = False,
    q_: Annotated[Optional[str], Query(alias="q")] = None,
    limit: int = Query(60, ge=1, le=500),
    cursor: Optional[str] = None,
):
    """Everyone, narrowed. Overdue first, then what's owed, then warm — a
    queue outranks a temperature, and neither is alphabetical."""
    rows = q.filter_people(kind=kind, stage=stage, seg_id=segment, pipeline=pipeline,
                           q=q_, warmth=warmth, tag=tag, company_id=company,
                           source=source, owes=owes)
    start = 0
    if cursor:
        ids = [p["id"] for p in rows]
        start = ids.index(cursor) + 1 if cursor in ids else 0
    page = rows[start:start + limit]
    nxt = page[-1]["id"] if start + limit < len(rows) and page else None
    return m.PersonList(
        # joined for the grid: a column needs a company's name and what's on
        # the table, and a request per row is not an answer
        people=[m.PersonRow(**q.row_out(p)) for p in page],
        total=len(rows),
        cursor=nxt,
        caption=q.caption_for(len(rows), stage=stage, seg_id=segment, kind=kind, q=q_),
    )


@app.post(f"{V1}/crm/people", response_model=m.Person, status_code=201)
def create_person(body: m.PersonIn):
    """Added by hand. The most ordinary way a person gets here, and the one a
    founder reaches for when a name arrives in a DM."""
    co = None
    if body.company:
        hit = next((c for c in data.COMPANIES if c["name"].lower() == body.company.lower()), None)
        co = hit["id"] if hit else None
    kind = body.kinds[0] if body.kinds else "prospect"
    p = q.new_person(body.name, kind, email=body.email, phone=body.phone, handle=body.handle,
                     company_id=co, stage_id=body.stage_id, source="manual", owner="you",
                     note=body.note)
    if len(body.kinds) > 1:
        p["kinds"] = list(body.kinds)
    q.add_touch(p["id"], "note", "you", "You added them", surface_id="sales")
    return _out(p)


@app.get(f"{V1}/crm/people/{{pid}}", response_model=m.PersonDetail)
def get_person(pid: str):
    """One person, opened: who they're with, what's on the table, and the
    whole trail behind them."""
    p = _person(pid)
    co = q.company(p["company_id"]) if p.get("company_id") else None
    return m.PersonDetail(
        **p,
        company=m.Company(**co) if co else None,
        deals=[m.Deal(**d) for d in q.deals_for(pid)],
        touches=[m.Touch(**t) for t in q.touches_for(pid)[:40]],
        segments=q.segments_for(p),
        facts=[f["text"] for f in data.FACTS if p["id"] in (f.get("person_id") or "")],
        next=[m.Move(**mv) for mv in q.next_moves(p)],
        attribution=m.Attribution(**q.attribution_for(p)),
        followups=[m.Followup(**f) for f in q.followups_for(pid)],
    )


@app.post(f"{V1}/crm/people/{{pid}}/moves/{{mid}}", response_model=m.MoveResult, status_code=201)
def take_move(pid: str, mid: str, body: m.MoveIn):
    """Take a move.

    This is the hinge. An agent or an expert gets a real work item that lands
    in the work list and comes back for approval; keeping it gets you a
    follow-up with a date that can go overdue. Before this existed the people
    layer read from every floor and wrote to none of them, which is the
    difference between a CRM and a page describing one."""
    p = _person(pid)
    try:
        res = q.take_move(p, mid, body.by, body.due)
    except KeyError:
        raise HTTPException(404, f"no move '{mid}'")
    except ValueError as e:
        raise HTTPException(422, str(e))
    return m.MoveResult(
        work=m.WorkItem(**res["work"]) if res["work"] else None,
        followup=m.Followup(**res["followup"]) if res["followup"] else None,
        touch=m.Touch(**res["touch"]),
        toast=res["toast"],
    )


@app.get(f"{V1}/crm/today", response_model=list[m.Prompt])
def get_today():
    """The shortest honest answer to "what do I do now?".

    Everything else on this layer is a way of looking; this is a way of
    deciding. Capped at three on purpose — a founder handed twenty
    priorities has been handed none."""
    return [m.Prompt(**p) for p in q.today()]


@app.get(f"{V1}/crm/followups", response_model=list[m.Followup])
def list_followups():
    """Today's list: late first, then due today, then what's coming."""
    return [m.Followup(**f) for f in q.queue()]


@app.post(f"{V1}/crm/people/{{pid}}/followups", response_model=m.Followup, status_code=201)
def add_followup(pid: str, body: m.FollowupIn):
    """Commit yourself to something, by a date. The one thing an agent can't
    do for you is decide you'll call someone Thursday."""
    _person(pid)
    return m.Followup(**q.new_followup(pid, body.what, body.due, body.by))


@app.patch(f"{V1}/crm/followups/{{fid}}", response_model=m.Followup)
def patch_followup(fid: str, body: m.FollowupPatch):
    """Done with it, or push it. Pushing keeps it open on purpose — a
    follow-up you can silently dismiss is one that never chases you."""
    f = q.followup(fid)
    if not f:
        raise HTTPException(404, f"unknown follow-up '{fid}'")
    return m.Followup(**q.patch_followup(f, body.state, body.due))


@app.get(f"{V1}/crm/origins", response_model=list[m.OriginStat])
def list_origins():
    """Every door in, ranked by what actually gets anywhere. "Where are the
    leads coming from" was never really a question about counts — the
    channel that brings the most is routinely not the one that converts."""
    return [m.OriginStat(**o) for o in q.origins_out()]


@app.patch(f"{V1}/crm/people/{{pid}}", response_model=m.Person)
def patch_person(pid: str, body: m.PersonPatch):
    p = _person(pid)
    for field in ("name", "email", "phone", "handle", "kinds", "tags", "note"):
        val = getattr(body, field)
        if val is not None:
            p[field] = val
    return _out(p)


@app.get(f"{V1}/crm/people/{{pid}}/journey", response_model=m.Journey)
def get_journey(pid: str):
    """Everything that ever happened to one person, in one place. This is the
    whole point of the layer — marketing's sends, sales' calls, PR's pitches
    and ops' payments on one trail, each still saying who did it."""
    p = _person(pid)
    return m.Journey(
        person_id=pid,
        name=p["name"],
        touches=[m.Touch(**t) for t in q.touches_for(pid)],
        stages=[m.StageChange(**s) for s in q.stage_changes(pid)],
        opened=p.get("created") or "",
        note=p.get("note") or "",
    )


@app.post(f"{V1}/crm/people/{{pid}}/touches", response_model=m.Touch, status_code=201)
def log_touch(pid: str, body: m.TouchIn):
    """A call you made, a note you took. The founder's own moves belong on the
    same trail as the agent's, in the same grammar."""
    _person(pid)
    return m.Touch(**q.add_touch(pid, body.kind, body.by, body.text, surface_id="sales"))


@app.post(f"{V1}/crm/people/{{pid}}/stage", response_model=m.PersonDetail)
def set_stage(pid: str, body: m.StageIn):
    """Move someone. Writes a touch, so the move is part of the journey rather
    than a silent edit to a field."""
    p = _person(pid)
    stages = {s["id"] for s in data.PIPELINE_BY_ID[p["pipeline_id"]]["stages"]}
    if body.stage_id not in stages:
        raise HTTPException(422, f"'{body.stage_id}' isn't a stage on the {p['pipeline_id']} pipeline")
    if body.stage_id == p["stage_id"]:
        raise HTTPException(409, "They're already there")
    q.move_stage(p, body.stage_id, "you", body.note)
    return get_person(pid)


@app.get(f"{V1}/crm/companies", response_model=list[m.Company])
def list_companies():
    """Accounts, with their people counted now rather than stored."""
    return [m.Company(**{**c, "people_count": len(q.filter_people(company_id=c["id"]))})
            for c in data.COMPANIES]


@app.get(f"{V1}/crm/companies/{{cid}}", response_model=m.Company)
def get_company(cid: str):
    c = q.company(cid)
    if not c:
        raise HTTPException(404, f"unknown company '{cid}'")
    return m.Company(**{**c, "people_count": len(q.filter_people(company_id=cid))})


@app.get(f"{V1}/crm/companies/{{cid}}/people", response_model=list[m.Person])
def company_people(cid: str):
    if not q.company(cid):
        raise HTTPException(404, f"unknown company '{cid}'")
    return [_out(p) for p in q.filter_people(company_id=cid)]


@app.get(f"{V1}/crm/deals", response_model=list[m.Deal])
def list_deals(state: Optional[str] = None, stage: Optional[str] = None):
    """What's actually on the table. Drawn as a band on the money funnel, not
    as a card on a board — four deals don't need a Kanban."""
    rows = data.DEALS
    if state:
        rows = [d for d in rows if d["state"] == state]
    if stage:
        rows = [d for d in rows if d["stage_id"] == stage]
    return [m.Deal(**d) for d in rows]


@app.get(f"{V1}/crm/deals/{{did}}", response_model=m.Deal)
def get_deal(did: str):
    d = q.deal(did)
    if not d:
        raise HTTPException(404, f"unknown deal '{did}'")
    return m.Deal(**d)


@app.post(f"{V1}/crm/deals", response_model=m.Deal, status_code=201)
def create_deal(body: m.DealIn):
    if body.person_id:
        _person(body.person_id)
    return m.Deal(**q.new_deal(body.title, body.value, person_id=body.person_id,
                               company_id=body.company_id, stage_id=body.stage_id,
                               expected_close=body.expected_close, note=body.note))


@app.patch(f"{V1}/crm/deals/{{did}}", response_model=m.Deal)
def patch_deal(did: str, body: m.DealPatch):
    """Advance, win or lose one. Winning moves the person to paying too — the
    two were never separate facts."""
    d = q.deal(did)
    if not d:
        raise HTTPException(404, f"unknown deal '{did}'")
    for field in ("stage_id", "state", "value", "expected_close", "note"):
        val = getattr(body, field)
        if val is not None:
            d[field] = val
    if body.state == "won":
        d["stage_id"] = "d-won"
        p = q.person(d.get("person_id") or "")
        if p and p["stage_id"] != "paying":
            q.move_stage(p, "paying", "you", f"Won — {d['title']}")
    if body.state == "lost":
        p = q.person(d.get("person_id") or "")
        if p:
            q.add_touch(p["id"], "note", "you", f"Lost — {d['title']}", surface_id="sales")
    return m.Deal(**d)


@app.get(f"{V1}/crm/pipelines", response_model=list[m.Pipeline])
def list_pipelines(source: Optional[str] = None):
    """The funnel, the money, the ladder, the raise and the press list. Same
    object five times, which is what lets one page draw all of them.

    `source` narrows every one of them to a single door in — the only way to
    see that the channel filling the top isn't filling the bottom."""
    return [m.Pipeline(**p) for p in q.pipelines_out(source)]


@app.get(f"{V1}/crm/pipelines/{{plid}}", response_model=m.Pipeline)
def get_pipeline(plid: str, source: Optional[str] = None):
    pl = data.PIPELINE_BY_ID.get(plid)
    if not pl:
        raise HTTPException(404, f"unknown pipeline '{plid}'")
    return m.Pipeline(**q.pipeline_out(pl, source))


@app.get(f"{V1}/crm/segments", response_model=list[m.Segment])
def list_segments():
    """What `audience` used to be a sentence about. Counts are live, so a
    campaign written against one knows how many it's going to."""
    return [m.Segment(**q.segment_out(s)) for s in data.SEGMENTS]


@app.get(f"{V1}/crm/segments/{{sid}}", response_model=m.Segment)
def get_segment(sid: str):
    s = q.segment(sid)
    if not s:
        raise HTTPException(404, f"unknown segment '{sid}'")
    return m.Segment(**q.segment_out(s))


@app.get(f"{V1}/crm/segments/{{sid}}/people", response_model=m.PersonList)
def segment_people(sid: str):
    s = q.segment(sid)
    if not s:
        raise HTTPException(404, f"unknown segment '{sid}'")
    rows = q.segment_people(s)
    return m.PersonList(people=[_out(p) for p in rows], total=len(rows),
                        caption=f"{len(rows)} · {s['label'].lower()}")


@app.post(f"{V1}/crm/segments", response_model=m.Segment, status_code=201)
def create_segment(body: m.SegmentIn):
    s = q.new_segment(body.label, body.rule.model_dump(), body.note)
    return m.Segment(**q.segment_out(s))


@app.post(f"{V1}/crm/import/preview", response_model=m.ImportPreview)
def preview_import(body: m.ImportIn):
    """What the file would do, before it does it. Nothing is stored by this
    call — the mapping is a guess the founder gets to see and correct."""
    return m.ImportPreview(**q.import_preview(body.csv, body.mapping, body.kind))


@app.post(f"{V1}/crm/import", response_model=m.ImportResult, status_code=201)
def run_import(body: m.ImportIn):
    """Commit it. Duplicates get merged onto the record that's already here,
    never doubled — that's the whole reason the cleanup work item exists."""
    return m.ImportResult(**q.do_import(body.csv, body.mapping, body.kind,
                                        body.on_duplicate, body.segment_label))


@app.post(f"{V1}/crm/ingest", response_model=m.IngestResult, status_code=202)
def ingest(body: m.IngestIn):
    """One event from somewhere else — a signup, a payment, an open, a reply.
    Resolved by email, then phone, then handle; a miss makes a person, because
    a touch with nobody to hang on is a touch we lose."""
    return m.IngestResult(**q.ingest(body.model_dump()))


@app.get(f"{V1}/crm/table", response_model=m.TableSpec)
def get_crm_table():
    """What the grid can show, and the named sets a founder picks between.

    The client holds no column list of its own: it renders by `key`, so a
    column added to TABLE_COLUMNS appears in the table with no frontend
    change. Widths aren't here on purpose — that's a screen decision."""
    return m.TableSpec(
        columns=[m.TableColumn(**c) for c in data.TABLE_COLUMNS],
        presets=[m.TablePreset(**p) for p in data.TABLE_PRESETS],
        groups=data.TABLE_GROUPS,
    )


@app.get(f"{V1}/crm/lexicon", response_model=m.Lexicon)
def get_lexicon():
    """The words this interface puts on the API's enums.

    Read once and cached. It exists because the alternative — a constant in
    every component that needs a word — had the warmth vocabulary spelled
    three different ways on three different screens."""
    return m.Lexicon(
        warmth=[m.WarmthWord(**w) for w in data.LEXICON["warmth"]],
        touch_kinds=data.LEXICON["touch_kinds"],
        urgency=data.LEXICON["urgency"],
        dispatch=[m.DispatchWord(**d) for d in data.LEXICON["dispatch"]],
        experts=data.LEXICON["experts"],
    )


@app.get(f"{V1}/crm/sources", response_model=list[m.Source])
def list_sources():
    """Where the people come from, and when each last brought any."""
    return [m.Source(**s) for s in q.sources_out()]


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
