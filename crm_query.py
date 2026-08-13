"""How the people book is read.

Everything in here derives. No count is stored: the moment a stored number and
the people disagree, the funnel is decoration. `crm_data` is the book; this is
the only place that counts, filters, resolves or moves anything in it.
"""

import csv as _csv
import datetime as _dt
import io as _io
import math as _math
import time

from crm_data import (
    COMPANIES,
    DAY,
    _MIDNIGHT,
    DEALS,
    DOTS,
    ORIGINS,
    PEOPLE,
    PIPELINE_BY_ID,
    PIPELINES,
    SEGMENTS,
    SOURCES,
    STAGE_LABEL,
    TODAY,
    TOUCHES,
    days_since,
    warmth_of,
)

_pseq = 0
_tseq = 1000
_dseq = 0
_sseq = 0


# ---- reading -----------------------------------------------------------

def person(pid: str):
    for p in PEOPLE:
        if p["id"] == pid:
            return p
    return None


def company(cid: str):
    for c in COMPANIES:
        if c["id"] == cid:
            return c
    return None


def deal(did: str):
    for d in DEALS:
        if d["id"] == did:
            return d
    return None


def touches_for(pid: str) -> list[dict]:
    """Newest first — a journey is read from what just happened, backwards."""
    return sorted([t for t in TOUCHES if t["person_id"] == pid], key=lambda t: -t["at"])


def deals_for(pid: str) -> list[dict]:
    return [d for d in DEALS if d.get("person_id") == pid]


def stage_changes(pid: str) -> list[dict]:
    out, prev = [], None
    for t in sorted([t for t in TOUCHES if t["person_id"] == pid], key=lambda t: t["at"]):
        if t["kind"] != "stage":
            continue
        out.append({"at": t["at"], "from_id": prev, "to_id": _to_stage(t["text"]),
                    "by": t["by"], "note": t["text"]})
        prev = out[-1]["to_id"]
    return out


_STAGE_BY_LABEL = {v.lower(): k for k, v in STAGE_LABEL.items()}


def _to_stage(text: str):
    for label, sid in _STAGE_BY_LABEL.items():
        if label in text.lower():
            return sid
    return ""


def matches(p: dict, rule: dict) -> bool:
    """An empty list means "don't narrow on this", so an all-empty rule is
    everyone. That's what lets a half-built segment show a real count while
    the founder is still building it."""
    # a hand-picked list is exactly who you chose, and nothing else narrows it
    if rule.get("person_ids"):
        return p["id"] in rule["person_ids"]
    if rule.get("kinds") and not set(rule["kinds"]) & set(p.get("kinds", [])):
        return False
    if rule.get("stage_ids") and p["stage_id"] not in rule["stage_ids"]:
        return False
    if rule.get("warmth") and p["warmth"] not in rule["warmth"]:
        return False
    if rule.get("tags") and not set(rule["tags"]) & set(p.get("tags", [])):
        return False
    if rule.get("sources") and p.get("source") not in rule["sources"]:
        return False
    if rule.get("not_touched_days") is not None and days_since(p) < rule["not_touched_days"]:
        return False
    if rule.get("touched_kind") or rule.get("never_kind"):
        kinds = {t["kind"] for t in TOUCHES if t["person_id"] == p["id"]}
        if rule.get("touched_kind") and rule["touched_kind"] not in kinds:
            return False
        if rule.get("never_kind") and rule["never_kind"] in kinds:
            return False
    return True


def segment(sid: str):
    for s in SEGMENTS:
        if s["id"] == sid:
            return s
    return None


def segment_people(seg: dict) -> list[dict]:
    return [p for p in PEOPLE if matches(p, seg["rule"])]


def segment_out(seg: dict) -> dict:
    """A segment on the wire always carries a live count."""
    return {**seg, "count": len(segment_people(seg))}


def segments_for(p: dict) -> list[str]:
    return [s["label"] for s in SEGMENTS if matches(p, s["rule"])]


def pipeline_out(pl: dict, source: str | None = None) -> dict:
    """Stage counts, computed now.

    `source` narrows the whole funnel to one door in — which is the only way
    to find out that the channel filling the top isn't the one filling the
    bottom. The deals pipeline also carries the money still open, because a
    funnel measured in ₹ has to say how much."""
    counts = {s["id"]: 0 for s in pl["stages"]}
    if pl["id"] == "deals":
        value = 0
        for d in DEALS:
            if d["pipeline_id"] != "deals":
                continue
            if source:
                owner = person(d.get("person_id") or "")
                if not owner or owner.get("origin_channel") != source:
                    continue
            counts[d["stage_id"]] = counts.get(d["stage_id"], 0) + 1
            if d["state"] == "open":
                value += d["value"]
        return {**pl, "counts": counts, "value": value}
    for p in PEOPLE:
        if p["pipeline_id"] != pl["id"]:
            continue
        if source and p.get("origin_channel") != source:
            continue
        counts[p["stage_id"]] = counts.get(p["stage_id"], 0) + 1
    return {**pl, "counts": counts, "value": None}


def pipelines_out(source: str | None = None) -> list[dict]:
    return [pipeline_out(p, source) for p in PIPELINES]


def origins_out() -> list[dict]:
    """Every door in, with how many came through it and how many of those
    got anywhere. This is the answer to "where are the leads coming from" —
    a count on its own was never the question."""
    life = [p for p in PEOPLE if p["pipeline_id"] == "lifecycle"]
    out = []
    for channel, said in ORIGINS + [("csv", "An old list you uploaded")]:
        grp = [p for p in life if p.get("origin_channel") == channel]
        if not grp:
            continue
        worth = len([p for p in grp if p["stage_id"] in ("worth-a-call", "paying")])
        paying = len([p for p in grp if p["stage_id"] == "paying"])
        out.append({
            "id": channel, "said": said, "count": len(grp),
            "worth": worth, "paying": paying,
            # the number a founder actually decides on
            "rate": round(worth / len(grp), 3) if grp else 0.0,
        })
    return sorted(out, key=lambda o: -o["rate"])


_RANK = {"warm": 0, "cooling": 1, "cold": 2, "never": 3}


def filter_people(kind=None, stage=None, seg_id=None, pipeline=None, q=None,
                  warmth=None, tag=None, company_id=None, source=None, owes=False) -> list[dict]:
    out = list(PEOPLE)
    if source:
        out = [p for p in out if p.get("origin_channel") == source]
    if owes:
        # only the people something is actually owed to
        out = [p for p in out if p.get("next_step")]
    if seg_id:
        s = segment(seg_id)
        out = [p for p in out if s and matches(p, s["rule"])]
    if kind:
        out = [p for p in out if kind in p.get("kinds", [])]
    if pipeline:
        out = [p for p in out if p["pipeline_id"] == pipeline]
    if stage:
        out = [p for p in out if p["stage_id"] == stage]
    if warmth:
        out = [p for p in out if p["warmth"] == warmth]
    if tag:
        out = [p for p in out if tag in p.get("tags", [])]
    if company_id:
        out = [p for p in out if p.get("company_id") == company_id]
    if q:
        n = q.strip().lower()
        out = [p for p in out
               if n in p["name"].lower() or n in (p.get("email") or "").lower()
               or n in (p.get("note") or "").lower()]
    # Owed first, and the latest of those first of all — a queue outranks a
    # temperature. Then warm, then most recently touched.
    return sorted(out, key=lambda p: (
        0 if p.get("overdue") else 1 if p.get("next_step") else 2,
        p.get("next_due") or "9999",
        _RANK.get(p["warmth"], 4),
        -(p.get("last_touch_at") or 0),
    ))


# ---- what they appear to want --------------------------------------------
#
# A stage says how far along someone is. It doesn't say what they're after,
# and those are different questions: two people in "Worth a call" can want
# opposite things, and the opener you write them is not the same.
#
# This is an inference, so it never travels alone — `intent_why` carries the
# evidence that produced it, and the grid shows the two together. A read a
# founder can't check is a read they shouldn't trust.

def intent_of(p: dict, touches: list[dict], co: dict | None) -> tuple[str, str]:
    kinds = p.get("kinds", [])
    stage = p["stage_id"]
    tags = p.get("tags", [])
    origin = (p.get("origin_said") or "").lower()
    said = " ".join(t["text"].lower() for t in touches)

    if "journalist" in kinds:
        if stage in ("replied", "covered"):
            return "Wants a story worth running", "They've written back at least once"
        return "Nothing yet — a name on the list", "No reply to anything so far"

    if "candidate" in kinds:
        return ("Wants the job",
                f"Applied{' and cleared the screen' if stage in ('screened', 'your-call') else ''}")

    if "investor" in kinds:
        return "Sizing up the round", "Warm intro, then the deck"

    if stage == "churned":
        back = "opened the win-back note" if "win-back" in said else "hasn't opened the win-back note"
        return "Gone — needs a reason to return", f"Cancelled, and {back}"

    if "agency-refugee" in tags:
        return ("Agency output without the retainer",
                "Left an agency over its price — the same story as SurferSearcher")

    if stage == "paying":
        return "Wants the work done for them", "Paying, so the question is delivery now"

    if co and co.get("size") and not co["size"].startswith(("1 ", "2 ", "3 ")):
        return f"Needs it for a team of {co['size'].split()[0]}", f"{co['name']} is {co['size']}"

    if "pricing" in origin or "pricing" in said:
        return ("Working out what this costs",
                "Came in through the pricing page" if "pricing" in origin
                else "Has read the pricing memo")

    if stage == "worth-a-call":
        return "Has the problem, hasn't asked yet", "Enriched and mid-funnel, but hasn't written to you"

    if stage == "talking":
        return "Deciding whether it fits", "Mid-conversation — answered something"

    if stage == "signed-up":
        if not any(t["kind"] == "email" for t in touches):
            return "Unclear — nothing they've done says", "Signed up and opened nothing since"
        return "Curious, not committed", "Opened the welcome sequence, hasn't replied"

    return "Unclear — nothing they've done says", "Too little has happened to read them"


def row_out(p: dict) -> dict:
    """A person, joined to everything a column needs.

    One pass over memory rather than a request per row. Every field here is
    derived — nothing is stored twice, so a grid can never drift from the
    record it's showing."""
    deals = deals_for(p["id"])
    ts = [t for t in TOUCHES if t["person_id"] == p["id"]]
    ts.sort(key=lambda t: -t["at"])
    co = company(p["company_id"]) if p.get("company_id") else None

    # how long they've sat where they are: the last stage move, or the day
    # they arrived if nobody has moved them since
    moved = next((t["at"] for t in ts if t["kind"] == "stage"), None)
    since = moved or (ts[-1]["at"] if ts else None)
    in_stage = None
    if since:
        in_stage = max(0, round((_MIDNIGHT + DAY - since) / DAY))

    owed = followups_for(p["id"], "open")
    intent, why = intent_of(p, ts, co)
    return {
        **p,
        "company_name": co["name"] if co else "",
        "company_size": co.get("size") or "" if co else "",
        "company_industry": co.get("industry") or "" if co else "",
        "intent": intent,
        "intent_why": why,
        "open_value": sum(d["value"] for d in deals if d["state"] == "open"),
        "deal_count": len(deals),
        "segment_labels": segments_for(p),
        "touch_count": len(ts),
        "last_said": ts[0]["text"] if ts else "",
        "days_in_stage": in_stage,
        "next_by": owed[0]["by"] if owed else None,
    }


def caption_for(total, stage=None, seg_id=None, kind=None, q=None) -> str:
    """What the filter narrowed to, said the way the page says it."""
    if q:
        return f"{total} matching “{q}”"
    if seg_id:
        s = segment(seg_id)
        if s:
            return f"{total} · {s['label'].lower()}"
    if stage:
        return f"{total} in {STAGE_LABEL.get(stage, stage).lower()}"
    if kind:
        return f"{total} {kind}s"
    return f"{total} people — everyone your company has touched"


# ---- writing -----------------------------------------------------------

def add_touch(pid, kind, by, text, **kw) -> dict:
    global _tseq
    _tseq += 1
    row = {
        "id": f"t{_tseq}", "person_id": pid, "at": int(time.time()), "kind": kind,
        "by": by, "text": text, "who": kw.get("who"), "channel": kw.get("channel"),
        "work_id": kw.get("work_id"), "campaign_id": kw.get("campaign_id"),
        "direction_id": kw.get("direction_id"), "surface_id": kw.get("surface_id"),
    }
    TOUCHES.append(row)
    p = person(pid)
    if p:
        p["last_touch_at"] = row["at"]
        p["warmth"] = warmth_of(p)
    return row


def move_stage(p: dict, stage_id: str, by: str = "you", note: str = "") -> dict:
    p["stage_id"] = stage_id
    label = STAGE_LABEL.get(stage_id, stage_id)
    return add_touch(p["id"], "stage", by, note or f"Moved to {label}",
                     surface_id=PIPELINE_BY_ID[p["pipeline_id"]]["surface_id"])


def new_person(name, kind="prospect", **kw) -> dict:
    global _pseq
    _pseq += 1
    pl = {"journalist": "press", "candidate": "hiring"}.get(kind, "lifecycle")
    stage = kw.get("stage_id") or {"press": "never", "hiring": "applied"}.get(pl, "signed-up")
    row = {
        "id": f"p-new{_pseq}", "name": name, "kinds": [kind],
        "email": kw.get("email"), "phone": kw.get("phone"), "handle": kw.get("handle"),
        "company_id": kw.get("company_id"), "pipeline_id": pl, "stage_id": stage,
        "warmth": "never", "source": kw.get("source", "manual"), "owner": kw.get("owner", "you"),
        "tags": list(kw.get("tags", [])), "value": None,
        "created": TODAY.isoformat(), "last_touch_at": None, "note": kw.get("note", ""),
    }
    PEOPLE.append(row)
    return row


def resolve(email=None, phone=None, handle=None):
    """Email, then phone, then handle. A miss makes a person, because a touch
    with nobody to hang on is a touch we lose."""
    for field, val in (("email", email), ("phone", phone), ("handle", handle)):
        if not val:
            continue
        v = val.strip().lower()
        for p in PEOPLE:
            if (p.get(field) or "").strip().lower() == v:
                return p
    return None


# where an arriving event puts someone, when it says anything about that
INGEST_STAGE = {
    "signup": "signed-up",
    "payment": "paying",
    "churn": "churned",
    "application": "applied",
}

INGEST_SAID = {
    "signup": "Signed up",
    "payment": "Paid — ₹2,000",
    "churn": "Cancelled",
    "email": "Opened an email",
    "whatsapp": "Read the message",
    "call": "Call logged",
    "meeting": "Met",
    "application": "Applied",
    "press": "Press touch logged",
    "note": "Noted",
    "import": "Came in on a file",
    "stage": "Moved stage",
}


def ingest(body: dict) -> dict:
    """One event from somewhere else, landed on a person."""
    hit = resolve(body.get("email"), body.get("phone"), body.get("handle"))
    created = hit is None
    if created:
        kind = "candidate" if body["kind"] == "application" else "prospect"
        name = body.get("name") or body.get("email") or body.get("phone") or "Someone new"
        hit = new_person(name, kind, email=body.get("email"), phone=body.get("phone"),
                         handle=body.get("handle"), source=body.get("source", "ingest"),
                         owner="agent", note="Arrived on their own. Nothing said yet.")
    t = add_touch(hit["id"], body["kind"], "agent",
                  body.get("text") or INGEST_SAID.get(body["kind"], "Something happened"),
                  channel=body.get("source"), campaign_id=body.get("campaign_id"))
    note = ""
    want = INGEST_STAGE.get(body["kind"])
    if want and want != hit["stage_id"] and hit["pipeline_id"] in ("lifecycle", "hiring"):
        move_stage(hit, want, "agent")
        note = f"Moved to {STAGE_LABEL.get(want, want)}"
    return {"person_id": hit["id"], "created": created, "touch_id": t["id"],
            "stage_id": hit["stage_id"], "note": note}


def new_deal(title, value, **kw) -> dict:
    global _dseq
    _dseq += 1
    row = {
        "id": f"dl-new{_dseq}", "person_id": kw.get("person_id"),
        "company_id": kw.get("company_id"), "title": title, "value": value,
        "currency": "INR", "pipeline_id": "deals",
        "stage_id": kw.get("stage_id") or "d-talking", "state": "open",
        "opened": TODAY.isoformat(), "expected_close": kw.get("expected_close"),
        "work_id": None, "note": kw.get("note", ""),
    }
    DEALS.append(row)
    if row["person_id"]:
        add_touch(row["person_id"], "note", "you", f"Opened — {title}, ₹{value:,}",
                  surface_id="sales")
    return row


def new_segment(label, rule, note="") -> dict:
    global _sseq
    _sseq += 1
    row = {"id": f"sg-new{_sseq}", "label": label, "rule": rule, "live": True, "note": note}
    SEGMENTS.append(row)
    return row


# ---- a file you upload -------------------------------------------------

_HEADINGS = {
    "email": ["email", "e-mail", "mail"],
    "phone": ["phone", "mobile", "number", "whatsapp"],
    "name": ["name", "contact", "person", "founder"],
    "handle": ["handle", "twitter", "linkedin", "username"],
    "company": ["company", "org", "organisation", "organization", "startup", "account"],
    "note": ["note", "comment", "context", "about"],
}


def guess_mapping(columns: list[str]) -> dict[str, str]:
    """Guess once, and show the guess. A mapping the founder can see is worth
    more than a clever one they can't."""
    out: dict[str, str] = {}
    for col in columns:
        c = (col or "").strip().lower()
        for field, names in _HEADINGS.items():
            if field in out.values():
                continue
            if any(n in c for n in names):
                out[col] = field
                break
    return out


def _rows(n: int) -> str:
    return "row has" if n == 1 else "rows have"


def parse_csv(text: str):
    rows = list(_csv.DictReader(_io.StringIO(text.strip())))
    cols = [c for c in (rows[0].keys() if rows else []) if c is not None]
    return cols, rows


def import_preview(text: str, mapping: dict, kind: str = "prospect") -> dict:
    cols, rows = parse_csv(text)
    mapping = mapping or guess_mapping(cols)
    inv = {v: k for k, v in mapping.items()}

    problems: list[str] = []
    if not rows:
        problems.append("The file has a heading row and nothing under it.")
    if "email" not in mapping.values() and "phone" not in mapping.values():
        problems.append("No email or phone column — there’d be no way to tell two people apart.")

    dupes, ready, seen, blank = [], 0, set(), 0
    for i, r in enumerate(rows):
        email = (r.get(inv.get("email", "")) or "").strip()
        phone = (r.get(inv.get("phone", "")) or "").strip()
        name = (r.get(inv.get("name", "")) or "").strip() or email or phone
        if not (email or phone):
            blank += 1
            continue
        key = (email or phone).lower()
        if key in seen:
            continue
        seen.add(key)
        hit = resolve(email=email or None, phone=phone or None)
        if hit:
            on = "email" if email and (hit.get("email") or "").lower() == email.lower() else "phone"
            dupes.append({"row": i + 2, "incoming": name, "existing_id": hit["id"],
                          "existing": hit["name"], "matched_on": on, "keep": hit["name"] or name})
        else:
            ready += 1
    if blank:
        problems.append(f"{blank} {_rows(blank)} no email and no phone — {'it' if blank == 1 else 'they'}’d be left out.")

    return {"columns": cols, "mapping": mapping, "rows_total": len(rows), "rows_ready": ready,
            "duplicates": dupes[:40], "problems": problems,
            "sample": [{k: (v or "") for k, v in r.items() if k} for r in rows[:5]]}


def do_import(text, mapping, kind="prospect", on_duplicate="merge", label=None) -> dict:
    cols, rows = parse_csv(text)
    mapping = mapping or guess_mapping(cols)
    inv = {v: k for k, v in mapping.items()}
    added = merged = skipped = 0
    touched: list[str] = []
    tag = f"import-{TODAY.isoformat()}"

    for r in rows:
        email = (r.get(inv.get("email", "")) or "").strip() or None
        phone = (r.get(inv.get("phone", "")) or "").strip() or None
        name = (r.get(inv.get("name", "")) or "").strip() or email or phone
        note = (r.get(inv.get("note", "")) or "").strip()
        if not (email or phone):
            skipped += 1
            continue
        hit = resolve(email=email, phone=phone)
        if hit:
            if on_duplicate == "skip":
                skipped += 1
                continue
            hit["email"] = hit.get("email") or email
            hit["phone"] = hit.get("phone") or phone
            if note and not hit.get("note"):
                hit["note"] = note
            if tag not in hit["tags"]:
                hit["tags"].append(tag)
            add_touch(hit["id"], "import", "you", "Matched a row in the file you uploaded",
                      channel="csv", surface_id="sales")
            merged += 1
            touched.append(hit["id"])
        else:
            p = new_person(name, kind, email=email, phone=phone, source="csv",
                           owner="agent", tags=[tag], note=note)
            add_touch(p["id"], "import", "you", "Came in on the file you uploaded",
                      channel="csv", surface_id="sales")
            added += 1
            touched.append(p["id"])

    seg_id = None
    if label and touched:
        seg_id = new_segment(label, {"tags": [tag]},
                             f"{len(touched)} from the file you uploaded")["id"]

    learned = [f"{added} {'person' if added == 1 else 'people'} you didn’t have",
               f"{merged} already here — merged, not doubled"]
    if skipped:
        learned.append(f"{skipped} {_rows(skipped)} no way to tell them apart — left out")
    return {"added": added, "merged": merged, "skipped": skipped,
            "segment_id": seg_id, "learned": learned}


# ---- the instruments, derived ------------------------------------------
#
# The funnel, the ladder and the radar keep the words they shipped with; the
# numbers under them now come from the book. `person_ids` is what turns a dot
# into something you can open rather than something you can only look at.

DOT_COPY: dict[str, dict] = {
    "signups": {"label": "Last week’s signups", "meta": "{n} enriched overnight",
                "at": 0, "lane": 0, "state": "running"},
    "cold": {"label": "Never opened anything", "meta": "{n} · leave them alone for now",
             "at": 0, "lane": 0, "state": "idle"},
    "talking": {"label": "Mid-conversation", "meta": "{n} · answered the first email",
                "at": 1, "lane": 0, "state": "running"},
    "leads": {"label": "Worth a call this week", "meta": "{n} · openers drafted, waiting on you",
              "at": 2, "lane": 0, "state": "needs-you"},
    "agency": {"label": "Tried an agency, bounced off price",
               "meta": "{n} · closest to SurferSearcher", "at": 2, "lane": 0, "state": "needs-you"},
    "won": {"label": "Paying", "meta": "{n} closed this month · ₹2,000 each",
            "at": 3, "lane": 0, "state": "shipped"},

    "ops-applied": {"label": "Applied", "meta": "{n} in 4 hours · above average",
                    "at": 0, "lane": 0, "state": "running"},
    "ops-screened": {"label": "Through the screen", "meta": "{n} the agent ranked against your JD",
                     "at": 1, "lane": 0, "state": "running"},
    "ops-your-call": {"label": "Your call", "meta": "Thursday 3pm and 4pm are held",
                      "at": 2, "lane": 0, "state": "needs-you"},
    "des-applied": {"label": "Applied", "meta": "not posted yet", "at": 0, "lane": 1, "state": "idle"},
    "des-screened": {"label": "Brief half-written", "meta": "you said designer first",
                     "at": 1, "lane": 1, "state": "idle"},
    "eng-applied": {"label": "Applied", "meta": "not started — deliberately",
                    "at": 0, "lane": 2, "state": "idle"},

    "tc": {"label": "TechCrunch — follow-up sent", "meta": "{d} · no reply yet, that’s normal",
           "size": 3, "state": "running"},
    "r1": {"label": "Replied to your last note", "meta": "{d} · warmest thing you have",
           "size": 3, "state": "shipped"},
    "r2": {"label": "Read it, didn’t reply", "meta": "{d}", "size": 2, "state": "running"},
    "r3": {"label": "Covers founder tooling monthly", "meta": "{d} · worth a personal note",
           "size": 3, "state": "needs-you"},
    "r4": {"label": "Asked for the deck once", "meta": "{d}", "size": 2, "state": "idle"},
    "r5": {"label": "{n} on the list have gone quiet",
           "meta": "{d} · your PR expert cut them", "size": 2, "state": "idle"},
    "r6": {"label": "New: writes about AI adoption", "meta": "never contacted",
           "size": 2, "state": "idle"},
    "r7": {"label": "{n} more on the rebuilt list",
           "meta": "never contacted · waiting on your approval", "size": 2, "state": "needs-you"},
}

FUNNEL_DOTS = ["signups", "cold", "talking", "leads", "agency", "won"]
LADDER_DOTS = ["ops-applied", "ops-screened", "ops-your-call",
               "des-applied", "des-screened", "eng-applied"]
RADAR_DOTS = ["tc", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]


def _said_days(days: float) -> str:
    if days >= 900:
        return "never contacted"
    if days < 1:
        return "today"
    if days < 2:
        return "yesterday"
    if days < 14:
        return f"{int(days)} days ago"
    if days < 60:
        return f"{int(days / 7)} weeks ago"
    return f"{int(days / 30)} months ago"


# how far out a dot sits, by how long since anyone spoke to them. Banded
# rather than smooth, because the gap between 2 days and 5 matters and the gap
# between 5 months and 6 doesn't.
_RADAR_BANDS = [(1, 0.14), (3, 0.20), (7, 0.28), (14, 0.42),
                (30, 0.58), (60, 0.70), (120, 0.82)]


def _radar_at(days: float) -> float:
    """The middle is someone you spoke to this week; the edge is someone going
    cold. Never contacted sits near the edge but inside the ones who went
    quiet on you — not hearing back is worse than not having asked."""
    if days >= 900:
        return 0.86
    for limit, at in _RADAR_BANDS:
        if days <= limit:
            return at
    return 0.92


def _dot(dot: str, ids: list[str]) -> dict:
    c = DOT_COPY[dot]
    n = len(ids)
    days = min((days_since(person(i)) for i in ids if person(i)), default=999.0)
    fill = {"n": n, "d": _said_days(days)}
    return {
        "id": dot,
        "label": c["label"].format(**fill),
        "meta": c["meta"].format(**fill),
        "at": float(c["at"]) if "at" in c else _radar_at(days),
        "lane": c.get("lane", 0),
        "value": float(c.get("size", n)),
        "state": c["state"],
        "person_ids": ids,
    }


_INSTRUMENTS = {
    "sales": ("lifecycle", FUNNEL_DOTS,
              ["Signed up", "In conversation", "Worth a call", "Paying"],
              "The funnel",
              "Each band is a stage. The size of a dot is how many people are in it.",
              "people"),
    "hiring": ("hiring", LADDER_DOTS, ["Ops", "Design", "Engineering"],
               "The ladder",
               "One column per role. Rungs are stages — the top rung is your call.",
               "people"),
    "pr": ("press", RADAR_DOTS, [], "Who’s warm",
           "The middle is someone you spoke to this week. The edge is someone going cold.",
           "days since contact"),
}


def instrument_for(sid: str):
    """The sales funnel, the hiring ladder and the press radar, read off the
    people rather than typed out. Marketing's timeline is left alone — it's
    about work, not people."""
    spec = _INSTRUMENTS.get(sid)
    if not spec:
        return None
    plid, dots, lanes, title, caption, unit = spec
    return {
        "surface_id": sid,
        "type": PIPELINE_BY_ID[plid]["geometry"],
        "title": title,
        "caption": caption,
        "lanes": lanes,
        "unit": unit,
        "items": [_dot(d, DOTS.get(d, [])) for d in dots],
    }


# ---- the page ----------------------------------------------------------

def crm_stats() -> list[dict]:
    life = [p for p in PEOPLE if p["pipeline_id"] == "lifecycle"]
    warm = [p for p in PEOPLE if p["warmth"] == "warm"]
    open_money = sum(d["value"] for d in DEALS if d["state"] == "open")
    return [
        {"id": "everyone", "value": str(len(PEOPLE)), "label": "people", "delta": None},
        {"id": "warm", "value": str(len(warm)), "label": "touched this week", "delta": None},
        {"id": "call", "value": str(len([p for p in life if p["stage_id"] == "worth-a-call"])),
         "label": "worth a call", "delta": None},
        {"id": "open", "value": f"₹{open_money:,}", "label": "on the table", "delta": None},
    ]


def crm_progress() -> dict:
    """The cleanup, said as how far through it is."""
    stale = len([p for p in PEOPLE if "stale" in p.get("tags", [])])
    return {"label": "Merging stale leads", "value": max(0, 41 - stale), "of": 41,
            "note": "your sales expert spot-checks before it writes"}


# ---- what you can actually do -----------------------------------------
#
# A move is a control, not a label. `does` is who can take it: an agent, an
# expert, or you. Taking it makes a real work item or a real follow-up —
# which is the difference between a CRM and a page that describes one.
#
# `work_title` is how it reads in the work list once dispatched; `own_title`
# is how it reads on your plate when you keep it. Both are written here
# because the frontend doesn't get to invent Allya's words.

MOVES: dict[str, dict] = {
    "pitch": {"label": "Write them a personal note", "does": ["expert", "you"],
              "work_title": "Personal note to {name}",
              "own_title": "Write {name} a personal note"},
    "follow": {"label": "Follow up on the last one", "does": ["agent", "expert", "you"],
               "work_title": "Follow up with {name}", "own_title": "Follow up with {name}"},
    "call": {"label": "Put them in front of you", "does": ["agent", "you"],
             "work_title": "Hold two slots for {name}", "own_title": "Interview {name}"},
    "notes": {"label": "Read the screen notes", "does": ["you"],
              "work_title": "", "own_title": "Read the screen notes on {name}"},
    "opener": {"label": "Draft the opener", "does": ["agent", "expert", "you"],
               "work_title": "Opener for {name} — drafted against what they read",
               "own_title": "Write {name} the opener yourself"},
    "book": {"label": "Book the call", "does": ["agent", "you"],
             "work_title": "Find a time with {name}", "own_title": "Call {name}"},
    "reply": {"label": "Write the next reply", "does": ["agent", "expert", "you"],
              "work_title": "Reply to {name}", "own_title": "Reply to {name} yourself"},
    "winback": {"label": "Ask what broke", "does": ["agent", "you"],
                "work_title": "Ask {name} what broke", "own_title": "Ask {name} what broke"},
    "nudge": {"label": "Nudge them once", "does": ["agent"],
              "work_title": "One nudge to {name}", "own_title": ""},
    "deal": {"label": "Put it on the table", "does": ["you"],
             "work_title": "", "own_title": "Price it for {name}"},
    "leave": {"label": "Leave them alone for now", "does": ["you"],
              "work_title": "", "own_title": "Leave {name} alone until something changes"},
    "note": {"label": "Log a note", "does": ["you"], "work_title": "",
             "own_title": "Write down what you know about {name}"},
}


def _move(mid: str, p: dict) -> dict:
    spec = MOVES[mid]
    name = p["name"]
    return {"id": mid, "label": spec["label"], "does": list(spec["does"]),
            "work_title": spec["work_title"].format(name=name),
            "own_title": spec["own_title"].format(name=name)}


def next_moves(p: dict) -> list[dict]:
    """What you could do with this person, said as the move rather than the
    feature. Read off where they actually stand, not a fixed menu."""
    ids: list[str] = []
    stage, warmth = p["stage_id"], p["warmth"]
    kinds = p.get("kinds", [])

    if "journalist" in kinds:
        ids.append("pitch")
        if stage in ("read", "replied"):
            ids.append("follow")
    elif "candidate" in kinds:
        if stage == "screened":
            ids.append("call")
        ids.append("notes")
    else:
        if stage == "worth-a-call":
            ids += ["opener", "book"]
        elif stage == "talking":
            ids.append("reply")
        elif stage == "churned":
            ids.append("winback")
        elif stage == "signed-up" and warmth != "cold":
            ids.append("nudge")
        if stage in ("talking", "worth-a-call") and not deals_for(p["id"]):
            ids.append("deal")

    if warmth in ("cold", "never") and stage != "churned":
        ids.append("leave")
    ids.append("note")
    return [_move(i, p) for i in ids[:4]]


def take_move(p: dict, move_id: str, by: str = "agent", due: str | None = None) -> dict:
    """Take one. An agent or an expert gets a work item that lands in the
    work list and comes back for approval; keeping it gets you a follow-up
    with a date on it. Either way the person's trail records that it
    happened, because a move nobody can see afterwards didn't happen."""
    spec = MOVES.get(move_id)
    if not spec:
        raise KeyError(move_id)
    mv = _move(move_id, p)
    if by not in mv["does"]:
        raise ValueError(f"'{mv['label']}' isn't something {by} can take")

    surface = PIPELINE_BY_ID[p["pipeline_id"]]["surface_id"]
    if by == "you":
        f = new_followup(p["id"], mv["own_title"] or mv["label"], due, "you")
        t = add_touch(p["id"], "note", "you", f"You took it on — {f['what'].lower()}",
                      surface_id=surface)
        return {"work": None, "followup": f, "touch": t,
                "toast": f"Yours, by {_said_due(f['due'])}."}

    w = new_work(p, mv, by, surface)
    f = new_followup(p["id"], mv["work_title"], due, by, work_id=w["id"])
    who = "an agent" if by == "agent" else EXPERT_OF.get(surface, "an expert")
    t = add_touch(p["id"], "note", by, mv["work_title"], who=None if by == "agent" else who,
                  work_id=w["id"], surface_id=surface)
    return {"work": w, "followup": f, "touch": t,
            "toast": f"{'An agent' if by == 'agent' else who.capitalize()} has it. "
                     f"It comes back to you before anything goes out."}


# generic by discipline, never a name — the house rule, and the only honest
# thing to say when the seam between agent and human is the product's claim
EXPERT_OF = {
    "sales": "your sales expert",
    "pr": "your PR expert",
    "hiring": "your hiring expert",
    "marketing": "your brand expert",
    "ops": "your ops expert",
    "workspace": "an expert",
}

_wseq = 0


def new_work(p: dict, mv: dict, by: str, surface: str) -> dict:
    """A real row in the work list, carrying the person it's about. This is
    the wire that was missing: the people layer read from every floor and
    wrote to none of them, which is what made it a dashboard."""
    global _wseq
    import data as _data

    _wseq += 1
    row = {
        "id": f"crm-{_wseq}", "surface_id": surface, "status": "running", "origin": by,
        "undoable": False, "title": mv["work_title"],
        "meta": ("agent · started just now"
                 if by == "agent" else f"expert · {EXPERT_OF.get(surface, 'an expert')} has it"),
        "person_id": p["id"], "segment_id": None,
    }
    _data.WORK.insert(0, row)
    _data.WORK_SEED[row["id"]] = dict(row)
    return row


# ---- what's owed, and when by ------------------------------------------
#
# A contact list tells you who exists. A CRM tells you who you owe something
# to today. That needs a date, and it needs to be able to go overdue —
# otherwise nothing ever chases you and the page is a place you visit rather
# than a place that calls.

FOLLOWUPS: list[dict] = []
_fseq = 0


def _said_due(due: str) -> str:
    """A date said the way a person would say it."""
    today = TODAY.isoformat()
    d = _parse_date(due)
    if not d:
        return due
    days = (d - TODAY).days
    if days < -1:
        return f"{-days} days late"
    if days == -1:
        return "yesterday — late"
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days < 7:
        return d.strftime("%A")
    return d.isoformat() if due != today else "today"


def _parse_date(s: str):
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return _dt.date(y, m, d)
    except Exception:
        return None


def new_followup(pid, what, due=None, by="you", work_id=None) -> dict:
    global _fseq
    _fseq += 1
    row = {
        "id": f"fu{_fseq}", "person_id": pid, "what": what,
        # two days out by default: far enough not to be today's problem,
        # near enough that it doesn't quietly become never
        "due": due or (TODAY + _dt.timedelta(days=2)).isoformat(),
        "by": by, "state": "open", "created": TODAY.isoformat(), "work_id": work_id,
    }
    FOLLOWUPS.append(row)
    p = person(pid)
    if p:
        refresh_next_step(p)
    return row


def followup(fid: str):
    for f in FOLLOWUPS:
        if f["id"] == fid:
            return f
    return None


def followups_for(pid: str, state=None) -> list[dict]:
    rows = [f for f in FOLLOWUPS if f["person_id"] == pid]
    if state:
        rows = [f for f in rows if f["state"] == state]
    return sorted(rows, key=lambda f: f["due"])


def refresh_next_step(p: dict) -> dict:
    """The soonest thing owed, folded onto the record so a list can be
    sorted by who's actually late without opening anybody."""
    open_ = followups_for(p["id"], "open")
    if not open_:
        p["next_step"], p["next_due"], p["overdue"] = None, None, False
        return p
    soonest = open_[0]
    d = _parse_date(soonest["due"])
    p["next_step"] = soonest["what"]
    p["next_due"] = soonest["due"]
    p["overdue"] = bool(d and d < TODAY)
    return p


def patch_followup(f: dict, state=None, due=None) -> dict:
    if state:
        f["state"] = state
    if due:
        f["due"] = due
        f["state"] = "open"
    p = person(f["person_id"])
    if p:
        refresh_next_step(p)
    return f


def queue() -> list[dict]:
    """Today's list: everyone who's late, then due today, then due next —
    the order a founder opens this page to get."""
    rows = [f for f in FOLLOWUPS if f["state"] == "open"]
    return sorted(rows, key=lambda f: f["due"])


# ---- where they came from ----------------------------------------------

# which touch channels count as a way in. A payment isn't a door — it's what
# happens after one.
_ACQUISITION = {"site", "email", "whatsapp", "csv", "press", "social", "referral", "job-boards"}


def _uncap(s: str) -> str:
    """Drop the leading capital so a title reads mid-sentence, without
    flattening the proper nouns inside it — "LinkedIn" is not "linkedin"."""
    return s[:1].lower() + s[1:] if s else s


def attribution_for(p: dict) -> dict:
    """What brought them, what was in front of them when they moved, and the
    route between.

    First touch answers "where do leads come from". Last touch answers the
    more expensive question — what actually closes them. Both, because the
    channel that fills the top of the funnel is very often not the one that
    fills the bottom, and a single `source` string can't say that."""
    ts = sorted([t for t in TOUCHES if t["person_id"] == p["id"]], key=lambda t: t["at"])
    if not ts:
        return {"first": None, "last": None, "path": [], "converted_at": None,
                "days_to_convert": None, "note": "Nothing has happened to them yet."}

    channel = p.get("origin_channel") or "direct"
    said = p.get("origin_said") or "Arrived on their own"
    first = {"at": ts[0]["at"], "channel": channel, "said": said,
             "campaign_id": ts[0].get("campaign_id"), "direction_id": ts[0].get("direction_id"),
             "surface_id": ts[0].get("surface_id")}

    # the route: every touch that came through a channel, without repeating
    # the same channel twice in a row — a path is a story, not a log
    path, prev = [first], None
    for t in ts:
        ch = t.get("channel")
        if ch not in _ACQUISITION:
            continue
        key = (ch, t.get("campaign_id"))
        if key == prev:
            continue
        prev = key
        path.append({"at": t["at"], "channel": ch, "said": t["text"],
                     "campaign_id": t.get("campaign_id"), "direction_id": t.get("direction_id"),
                     "surface_id": t.get("surface_id")})

    conv = next((t for t in reversed(ts) if t["kind"] == "payment"), None)
    before = [s for s in path[1:] if not conv or s["at"] < conv["at"]]
    last = before[-1] if before else (path[1] if len(path) > 1 else None)

    days = None
    if conv:
        days = max(0, round((conv["at"] - first["at"]) / DAY))

    came = f"Came from {_uncap(said)}"
    if conv:
        note = f"{came} — paid {days} {'day' if days == 1 else 'days'} later."
    elif last:
        note = f"{came}. Last moved by: {_uncap(last['said'])}"
        note = note if note.endswith(".") else note + "."
    else:
        note = f"{came}. Nothing since."

    return {"first": first, "last": last, "path": path[:12],
            "converted_at": conv["at"] if conv else None,
            "days_to_convert": days, "note": note}


def today(limit: int = 3) -> list[dict]:
    """What's worth doing now, in the order it's worth doing.

    A founder who opens a hundred rows and a dozen columns has been handed a
    report, not an answer. This is the answer: at most three, each with the
    one move that handles it. The ranking is deliberately dull — what you
    already promised, then what an agent found and is waiting on you for,
    then the thing most likely to matter that nobody has started."""
    out: list[dict] = []
    seen: set[str] = set()

    def add(pid, why, urgency, move_id=None):
        if pid in seen or len(out) >= limit:
            return
        p = person(pid)
        if not p:
            return
        seen.add(pid)
        mv = None
        if move_id:
            mv = next((m for m in next_moves(p) if m["id"] == move_id), None)
        mv = mv or (next_moves(p) or [None])[0]
        out.append({
            "id": f"t-{pid}", "person_id": pid, "name": p["name"], "why": why,
            "move_id": mv["id"] if mv else None,
            "move_label": mv["label"] if mv else "",
            "does": mv["does"] if mv else [],
            "urgency": urgency,
        })

    # 1. what you already said you'd do, late first
    for f in sorted((f for f in FOLLOWUPS if f["state"] == "open"), key=lambda f: f["due"]):
        d = _parse_date(f["due"])
        late = bool(d and d < TODAY)
        due_now = bool(d and d == TODAY)
        if late or due_now:
            add(f["person_id"], f["what"], "late" if late else "today")

    # 2. the ones an agent worked up and handed back
    for p in filter_people(stage="worth-a-call", warmth="warm"):
        if not p.get("next_step"):
            add(p["id"], p.get("note") or "Worth a call this week.", "soon", "opener")

    # 3. the money already on the table with nothing scheduled against it
    for d in DEALS:
        if d["state"] == "open" and d.get("person_id"):
            p = person(d["person_id"])
            if p and not p.get("next_step"):
                add(p["id"], f"{d['note'] or d['title']} — ₹{d['value']:,} is open.", "soon", "book")

    # 4. nothing pressing: the most useful idle thing, said as a choice
    if not out:
        quiet = filter_people(stage="talking", warmth="cooling") or filter_people(stage="talking")
        if quiet:
            add(quiet[0]["id"], "Mid-conversation and going quiet. One reply keeps it alive.", "idea", "reply")
    return out[:limit]


def sources_out() -> list[dict]:
    return [{**s, "count": len([p for p in PEOPLE if p.get("source") == s["id"]])}
            for s in SOURCES]
