"""The people book.

Every floor already acted on people — the sales funnel, the hiring ladder and
the press radar are the same object drawn three ways. This is that object,
seeded once, so those three instruments can stop carrying hardcoded counts and
start reading from the same place.

The numbers here are not free. They have to reconcile with copy that already
ships, and the API's own test is that they still do:

    Signed up      58   (40 last week's signups + 18 who never opened)
    In conversation 6
    Worth a call   10   (7 worth a call + 3 who bounced off an agency's price)
    Paying          2   at ₹2,000 each
    Churned        12   the win-back note's recipients
    stale-tagged   41   what the CRM cleanup work item is merging
    journalists    22   the press list, 9 of them gone quiet
    candidates     11   the ops/design/engineering ladder

Naming: leads are a first name and an initial, companies are invented, and
journalists are an outlet and a beat rather than a byline. Nobody in here is
meant to resolve to a real person — the house rule against invented personas is
about Allya's experts, and a demo book that borrowed real journalists' names
would be a worse version of the same mistake.
"""

import datetime
import time

TODAY = datetime.date.today()
_MIDNIGHT = int(time.mktime(TODAY.timetuple()))
DAY = 86400


def _ts(days_ago: float, hour: int = 9) -> int:
    """A moment, said as 'this many days back'. Relative to today so the
    journey is always recent, the way the calendar already does it."""
    return int(_MIDNIGHT - days_ago * DAY + hour * 3600)


def _date(days_ago: float) -> str:
    return (TODAY - datetime.timedelta(days=round(days_ago))).isoformat()


# ---- pipelines ---------------------------------------------------------
#
# A stage's `at` is the lane index the instruments already encode with, so a
# stage and a funnel band are the same number.

PIPELINES: list[dict] = [
    {
        "id": "lifecycle",
        "label": "The funnel",
        "person_kind": "prospect",
        "surface_id": "sales",
        "geometry": "funnel",
        "unit": "people",
        "count_noun": "people",
        "stages": [
            {"id": "signed-up", "at": 0, "label": "Signed up", "kind": "open",
             "note": "They made an account. That’s all it means."},
            {"id": "talking", "at": 1, "label": "In conversation", "kind": "open",
             "note": "Answered something. The only stage you can’t automate out of."},
            {"id": "worth-a-call", "at": 2, "label": "Worth a call", "kind": "open",
             "note": "Same stage, same problem as SurferSearcher was."},
            {"id": "paying", "at": 3, "label": "Paying", "kind": "won",
             "note": "₹2,000 a month, first month free."},
            {"id": "churned", "at": 4, "label": "Churned", "kind": "dormant",
             "note": "Left. Month two is where you lose them."},
        ],
    },
    {
        "id": "deals",
        "label": "What’s on the table",
        "person_kind": "prospect",
        "surface_id": "sales",
        "geometry": "funnel",
        "unit": "₹",
        "count_noun": "deals",
        "stages": [
            {"id": "d-talking", "at": 0, "label": "Talking", "kind": "open", "note": ""},
            {"id": "d-quoted", "at": 1, "label": "Priced", "kind": "open",
             "note": "They’ve seen ₹2,000 and didn’t leave."},
            {"id": "d-committed", "at": 2, "label": "Said yes", "kind": "open",
             "note": "Waiting on a card, not a decision."},
            {"id": "d-won", "at": 3, "label": "Paying", "kind": "won", "note": ""},
        ],
    },
    {
        "id": "hiring",
        "label": "The ladder",
        "person_kind": "candidate",
        "surface_id": "hiring",
        "geometry": "ladder",
        "unit": "people",
        "count_noun": "people",
        "stages": [
            {"id": "applied", "at": 0, "label": "Applied", "kind": "open", "note": ""},
            {"id": "screened", "at": 1, "label": "Through the screen", "kind": "open",
             "note": "Ranked against the JD you approved."},
            {"id": "your-call", "at": 2, "label": "Your call", "kind": "open",
             "note": "The rung nothing gets past without you."},
            {"id": "offer", "at": 3, "label": "Offer out", "kind": "open", "note": ""},
            {"id": "joined", "at": 4, "label": "Joined", "kind": "won", "note": ""},
        ],
    },
    {
        "id": "investors",
        "label": "The raise",
        "person_kind": "investor",
        "surface_id": "workspace",
        "geometry": "radar",
        "unit": "days since contact",
        "count_noun": "people",
        "stages": [
            {"id": "i-intro", "at": 0, "label": "Intro made", "kind": "open", "note": ""},
            {"id": "i-talking", "at": 1, "label": "Talking", "kind": "open", "note": ""},
            {"id": "i-diligence", "at": 2, "label": "Diligence", "kind": "open", "note": ""},
            {"id": "i-committed", "at": 3, "label": "Committed", "kind": "won", "note": ""},
        ],
    },
    {
        "id": "press",
        "label": "Who’s warm",
        "person_kind": "journalist",
        "surface_id": "pr",
        "geometry": "radar",
        "unit": "days since contact",
        "count_noun": "people",
        "stages": [
            {"id": "never", "at": 0, "label": "Never contacted", "kind": "open", "note": ""},
            {"id": "pitched", "at": 1, "label": "Pitched", "kind": "open", "note": ""},
            {"id": "read", "at": 2, "label": "Read it", "kind": "open", "note": ""},
            {"id": "replied", "at": 3, "label": "Replied", "kind": "open",
             "note": "Relationships before pitches — this is the only stage that matters."},
            {"id": "covered", "at": 4, "label": "Wrote about you", "kind": "won", "note": ""},
        ],
    },
]

PIPELINE_BY_ID = {p["id"]: p for p in PIPELINES}
STAGE_LABEL = {s["id"]: s["label"] for p in PIPELINES for s in p["stages"]}
STAGE_AT = {s["id"]: s["at"] for p in PIPELINES for s in p["stages"]}


# ---- companies ---------------------------------------------------------

COMPANIES: list[dict] = [
    {"id": "co-surfer", "name": "SurferSearcher", "domain": "surfersearcher.com",
     "size": "2 people", "industry": "SEO tooling", "stage_id": "paying", "value": 2000,
     "note": "The one you keep telling everyone about. 13 campaigns in month one."},
    {"id": "co-hearth", "name": "Hearth Studio", "domain": "hearth.studio",
     "size": "3 people", "industry": "Design studio", "stage_id": "paying", "value": 2000,
     "note": "Signed after reading the pricing memo. Never took a call."},
    {"id": "co-plotline", "name": "Plotline", "domain": "plotline.in",
     "size": "4 people", "industry": "D2C analytics", "stage_id": "worth-a-call",
     "note": "Tried an agency for six months, bounced off ₹80,000 a month."},
    {"id": "co-kettle", "name": "Kettle", "domain": "kettle.app",
     "size": "1 person", "industry": "Founder tooling", "stage_id": "worth-a-call",
     "note": "Read the pricing page four times this week."},
    {"id": "co-marg", "name": "Marg Logistics", "domain": "marglogistics.com",
     "size": "11 people", "industry": "Logistics", "stage_id": "talking",
     "note": "Bigger than your usual. Wants a call, not a campaign."},
    {"id": "co-nimbus", "name": "Nimbus Labs", "domain": "nimbuslabs.io",
     "size": "6 people", "industry": "Dev tools", "stage_id": "churned",
     "note": "Left in month two. Said the hiring floor wasn’t what they came for."},
]

COMPANY_BY_ID = {c["id"]: c for c in COMPANIES}


# ---- the people --------------------------------------------------------

PEOPLE: list[dict] = []
TOUCHES: list[dict] = []
# dot id -> person ids. What lets an instrument keep its shipped wording while
# its numbers come from the book underneath it.
DOTS: dict[str, list[str]] = {}

_seq = 0


# Where leads actually come from, at the grain a founder decides on. "The
# site" isn't an answer — which post, which story, whose referral is. These
# are the six doors into this company, and the funnel can be split by any of
# them, which is the only way to find out that the channel filling the top
# is not the one filling the bottom.
ORIGINS: list[tuple[str, str]] = [
    ("press", "The SurferSearcher story"),
    ("social", "The pivot-lesson post on LinkedIn"),
    ("site", "The pricing page"),
    ("email", "The founder newsletter"),
    ("referral", "A founder who already pays"),
    ("direct", "Typed the address in"),
]

ORIGIN_BY_CHANNEL = dict(ORIGINS)


def _person(pid, name, kind, pipeline, stage, *, email=None, company=None, warmth="never",
            source="product-signups", owner="agent", tags=(), value=None, created=0.0,
            note="", dot=None, phone=None, handle=None, origin=None):
    channel, said = origin or ("direct", "Typed the address in")
    row = {
        "id": pid,
        "name": name,
        "kinds": [kind],
        "email": email,
        "phone": phone,
        "handle": handle,
        "company_id": company,
        "pipeline_id": pipeline,
        "stage_id": stage,
        "warmth": warmth,
        "source": source,
        "owner": owner,
        "tags": list(tags),
        "value": value,
        "created": _date(created),
        "last_touch_at": None,
        "note": note,
        "origin_channel": channel,
        "origin_said": said,
        "next_step": None,
        "next_due": None,
        "overdue": False,
    }
    PEOPLE.append(row)
    if dot:
        DOTS.setdefault(dot, []).append(pid)
    return row


def _touch(pid, days_ago, kind, by, text, *, who=None, channel=None, work=None,
           campaign=None, direction=None, surface=None, hour=9):
    global _seq
    _seq += 1
    TOUCHES.append({
        "id": f"t{_seq}",
        "person_id": pid,
        "at": _ts(days_ago, hour),
        "kind": kind,
        "by": by,
        "text": text,
        "who": who,
        "channel": channel,
        "work_id": work,
        "campaign_id": campaign,
        "direction_id": direction,
        "surface_id": surface,
    })


# --- the two who pay ---------------------------------------------------

_person("p-surfer", "Rahul M.", "customer", "lifecycle", "paying", email="rahul@surfersearcher.com",
        company="co-surfer", warmth="warm", owner="you", value=2000, created=64,
        tags=["ideal", "case-study"], dot="won", origin=("site", "The pricing page"),
        note="Your proof. Everything you pitch is some version of what happened to them.")
_touch("p-surfer", 64, "signup", "agent", "Signed up from the pricing page", channel="site", surface="sales")
_touch("p-surfer", 61, "email", "agent", "First campaign went out — 13 in month one started here",
       channel="email", direction="email", surface="marketing")
_touch("p-surfer", 58, "call", "you", "You took the call yourself. 40 minutes, no deck.", surface="sales")
_touch("p-surfer", 57, "payment", "agent", "₹2,000 · first month free ended", channel="stripe", surface="ops")
_touch("p-surfer", 12, "note", "expert", "Agreed to be named in the newsletter",
       who="your PR expert", surface="pr")
_touch("p-surfer", 3, "email", "agent", "Opened the pivot-lesson post twice, forwarded it once",
       channel="email", direction="email", surface="marketing")

_person("p-hearth", "Devika S.", "customer", "lifecycle", "paying", email="devika@hearth.studio",
        company="co-hearth", warmth="cooling", owner="agent", value=2000, created=31,
        tags=["self-serve"], dot="won", origin=("email", "The founder newsletter"),
        note="Signed off the pricing memo alone. Nobody has spoken to her since.")
_touch("p-hearth", 31, "signup", "agent", "Signed up at 11:40pm", channel="site", surface="sales")
_touch("p-hearth", 30, "email", "agent", "Read the pricing memo end to end", channel="email",
       direction="email", surface="marketing")
_touch("p-hearth", 29, "payment", "agent", "₹2,000 · never asked a question first",
       channel="stripe", surface="ops")
_touch("p-hearth", 22, "email", "agent", "Opened the month-two note, didn’t reply",
       channel="email", direction="email", surface="marketing")

# --- worth a call: the seven -------------------------------------------

_WORTH = [
    ("p-kettle", "Arjun P.", "arjun@kettle.app", "co-kettle", 9,
     "Read the pricing page four times this week and hasn’t written to you."),
    ("p-w2", "Sneha R.", "sneha.r@fold.co", None, 11,
     "Asked what happens after the free month. That’s the whole objection."),
    ("p-w3", "Imran K.", "imran@bellwether.dev", None, 7,
     "Runs marketing alone for two products. Exactly the pain you wrote about."),
    ("p-w4", "Tanvi B.", "tanvi@quietmile.in", None, 14,
     "Replied to the win-back note from a list she was never on."),
    ("p-w5", "Karthik V.", "kv@sundial.studio", None, 6,
     "Came from the SurferSearcher post. Mentioned it unprompted."),
    ("p-w6", "Meera J.", "meera@thirdshelf.co", None, 8,
     "Booked a call, moved it twice, hasn’t cancelled."),
    ("p-w7", "Aditya N.", "aditya@rowboat.app", None, 10,
     "Pre-revenue, bootstrapped, two weeks from launch. Your ICP, written down."),
]
# three of the seven came off one story. A bucket called "the site" would
# have hidden that, which is the whole reason this is a channel and a name.
_WORTH_ORIGIN = ["site", "press", "social", "email", "press", "referral", "press"]
for i, (pid, name, email, co, ago, note) in enumerate(_WORTH):
    _ch = _WORTH_ORIGIN[i]
    _person(pid, name, "prospect", "lifecycle", "worth-a-call", email=email, company=co,
            warmth="warm", owner="agent", created=ago + 6, tags=["enriched"], dot="leads",
            note=note, origin=(_ch, ORIGIN_BY_CHANNEL[_ch]))
    _touch(pid, ago + 6, "signup", "agent", "Signed up", channel="site", surface="sales")
    _touch(pid, ago, "email", "agent", "Opened the welcome sequence twice",
           channel="email", direction="email", surface="marketing")
    _touch(pid, 1, "note", "agent", "Enriched overnight — moved to worth a call",
           work="leads", surface="sales")

# --- worth a call: the three who bounced off an agency ------------------

_AGENCY = [
    ("p-plotline", "Nikhil D.", "nikhil@plotline.in", "co-plotline",
     "Six months with an agency at ₹80,000. Closest thing to SurferSearcher you have."),
    ("p-a2", "Ritika S.", "ritika@saltandpine.co", None,
     "Left an agency mid-retainer. Wants to see the work before the invoice."),
    ("p-a3", "Vikram A.", "vikram@northfold.in", None,
     "Priced out twice. Asked if ₹2,000 was a typo."),
]
for pid, name, email, co, note in _AGENCY:
    _person(pid, name, "prospect", "lifecycle", "worth-a-call", email=email, company=co,
            warmth="warm", owner="expert", created=26, tags=["agency-refugee", "enriched"],
            dot="agency", note=note, origin=("press", "The SurferSearcher story"))
    _touch(pid, 26, "signup", "agent", "Signed up", channel="site", surface="sales")
    _touch(pid, 19, "email", "agent", "Replied to the pricing memo", channel="email",
           direction="email", surface="marketing")
    _touch(pid, 4, "note", "expert", "Sales expert flagged this one — same story as SurferSearcher",
           who="your sales expert", surface="sales")

# --- in conversation: the six ------------------------------------------

_TALKING = [
    ("p-marg", "Sunil G.", "sunil@marglogistics.com", "co-marg",
     "Eleven people. Bigger than your usual, and asking about seats."),
    ("p-t2", "Farah H.", "farah@lanternwork.com", None, "Answered the first email in nine minutes."),
    ("p-t3", "Rohan T.", "rohan@paperkite.co", None, "Wants proof it works for services, not products."),
    ("p-t4", "Ananya C.", "ananya@twelvefold.in", None, "Asked for the hiring floor specifically."),
    ("p-t5", "Zaid M.", "zaid@corner.store", None, "Two replies, no question yet. Let him get there."),
    ("p-t6", "Priyanka L.", "priyanka@havenlabs.io", None, "Said “not this quarter” — which is a yes with a date."),
]
_TALKING_ORIGIN = ["referral", "social", "press", "site", "email", "social"]
for i, (pid, name, email, co, note) in enumerate(_TALKING):
    _ch = _TALKING_ORIGIN[i]
    _person(pid, name, "prospect", "lifecycle", "talking", email=email, company=co,
            warmth="warm", owner="agent", created=17, tags=["replied"], dot="talking",
            note=note, origin=(_ch, ORIGIN_BY_CHANNEL[_ch]))
    _touch(pid, 17, "signup", "agent", "Signed up", channel="site", surface="sales")
    _touch(pid, 15, "email", "agent", "First email out", channel="email", direction="email",
           surface="marketing")
    _touch(pid, 5, "email", "you", "Replied", channel="email", surface="sales")

# --- signed up: last week's forty --------------------------------------

_FIRST = ["Aarav", "Isha", "Kabir", "Nandini", "Yash", "Aisha", "Dev", "Riya", "Om", "Sara",
          "Neel", "Trisha", "Manav", "Kavya", "Ishaan", "Pooja", "Rehan", "Diya", "Arnav", "Simran"]
_LAST = "SGMKRTVBNPDJACLHFEW"
_DOMAIN = ["gmail.com", "outlook.com", "hey.com", "proton.me"]

for i in range(40):
    pid = f"p-s{i + 1}"
    name = f"{_FIRST[i % len(_FIRST)]} {_LAST[i % len(_LAST)]}."
    ago = 1 + (i % 7)
    # 23 of last week's forty came in on an old list and duplicated someone
    stale = ["stale"] if i % 5 in (0, 2) and i < 58 else []
    _person(pid, name, "prospect", "lifecycle", "signed-up",
            email=f"{_FIRST[i % len(_FIRST)].lower()}{i}@{_DOMAIN[i % 4]}",
            warmth="cooling" if i % 3 else "warm", owner="agent",
            source="product-signups", created=ago, tags=["enriched"] + stale, dot="signups",
            note="Enriched overnight. Nothing said yet.",
            # social and the site bring the volume; press brings the few that
            # go anywhere. Which is the point of being able to split by it.
            origin=ORIGINS[[1, 2, 1, 0, 2, 3, 1, 2, 5, 4][i % 10]])
    _touch(pid, ago, "signup", "agent", "Signed up", channel="site", surface="sales")
    _touch(pid, max(0.5, ago - 0.5), "email", "agent", "Welcome sequence started",
           channel="email", direction="email", surface="marketing")
    _touch(pid, 1, "note", "agent", "Enriched — company, role and stage filled in",
           work="leads", surface="sales")

# --- signed up: the eighteen who never opened anything ------------------

for i in range(18):
    pid = f"p-c{i + 1}"
    name = f"{_FIRST[(i + 7) % len(_FIRST)]} {_LAST[(i + 5) % len(_LAST)]}."
    ago = 34 + i * 3
    _person(pid, name, "prospect", "lifecycle", "signed-up",
            email=f"{_FIRST[(i + 7) % len(_FIRST)].lower()}.{i}@{_DOMAIN[i % 4]}",
            warmth="cold", owner="agent", source="csv", created=ago,
            tags=["stale"], dot="cold",
            note="Never opened anything. Leave them alone for now.",
            origin=("csv", "An old list you uploaded"))
    _touch(pid, ago, "import", "agent", "Came in on the old CSV", channel="csv", surface="sales")

# top up the stale tag to the 41 the cleanup work item is merging
_stale_now = [p for p in PEOPLE if "stale" in p["tags"]]
for p in PEOPLE:
    if len(_stale_now) >= 41:
        break
    if "stale" not in p["tags"] and p["stage_id"] == "signed-up":
        p["tags"].append("stale")
        _stale_now.append(p)

# --- churned: the twelve the win-back note went to ---------------------

for i in range(12):
    pid = f"p-ch{i + 1}"
    name = f"{_FIRST[(i + 3) % len(_FIRST)]} {_LAST[(i + 11) % len(_LAST)]}."
    _person(pid, name, "customer", "lifecycle", "churned",
            email=f"{_FIRST[(i + 3) % len(_FIRST)].lower()}{i}@{_DOMAIN[(i + 2) % 4]}",
            company="co-nimbus" if i == 0 else None,
            warmth="cooling" if i < 3 else "cold", owner="agent", source="product-signups",
            created=90 + i * 4, tags=["churned"], dot="churn",
            note="Left in month two. Three of these opened the win-back note twice.",
            origin=ORIGINS[[2, 1, 2, 5, 1, 2][i % 6]])
    _touch(pid, 90 + i * 4, "signup", "agent", "Signed up", channel="site", surface="sales")
    _touch(pid, 40 + i, "payment", "agent", "₹2,000 · one month", channel="stripe", surface="ops")
    _touch(pid, 32 + i, "churn", "agent", "Cancelled. No reason given.", channel="stripe", surface="ops")
    _touch(pid, 0, "email", "agent", "Win-back note sent", channel="email", campaign="e-winback",
           direction="email", work="winback", surface="marketing", hour=6)
    if i < 3:
        _touch(pid, 0, "email", "agent", "Opened it twice", channel="email",
               campaign="e-winback", direction="email", surface="marketing", hour=11)

# --- the press list: twenty-two ----------------------------------------
#
# An outlet and a beat, not a byline — a demo book with real journalists'
# names in it would be a worse version of the persona rule.

_PRESS = [
    ("p-tc", "TechCrunch — the India desk", "pitched", 2, "tc", "warm",
     "Follow-up sent with the 13-campaign number. No reply yet, that’s normal."),
    ("p-r1", "The Ken — founder tooling", "replied", 5, "r1", "warm",
     "Replied to your last note. Warmest thing you have."),
    ("p-r2", "Entrackr — SaaS funding", "read", 11, "r2", "cooling",
     "Read it, didn’t reply."),
    ("p-r3", "YourStory — bootstrapped founders", "pitched", 21, "r3", "cooling",
     "Covers founder tooling monthly. Worth a personal note, not a pitch."),
    ("p-r4", "Inc42 — early stage", "replied", 42, "r4", "cold",
     "Asked for the deck once, six weeks ago."),
    ("p-r6", "Morning Context — AI adoption", "never", None, "r6", "never",
     "New to the list. Writes about who’s actually using this stuff."),
]
for pid, name, stage, ago, dot, warmth, note in _PRESS:
    _person(pid, name, "journalist", "press", stage, warmth=warmth, owner="expert",
            source="press-list", created=120, tags=["press-list"], dot=dot, note=note,
            origin=("press", "Your PR expert kept them"))
    if ago is not None:
        _touch(pid, ago, "press", "expert", "Pitched the pivot story",
               who="your PR expert", surface="pr")
    if stage in ("read", "replied"):
        _touch(pid, ago - 1, "press", "agent", "Opened it", surface="pr")
    if stage == "replied":
        _touch(pid, ago - 2, "press", "expert", "Wrote back", who="your PR expert", surface="pr")

for i in range(9):
    pid = f"p-q{i + 1}"
    _person(pid, f"{['Founding', 'Startup', 'Tech', 'Business', 'Product'][i % 5]} desk — outlet {i + 1}",
            "journalist", "press", "pitched", warmth="cold", owner="expert",
            source="press-list", created=200, tags=["press-list", "quiet"], dot="r5",
            origin=("press", "Your PR expert kept them"),
            note="Six months quiet. Your PR expert cut these from the refresh.")
    _touch(pid, 180 + i, "press", "expert", "Pitched once, never answered",
           who="your PR expert", surface="pr")

for i in range(7):
    pid = f"p-n{i + 1}"
    _person(pid, f"{['Regional', 'Weekend', 'Trade', 'Newsletter', 'Podcast', 'Video', 'Wire'][i]} desk — new",
            "journalist", "press", "never", warmth="never", owner="expert",
            source="press-list", created=3, tags=["press-list", "new"], dot="r7",
            origin=("press", "The rebuilt press list"),
            note="On the rebuilt list, never contacted. Waiting on your approval.")

# --- the hiring ladder: eleven -----------------------------------------

_CANDIDATES = [
    ("p-h1", "Ops", "your-call", "Thursday 3pm is held. Ranked first against your JD."),
    ("p-h2", "Ops", "your-call", "Thursday 4pm is held. Slower, better written."),
    ("p-h3", "Ops", "screened", "Through the screen. Ran ops at a 12-person company."),
    ("p-h4", "Ops", "screened", "Through the screen. Wants remote, you didn’t say."),
    ("p-h5", "Ops", "applied", "Applied in the first hour."),
    ("p-h6", "Ops", "applied", "Applied. No cover note, strong work."),
    ("p-h7", "Ops", "applied", "Applied twice from two addresses."),
    ("p-h8", "Ops", "applied", "Applied. Overqualified and knows it."),
    ("p-h9", "Ops", "applied", "Applied from the LinkedIn post."),
    ("p-h10", "Ops", "applied", "Applied. Asked what the first 90 days look like."),
    ("p-h11", "Design", "screened", "The brief is half-written — you said designer first."),
]
for pid, role, stage, note in _CANDIDATES:
    _person(pid, f"Candidate · {role.lower()} · {pid.split('-')[1]}", "candidate", "hiring", stage,
            warmth="warm" if stage == "your-call" else "cooling", owner="agent",
            source="job-boards", created=4, tags=[f"role:{role.lower()}"],
            dot=f"{role.lower()[:3]}-{stage}", note=note,
            origin=("job-boards", "The ops-role posting"))
    _touch(pid, 4, "application", "agent", f"Applied for the {role.lower()} role", surface="hiring")
    if stage in ("screened", "your-call"):
        _touch(pid, 1, "stage", "agent", "Through the first screen — ranked against your JD",
               work="screening", surface="hiring")
    if stage == "your-call":
        _touch(pid, 0, "meeting", "expert", "Your hiring expert sat in and held the slot",
               who="your hiring expert", surface="hiring")

# --- one investor, because the workspace calendar already has the call --

_person("p-meridian", "Meridian — partner", "investor", "investors", "i-talking", warmth="warm",
        owner="you", source="intro", created=48, tags=["investor"],
        origin=("referral", "A warm intro"),
        note="Call today at 11. Notes are ready — the 13-campaign number is the whole story.")
_touch("p-meridian", 48, "meeting", "you", "Warm intro", surface="workspace")
_touch("p-meridian", 9, "email", "you", "Sent the deck", channel="email", surface="workspace")
_touch("p-meridian", 0, "meeting", "agent", "Investor call — notes ready", surface="workspace", hour=11)


# ---- last_touch_at and warmth, derived once ---------------------------

_LAST_TOUCH: dict[str, int] = {}
for t in TOUCHES:
    pid = t["person_id"]
    if t["at"] > _LAST_TOUCH.get(pid, 0):
        _LAST_TOUCH[pid] = t["at"]

for p in PEOPLE:
    p["last_touch_at"] = _LAST_TOUCH.get(p["id"])


def warmth_of(person: dict) -> str:
    """How long since anyone spoke to them, said as a word. Recomputed rather
    than stored, so a touch landing today warms someone up on its own."""
    at = person.get("last_touch_at")
    if not at:
        return "never"
    days = (_MIDNIGHT + DAY - at) / DAY
    if days <= 7:
        return "warm"
    if days <= 30:
        return "cooling"
    return "cold"


def days_since(person: dict) -> float:
    at = person.get("last_touch_at")
    if not at:
        return 999.0
    return max(0.0, (_MIDNIGHT + DAY - at) / DAY)


for p in PEOPLE:
    p["warmth"] = warmth_of(p)


# ---- deals -------------------------------------------------------------

DEALS: list[dict] = [
    {"id": "dl-surfer", "person_id": "p-surfer", "company_id": "co-surfer",
     "title": "SurferSearcher · monthly", "value": 2000, "currency": "INR",
     "pipeline_id": "deals", "stage_id": "d-won", "state": "won",
     "opened": _date(64), "expected_close": None, "work_id": None,
     "note": "Closed on a call you took yourself."},
    {"id": "dl-hearth", "person_id": "p-hearth", "company_id": "co-hearth",
     "title": "Hearth Studio · monthly", "value": 2000, "currency": "INR",
     "pipeline_id": "deals", "stage_id": "d-won", "state": "won",
     "opened": _date(31), "expected_close": None, "work_id": None,
     "note": "Closed itself. Nobody spoke to them."},
    {"id": "dl-plotline", "person_id": "p-plotline", "company_id": "co-plotline",
     "title": "Plotline · monthly", "value": 2000, "currency": "INR",
     "pipeline_id": "deals", "stage_id": "d-quoted", "state": "open",
     "opened": _date(19), "expected_close": _date(-9), "work_id": "leads",
     "note": "Has seen ₹2,000 against the ₹80,000 they were paying. Didn’t leave."},
    {"id": "dl-marg", "person_id": "p-marg", "company_id": "co-marg",
     "title": "Marg Logistics · seats", "value": 6000, "currency": "INR",
     "pipeline_id": "deals", "stage_id": "d-talking", "state": "open",
     "opened": _date(15), "expected_close": _date(-21), "work_id": None,
     "note": "Eleven people. The first one that isn’t a single founder."},
    {"id": "dl-kettle", "person_id": "p-kettle", "company_id": "co-kettle",
     "title": "Kettle · monthly", "value": 2000, "currency": "INR",
     "pipeline_id": "deals", "stage_id": "d-committed", "state": "open",
     "opened": _date(9), "expected_close": _date(-2), "work_id": None,
     "note": "Said yes. Waiting on a card, not a decision."},
]


# ---- segments ----------------------------------------------------------
#
# What `audience` used to be a sentence about. A campaign still says
# "Signups who never opened" out loud — this is what that resolves to.

SEGMENTS: list[dict] = [
    {"id": "sg-never-opened", "label": "Signups who never opened",
     "rule": {"stage_ids": ["signed-up"], "never_kind": "email"},
     "live": True, "note": "The eighteen. Leave them alone until something changes."},
    {"id": "sg-worth-a-call", "label": "Worth a call this week",
     "rule": {"stage_ids": ["worth-a-call"]},
     "live": True, "note": "Same stage, same problem as SurferSearcher was."},
    {"id": "sg-last-week", "label": "Last week’s signups",
     "rule": {"stage_ids": ["signed-up"], "sources": ["product-signups"]},
     "live": True, "note": "Enriched overnight."},
    {"id": "sg-churned", "label": "Churned users",
     "rule": {"stage_ids": ["churned"]},
     "live": True, "note": "Month two is where you lose them."},
    {"id": "sg-agency", "label": "Bounced off an agency’s price",
     "rule": {"tags": ["agency-refugee"]},
     "live": True, "note": "The closest thing you have to a repeatable story."},
    {"id": "sg-talking", "label": "Mid-conversation",
     "rule": {"stage_ids": ["talking"]},
     "live": True, "note": "The only stage you can’t automate your way out of."},
    {"id": "sg-quiet", "label": "Nobody has written in 30 days",
     "rule": {"kinds": ["prospect", "customer"], "not_touched_days": 30},
     "live": True, "note": "Not a campaign. A list to look at."},
    {"id": "sg-press-warm", "label": "Press who replied once",
     "rule": {"kinds": ["journalist"], "stage_ids": ["replied"]},
     "live": True, "note": "Relationships before pitches."},
    {"id": "sg-stale", "label": "Duplicates of each other",
     "rule": {"tags": ["stale"]},
     "live": True, "note": "What the cleanup is merging. It shrinks as it works."},
    {"id": "sg-press-list", "label": "The press list",
     "rule": {"kinds": ["journalist"]},
     "live": True, "note": "Everyone your PR expert keeps, quiet ones included."},
    {"id": "sg-shortlist", "label": "Candidates past the screen",
     "rule": {"kinds": ["candidate"], "stage_ids": ["screened", "your-call"]},
     "live": True, "note": "Ranked against the JD you approved."},
    {"id": "sg-everyone-email", "label": "Everyone with an address",
     "rule": {"kinds": ["prospect", "customer"]},
     "live": True, "note": "The whole list, which is almost never the right answer."},
]


# ---- where they come from ----------------------------------------------

SOURCES: list[dict] = [
    {"id": "product-signups", "label": "Product signups", "state": "connected",
     "blurb": "Everyone who makes an account lands here the moment they do.",
     "last_sync": "today, 6:10am", "count": 0, "note": ""},
    {"id": "site", "label": "The site", "state": "connected",
     "blurb": "Pricing-page visits and form fills, matched to a person by email.",
     "last_sync": "today, 6:10am", "count": 0, "note": "1,900 visits last month, 40 with a name on them."},
    {"id": "email", "label": "Email", "state": "connected",
     "blurb": "Sends, opens and replies land on the person, not just the campaign.",
     "last_sync": "today, 7:05am", "count": 0, "note": ""},
    {"id": "whatsapp", "label": "WhatsApp", "state": "connected",
     "blurb": "Reads and replies, same shape as email.",
     "last_sync": "yesterday, 8:40pm", "count": 0, "note": ""},
    {"id": "stripe", "label": "Payments", "state": "connected",
     "blurb": "A payment moves someone to paying. A cancellation moves them out.",
     "last_sync": "today, 5:40am", "count": 0, "note": ""},
    {"id": "csv", "label": "A file you upload", "state": "available",
     "blurb": "Drop the spreadsheet you already keep. Duplicates get merged, not doubled.",
     "last_sync": "34 days ago", "count": 0, "note": "The last one is where the 41 stale leads came from."},
    {"id": "press-list", "label": "The press list", "state": "connected",
     "blurb": "Journalists your PR expert keeps, on the same records as everyone else.",
     "last_sync": "today, 6:50am", "count": 0, "note": ""},
    {"id": "job-boards", "label": "Job boards", "state": "connected",
     "blurb": "Applicants arrive as people, so a candidate who becomes a customer is one record.",
     "last_sync": "today, 7:15am", "count": 0, "note": ""},
]


# ---- what the page says ------------------------------------------------

CRM_NOUNS = {
    "one": "person", "many": "people", "metric": "warm",
    "automations": "segments", "audience_word": "segment",
}

CRM_UI = {
    "tint": "b1",
    "floor_label": "Sales",
    "floor_href": "/sales",
    "placeholder": "Ask about anyone — “who’s worth a call?”",
    "suggestions": [
        "Who’s worth a call this week?",
        "Who’s gone quiet since last month?",
        "Show me everyone who bounced off an agency",
    ],
    "know_title": "What I know about your people",
    "brain_title": "Everyone, and every touch",
    "brain_subtitle": "touch a band",
    "back_label": "Back to Sales",
    "back_href": "/sales",
    # filled in below, once the views are declared
}

# ---- the grid's shape -------------------------------------------------
#
# Which columns exist, what they're called and which show by default. The
# client renders a column by `key`, which is a field on a person row — so a
# column added here appears in the grid with no frontend change at all.
#
# Column names are the first place a CRM starts sounding like software.
# "Owed", "Worked by", "On the table" and "Came in through" are how the
# system thinks; "Next step", "Who's on it", "Deal" and "Found you via" are
# how a founder asks. Same data.

def _col(key, label, group, on=False, **kw):
    return {"key": key, "label": label, "group": group, "on": on,
            "num": kw.get("num", False), "wide": kw.get("wide", False)}


TABLE_GROUPS = ["Who", "Where", "Money", "Contact", "History"]

TABLE_COLUMNS: list[dict] = [
    _col("name", "Name", "Who", True),
    _col("kind", "What they are", "Who"),
    _col("company", "Company", "Who"),
    # keys are camelCase because they name fields on a person row as the wire
    # spells them — that's what lets the client render a column it has never
    # been taught about
    _col("companySize", "How big they are", "Who"),
    _col("companyIndustry", "What they do", "Who"),
    _col("owner", "Who’s on it", "Who"),

    # A stage says how far along someone is; it doesn't say what they're
    # after. Two people in one band can want opposite things.
    _col("intent", "What they want", "Where", True, wide=True),
    _col("stage", "Stage", "Where", True),
    _col("inStage", "Days here", "Where", num=True),
    _col("warmth", "Last contact", "Where", True),
    _col("touch", "Ago", "Where", num=True),
    _col("due", "Next step", "Where", True),
    _col("segments", "Lists they’re on", "Where", wide=True),

    _col("open", "Deal", "Money", num=True),
    _col("value", "Paying", "Money", num=True),
    _col("deals", "Deals", "Money", num=True),

    _col("email", "Email", "Contact", True),
    _col("phone", "Phone", "Contact"),
    _col("handle", "Handle", "Contact"),
    _col("tags", "Tags", "Contact"),

    _col("origin", "Found you via", "History", True, wide=True),
    _col("created", "First seen", "History", num=True),
    _col("touches", "Times touched", "History", num=True),
    _col("last", "Last thing that happened", "History", wide=True),
    _col("note", "What I know about them", "History", True, wide=True),
]

TABLE_PRESETS: list[dict] = [
    {"id": "simple", "label": "Simple",
     "note": "who they are, what they want, and what’s next",
     "keys": ["name", "intent", "stage", "warmth", "due", "origin", "email", "note"]},
    {"id": "sales", "label": "Chasing revenue",
     "note": "adds the money, the account and how long they’ve sat there",
     "keys": ["name", "company", "companySize", "intent", "stage", "inStage",
              "warmth", "due", "open", "origin", "owner", "note"]},
    {"id": "all", "label": "Everything",
     "note": f"all {len(TABLE_COLUMNS)}",
     "keys": [c["key"] for c in TABLE_COLUMNS]},
]


# ---- the words the interface uses ---------------------------------------
#
# Each of these was a constant in a component, which is how the warmth words
# ended up spelled three different ways on three different screens.

LEXICON = {
    "warmth": [
        {"id": "warm", "said": "this week", "said_full": "spoken to this week", "rank": 0},
        {"id": "cooling", "said": "this month", "said_full": "spoken to this month", "rank": 1},
        {"id": "cold", "said": "gone quiet", "said_full": "gone quiet", "rank": 2},
        {"id": "never", "said": "never", "said_full": "never spoken to", "rank": 3},
    ],
    "touch_kinds": {
        "signup": "Signed up", "email": "Email", "whatsapp": "WhatsApp",
        "call": "Call", "meeting": "Met", "payment": "Payment",
        "churn": "Cancelled", "note": "Note", "stage": "Moved",
        "import": "Imported", "application": "Applied", "press": "Press",
    },
    "urgency": {
        "late": "late", "today": "today",
        "soon": "worth doing", "idea": "if you have a minute",
    },
    "dispatch": [
        {"id": "agent", "verb": "An agent", "note": "comes back before anything goes out"},
        {"id": "expert", "verb": "An expert", "note": "a real operator writes it"},
        {"id": "you", "verb": "I will", "note": "lands on your list with a date"},
    ],
    "experts": {
        "sales": "your sales expert", "pr": "your PR expert",
        "hiring": "your hiring expert", "marketing": "your brand expert",
        "ops": "your ops expert", "workspace": "an expert",
    },
}

CRM_VIEWS = [
    {"id": "table", "label": "Table", "note": "every column, sortable"},
    {"id": "people", "label": "Map", "note": "the funnel and what’s owed"},
    {"id": "companies", "label": "Companies", "note": "the accounts they belong to"},
]

# the switch in the header is drawn from the page's own dressing, like every
# other word on it
CRM_UI["views"] = CRM_VIEWS

CRM_NOTES = [
    "Every send, reply, payment and cancellation lands on the person it happened to.",
    "41 of your leads are duplicates of each other — the cleanup is running now.",
    "Nobody has written to the eighteen who never opened anything. That’s deliberate.",
    "A journalist, a candidate and a lead are one record here, not three.",
]

CRM_BLURB = ("Everyone your company has ever touched, and everything that happened to them. "
             "Marketing writes to them, sales calls them, PR pitches them — same book.")


# ---- snapshots, for undo -----------------------------------------------

PEOPLE_SEED = {p["id"]: dict(p, tags=list(p["tags"]), kinds=list(p["kinds"])) for p in PEOPLE}
TOUCHES_SEED = [dict(t) for t in TOUCHES]
DEALS_SEED = {d["id"]: dict(d) for d in DEALS}
