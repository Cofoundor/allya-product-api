"""Dummy API for the Allya product brain surfaces.

It exists to pin down the contract, nothing more: in-memory state, static
seeds, no auth, no database. Replace the bodies with real logic and the
frontend should not need to change.

    uvicorn main:app --reload --port 8000
"""

import os

from fastapi import FastAPI, HTTPException, Query
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
    return m.Surface(**_surface(sid))


@app.get(f"{V1}/surfaces/{{sid}}/brain", response_model=m.BrainGraph)
def get_brain(sid: str):
    _surface(sid)
    return m.BrainGraph(**data.BRAINS[sid])


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


@app.get(f"{V1}/surfaces/{{sid}}/knowledge", response_model=m.FactList)
def get_knowledge(
    sid: str,
    period: m.Period | None = None,
    date: str | None = Query(None, description="YYYY-MM-DD; overrides period"),
):
    _surface(sid)
    facts = [f for f in data.FACTS if f["surface_id"] == sid and not f.get("removed")]
    if date:
        import datetime

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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
