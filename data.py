"""In-memory seed for the dummy API.

Everything the two brain surfaces render lives here. Swap these dicts for real
queries and the contract in models.py does not change.

House rules carried over from the product: leaves are live thoughts, not
service names; proof points are the real ones (SurferSearcher's 13 campaigns,
Mili's 28 tasks, ₹2,000/mo first month free); humans are referred to
generically — "your brand expert" — never by an invented name.
"""

import os
import time

DAY = 86400
NOW = int(time.time())

# the eight branch tints the client maps to colours, reused per surface
TINTS = ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]

SERVICE_IDS = ["marketing", "hiring", "pr", "sales", "ops"]


# ---- surfaces ----------------------------------------------------------

SURFACES: dict[str, dict] = {
    "workspace": {
        "id": "workspace",
        "label": "Workspace",
        "greeting": "Morning. Here’s your company as I hold it — five services and what’s live under each. Touch a service to go inside it.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — what's eating your week?",
        "suggestions": [
            "Draft next week’s newsletter",
            "Where’s the ops hire?",
            "Clean up my CRM again this week",
        ],
        "brain": {
            "title": "The brain",
            "subtitle": "your company, as I understand it — touch a service to open it",
            "back_label": "Onboarding →",
            "back_href": "/onboarding",
        },
        "status_noun": "agent",
        "knowledge_title": "What I know",
        "schedule_title": "Today",
        "node_copy": {
            "core": "Everything Allya knows about your company, in one place.",
            "marketing": "How the market hears about you. Campaigns, content, and the story you keep telling.",
            "hiring": "Who joins, in what order, and what you promise them on day one.",
            "pr": "Who writes about you, and why now. Relationships before pitches.",
            "sales": "Where revenue actually comes from this month — not the theory of it.",
            "ops": "The plumbing: money out, time spent, decisions written down.",
        },
        "empty_needs": "Nothing right now. Agents are working; experts are checking. That’s the whole point.",
    },
    "marketing": {
        "id": "marketing",
        "label": "Marketing",
        "greeting": "Marketing, opened up. Everything hanging off it is above — the cord below goes back to the company.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — what should the market hear this week?",
        "suggestions": [
            "What’s working this week?",
            "Draft next week’s newsletter",
            "Cut the demo into shorts",
        ],
        "brain": {
            "title": "The brain · marketing",
            "subtitle": "8 directions — touch one",
            "back_label": "Whole company →",
            "back_href": "/",
        },
        "status_noun": "marketing agent",
        "knowledge_title": "What I know about your marketing",
        "schedule_title": "Going out this week",
        "node_copy": {
            "marketing": "How the market hears about you — opened up. Eight directions, and what’s live under each.",
            "b1": "What you stand for, in words you’d actually say out loud. Everything else is downstream of this.",
            "b2": "The proof you publish. Made once, cut many ways — the demo is the raw material.",
            "b3": "Where founders already are. Reach earned by showing up, not by budget.",
            "b4": "The channel you own. Nobody can throttle it, so it has to be worth opening.",
            "b5": "Moments with a date on them. A launch is a deadline pointed at the market.",
            "b6": "Where you get found, and what happens in the six seconds after.",
            "b7": "Other people’s rooms, and the clients who’ll vouch for you in them.",
            "b8": "Money as a test, not a habit. Nothing scales until the organic version works.",
        },
        "empty_needs": "Nothing right now. Agents are drafting; your brand expert is checking. Marketing keeps moving without you in the room.",
    },
    "hiring": {
        "id": "hiring",
        "label": "Hiring",
        "greeting": "Hiring, opened up. Who joins, in what order, and what you promise them on day one.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — who are we looking for?",
        "suggestions": ["Where’s the ops hire?", "Show me the shortlist", "Write the day-one checklist"],
        "brain": {"title": "The brain · hiring", "subtitle": "4 directions — touch one", "back_label": "Whole company →", "back_href": "/"},
        "status_noun": "hiring agent",
        "knowledge_title": "What I know about your hiring",
        "schedule_title": "This week",
        "node_copy": {
            "hiring": "Who joins, in what order, and what you promise them on day one.",
            "b1": "Who’s in the funnel right now, and how they got there.",
            "b2": "How you decide. Fewer rounds, better questions.",
            "b3": "The first week. It sets the next year.",
            "b4": "What the role is worth, and what you can actually pay.",
        },
        "empty_needs": "Nothing waiting. The screening agent is working; your hiring expert reviews before anything reaches you.",
    },
    "pr": {
        "id": "pr",
        "label": "PR",
        "greeting": "PR, opened up. Who writes about you, and why now.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — what story are we telling?",
        "suggestions": ["Who should we pitch?", "Refresh the press list", "What’s the angle this month?"],
        "brain": {"title": "The brain · PR", "subtitle": "4 directions — touch one", "back_label": "Whole company →", "back_href": "/"},
        "status_noun": "PR agent",
        "knowledge_title": "What I know about your PR",
        "schedule_title": "This week",
        "node_copy": {
            "pr": "Who writes about you, and why now. Relationships before pitches.",
            "b1": "The people who might write it. Kept warm, not spammed.",
            "b2": "Why a story is worth running this week and not next.",
            "b3": "The slow part. It’s also the part that works.",
            "b4": "What ran, and what you did with it afterwards.",
        },
        "empty_needs": "Nothing waiting. Your PR expert is working the list; nothing gets pitched without you.",
    },
    "sales": {
        "id": "sales",
        "label": "Sales",
        "greeting": "Sales, opened up. Where revenue actually comes from this month.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — where’s revenue coming from?",
        "suggestions": ["Who should I call today?", "Clean up my CRM", "Should we test annual pricing?"],
        "brain": {"title": "The brain · sales", "subtitle": "4 directions — touch one", "back_label": "Whole company →", "back_href": "/"},
        "status_noun": "sales agent",
        "knowledge_title": "What I know about your sales",
        "schedule_title": "This week",
        "node_copy": {
            "sales": "Where revenue actually comes from this month — not the theory of it.",
            "b1": "What’s real, what’s hope, and what’s already dead.",
            "b2": "How you start conversations without buying a list.",
            "b3": "The number, and how you say it out loud.",
            "b4": "Month two is where you lose them. This is that.",
        },
        "empty_needs": "Nothing waiting. Agents are enriching and sequencing; your sales expert spot-checks before anything sends.",
    },
    "ops": {
        "id": "ops",
        "label": "Ops",
        "greeting": "Ops, opened up. Money out, time spent, decisions written down.",
        "hint": "Click the bar below when you want to talk",
        "placeholder": "Direct Allya — what should I stop doing?",
        "suggestions": ["Where’s my time going?", "Write the pricing memo", "What can we cut?"],
        "brain": {"title": "The brain · ops", "subtitle": "4 directions — touch one", "back_label": "Whole company →", "back_href": "/"},
        "status_noun": "ops agent",
        "knowledge_title": "What I know about your ops",
        "schedule_title": "This week",
        "node_copy": {
            "ops": "The plumbing: money out, time spent, decisions written down.",
            "b1": "Your calendar is the real strategy document.",
            "b2": "What leaves the account, and how long that leaves you.",
            "b3": "Written down, or it didn’t happen.",
            "b4": "One tool per job. Cancel the rest.",
        },
        "empty_needs": "Nothing waiting. Quiet is the correct state here.",
    },
}


# ---- brains ------------------------------------------------------------

def _node(nid, label, tier, group, parent=None, **kw):
    return {"id": nid, "label": label, "tier": tier, "group": group, "parent": parent, **kw}


def _branch(service: str, branches: list[tuple[str, str, str, list[tuple[str, str]]]]):
    """Expand (id, label, short, [(leaf_id, leaf_label)]) into a spray graph.

    The company hub and the service itself are always present — that single
    hub→service link is what keeps a service page part of the same brain.
    """
    nodes = [
        # the cord runs somewhere: tapping the company flies back up to it
        _node("co", "Your company", 0, "core", surface="workspace"),
        _node(service, SURFACES[service]["label"], 1, service, "co"),
    ]
    for i, (bid, label, short, leaves) in enumerate(branches):
        tint = TINTS[i % len(TINTS)]
        nodes.append(_node(bid, label, 2, tint, service, short=short, hidden=True))
        for lid, ltext in leaves:
            work = lid if lid in WORK_IDS else None
            nodes.append(_node(lid, ltext, 3, tint, bid, hidden=True, work=work))
    return nodes


# work ids referenced from brain leaves, declared before _branch runs
WORK_IDS = {
    "newsletter", "reel", "shorts", "warmup", "hero", "listening", "linkedin", "retarget",
    "shortlist", "screening", "jd-posted",
    "presslist", "pitch", "coverage",
    "leads", "crm", "winback",
    "pricing-memo", "hosting", "runway",
}

MARKETING_BRANCHES = [
    ("story", "Story & positioning", "Story", [
        ("st_fast", "Own “fast”, not “cheap”"),
        ("st_price", "Say the ₹2,000 out loud"),
        ("st_line", "The one-liner is still hedging"),
        ("st_seam", "Show the 85/15 seam"),
        ("hero", "Kill the word “platform”"),
    ]),
    ("content", "Content", "Content", [
        ("shorts", "Cut the demo into shorts"),
        ("ct_memo", "Publish the pricing memo"),
        ("ct_28", "Teardown: 28 tasks in 30 days"),
        ("ct_diary", "Founder diary, once a week"),
        ("ct_faq", "Turn support replies into FAQs"),
    ]),
    ("social", "Social", "Social", [
        ("linkedin", "LinkedIn: the pivot lesson"),
        ("reel", "Reel: the day-one story"),
        ("so_reply", "Reply to 10 founders a day"),
        ("so_ugly", "Post the ugly first draft"),
        ("so_thread", "Thread: 13 campaigns, month one"),
    ]),
    ("email", "Email & lifecycle", "Email", [
        ("newsletter", "Next week’s newsletter"),
        ("warmup", "Warm 200 cold addresses"),
        ("em_day3", "The day-3 nudge is too polite"),
        ("em_back", "Win back last month’s signups"),
        ("em_ps", "One-reply P.S., every send"),
    ]),
    ("launch", "Launches", "Launches", [
        ("la_free", "Launch the free first month"),
        ("la_receipts", "Receipts post: 13 campaigns"),
        ("la_invite", "Waitlist → 3 invites a day"),
        ("la_ph", "Product Hunt — or skip it?"),
        ("la_ab", "A/B the hero line"),
    ]),
    ("site", "Search & site", "Search", [
        ("si_query", "Own “AI cofounder” queries"),
        ("si_clever", "The landing page is too clever"),
        ("si_vs", "Answer “agency vs Allya”"),
        ("si_bounce", "Fix the 6-second bounce"),
        ("si_gpt", "Comparison page vs ChatGPT"),
    ]),
    ("community", "Community & partners", "Community", [
        ("cm_groups", "Founder WhatsApp groups"),
        ("cm_accel", "Co-post with an accelerator"),
        ("cm_proof", "Ask Mili for the 28-task story"),
        ("cm_ama", "Host a 20-founder AMA"),
        ("cm_ref", "Referral: a month free, both ways"),
    ]),
    ("paid", "Paid & experiments", "Paid", [
        ("pd_meta", "Test ₹500/day on Meta"),
        ("retarget", "Retarget the pricing page"),
        ("pd_bleed", "Kill the keyword bleed"),
        ("pd_creative", "Creative: the 11pm line"),
        ("pd_cac", "Only spend after CAC proof"),
    ]),
]

STUB_BRANCHES = {
    "hiring": [
        ("hi_pipe", "Pipeline", "Pipeline", [
            ("screening", "6 candidates to screen"),
            ("shortlist", "Hire a designer first"),
            ("hi_ref", "Referrals beat job boards"),
        ]),
        ("hi_int", "Interviewing", "Interviews", [
            ("hi_founder", "Add a founder round"),
            ("hi_take", "Kill the take-home"),
            ("hi_worst", "Ask about their worst week"),
        ]),
        ("hi_on", "Onboarding", "Onboarding", [
            ("jd-posted", "Day-one checklist"),
            ("hi_buddy", "A buddy for week one"),
            ("hi_book", "Write the handbook later"),
        ]),
        ("hi_comp", "Team & comp", "Comp", [
            ("hi_band", "Equity band for hire #3"),
            ("hi_contract", "Contractor first, then full-time"),
            ("hi_range", "Publish the salary range"),
        ]),
    ],
    "pr": [
        ("pr_list", "Press list", "List", [
            ("presslist", "Refresh the press list"),
            ("pr_warm", "3 reporters to warm up"),
            ("pr_dead", "Drop the dead contacts"),
        ]),
        ("pr_angle", "Story angles", "Angles", [
            ("pitch", "Pitch the pivot story"),
            ("pr_price", "The ₹2,000 angle"),
            ("pr_13", "13 campaigns, month one"),
        ]),
        ("pr_rel", "Relationships", "Relations", [
            ("pr_reply", "Reply before you pitch"),
            ("pr_voice", "Founder voice, not PR-speak"),
            ("pr_coffee", "One coffee a week"),
        ]),
        ("pr_cov", "Coverage", "Coverage", [
            ("coverage", "Follow up: TechCrunch"),
            ("pr_reuse", "Turn coverage into a post"),
            ("pr_release", "Nobody reads a press release"),
        ]),
    ],
    "sales": [
        ("sa_pipe", "Pipeline", "Pipeline", [
            ("leads", "7 warm leads to call"),
            ("crm", "Clean up the CRM"),
            ("sa_refer", "Push referrals next"),
        ]),
        ("sa_out", "Outreach", "Outreach", [
            ("sa_warm", "Warm beats cold, always"),
            ("sa_signup", "Reply to every signup"),
            ("sa_seq", "Stop the 7-email sequence"),
        ]),
        ("sa_price", "Pricing", "Pricing", [
            ("sa_annual", "Test annual pricing"),
            ("sa_first", "Say the ₹2,000 first"),
            ("sa_disc", "Nobody asked for a discount"),
        ]),
        ("sa_ret", "Retention", "Retention", [
            ("winback", "Win back churned users"),
            ("sa_quiet", "Call the quiet ones"),
            ("sa_month2", "Month two is where you lose them"),
        ]),
    ],
    "ops": [
        ("op_time", "Time", "Time", [
            ("op_fri", "Protect deep-work Fridays"),
            ("op_standup", "Kill the standup"),
            ("op_batch", "Batch the calls"),
        ]),
        ("op_money", "Money", "Money", [
            ("hosting", "Cut hosting costs"),
            ("runway", "Runway is 11 months"),
            ("op_annual", "Test annual pricing"),
        ]),
        ("op_dec", "Decisions", "Decisions", [
            ("pricing-memo", "Write the pricing memo"),
            ("op_written", "Decisions in writing, always"),
            ("op_revisit", "Revisit in 30 days"),
        ]),
        ("op_tools", "Tools", "Tools", [
            ("op_one", "One tool per job"),
            ("op_cancel", "Cancel what you don’t open"),
            ("op_export", "Export everything monthly"),
        ]),
    ],
}

# marketing weaves its directions together; the stubs stay a clean tree
MARKETING_LINKS = [
    ("st_fast", "la_ab"), ("st_price", "ct_memo"), ("hero", "si_clever"),
    ("st_seam", "ct_28"), ("shorts", "reel"), ("ct_faq", "si_vs"),
    ("ct_28", "cm_proof"), ("so_thread", "la_receipts"), ("so_ugly", "ct_diary"),
    ("so_reply", "cm_groups"), ("warmup", "em_back"), ("newsletter", "la_receipts"),
    ("em_ps", "so_reply"), ("la_free", "st_price"), ("la_invite", "cm_accel"),
    ("si_bounce", "retarget"), ("si_gpt", "st_fast"), ("pd_cac", "la_free"),
    ("pd_creative", "reel"), ("cm_ref", "em_back"), ("pd_meta", "pd_cac"),
]

# What the company brain holds under each service: a few of the live thoughts
# you'll find in full once you go inside. Same ids and same words as the floor
# below, so the two views agree — and the ones mirroring a work item breathe.
WORKSPACE_LEAVES: dict[str, list[tuple[str, str]]] = {
    "marketing": [
        ("newsletter", "Next week’s newsletter"),
        ("reel", "Reel: the day-one story"),
        ("shorts", "Cut the demo into shorts"),
        ("st_fast", "Own “fast”, not “cheap”"),
    ],
    "hiring": [
        ("screening", "6 candidates to screen"),
        ("shortlist", "Hire a designer first"),
        ("hi_founder", "Add a founder round"),
    ],
    "pr": [
        ("presslist", "Refresh the press list"),
        ("pitch", "Pitch the pivot story"),
        ("pr_warm", "3 reporters to warm up"),
    ],
    "sales": [
        ("leads", "7 warm leads to call"),
        ("crm", "Clean up the CRM"),
        ("sa_refer", "Push referrals next"),
    ],
    "ops": [
        ("pricing-memo", "Write the pricing memo"),
        ("hosting", "Cut hosting costs"),
        ("op_fri", "Protect deep-work Fridays"),
    ],
}

# a few strands across services, so the company reads as a web and not a fan
WORKSPACE_LINKS = [
    ("newsletter", "presslist"),
    ("st_fast", "pitch"),
    ("leads", "reel"),
    ("crm", "pricing-memo"),
    ("shortlist", "hosting"),
    ("pr_warm", "sa_refer"),
]


def _workspace_nodes() -> list[dict]:
    nodes = [_node("co", "Your company", 0, "core")]
    for s in SERVICE_IDS:
        nodes.append(_node(s, SURFACES[s]["label"], 1, s, "co", surface=s))
        for lid, label in WORKSPACE_LEAVES[s]:
            nodes.append(_node(lid, label, 2, s, s, work=lid if lid in WORK_IDS else None))
    return nodes


BRAINS: dict[str, dict] = {
    "workspace": {
        "surface_id": "workspace",
        "layout": "web",
        "anchor_id": "co",
        "nodes": _workspace_nodes(),
        "links": WORKSPACE_LINKS,
    },
    "marketing": {
        "surface_id": "marketing",
        "layout": "spray",
        "anchor_id": "marketing",
        "nodes": _branch("marketing", MARKETING_BRANCHES),
        "links": MARKETING_LINKS,
    },
    **{
        s: {
            "surface_id": s,
            "layout": "spray",
            "anchor_id": s,
            "nodes": _branch(s, STUB_BRANCHES[s]),
            "links": [],
        }
        for s in ["hiring", "pr", "sales", "ops"]
    },
}


# ---- work --------------------------------------------------------------

def _w(wid, sid, status, origin, **kw):
    return {"id": wid, "surface_id": sid, "status": status, "origin": origin, "undoable": False, **kw}


WORK: list[dict] = [
    _w("newsletter", "marketing", "needs-you", "expert", who="A", who_name="Allya",
       who_role="with your PR expert",
       say="Next week’s newsletter is drafted around the SurferSearcher result — 13 campaigns in month one. Your PR expert’s edits are in. Read it before it ships?"),
    _w("reel", "marketing", "needs-you", "expert", who="A", who_name="Allya",
       who_role="with your brand expert",
       say="Three cuts of the day-one story, 22 seconds each. Your brand expert picked the one that doesn’t explain itself. Pick a cut and it goes out Wednesday."),
    _w("shorts", "marketing", "running", "agent", title="Cutting the demo into 6 shorts",
       meta="agent · 4 rendered, captions next"),
    _w("warmup", "marketing", "running", "agent", title="Warming 200 addresses for the founder list",
       meta="agent · day 4 of 14 · 0 bounces"),
    _w("hero", "marketing", "running", "expert",
       title="Landing hero — 5 variants against “own fast, not cheap”",
       meta="expert · brand expert on the final pass"),
    _w("listening", "marketing", "running", "agent", title="Watching 3 competitor launches for openings",
       meta="agent · nothing worth waking you for yet"),
    _w("linkedin", "marketing", "shipped", "agent", title="LinkedIn post shipped — the pivot lesson",
       meta="7:05am · 1.4k views, 11 replies, 2 demo asks"),
    _w("retarget", "marketing", "shipped", "agent",
       title="Retargeting audience rebuilt — 1,900 pricing-page visitors",
       meta="6:20am · brand expert spot-checked the creative"),

    _w("shortlist", "hiring", "needs-you", "expert", who="A", who_name="Allya",
       who_role="with your hiring expert",
       say="Six through the first screen for the ops role. Your hiring expert sat in on the top two and held Thursday 3pm and 4pm. Want to see the ranking?"),
    _w("screening", "hiring", "running", "agent", title="Screening 6 candidates for the ops role",
       meta="agent · ranking against your approved JD"),
    _w("jd-posted", "hiring", "shipped", "agent", title="Ops-hire JD written and posted to three boards",
       meta="7:15am · 6 already through first screen"),

    _w("presslist", "pr", "needs-you", "expert", who="A", who_name="Allya",
       who_role="with your PR expert",
       say="The press list is rebuilt — 22 journalists who actually cover founder tooling in India. Your PR expert cut 9 who’ve gone quiet. Approve it and I’ll start warming them."),
    _w("pitch", "pr", "running", "expert", title="Pitching the pivot story to 3 reporters",
       meta="expert · personalised, not a blast"),
    _w("coverage", "pr", "shipped", "agent", title="TechCrunch follow-up sent with the 13-campaign number",
       meta="6:50am · no reply yet, that’s normal"),

    _w("leads", "sales", "needs-you", "agent", who="A", who_name="Allya",
       who_role="from last week’s signups",
       say="40 signups enriched, 7 are worth a call this week — same stage, same problem as SurferSearcher was. Want the list and what to open with?"),
    _w("crm", "sales", "running", "agent", title="CRM cleanup — merging 41 stale leads",
       meta="agent · sales expert spot-checks before it writes"),
    _w("winback", "sales", "shipped", "agent", title="Win-back note sent to 12 churned users",
       meta="6:05am · 3 opened twice"),

    _w("pricing-memo", "ops", "needs-you", "expert", who="A", who_name="Allya",
       who_role="with your ops expert",
       say="The pricing memo is drafted — ₹2,000, first month free, and why you don’t discount. It’s the thing you keep re-explaining. Read it before it goes in the handbook?"),
    _w("hosting", "ops", "running", "agent", title="Auditing hosting spend across 4 providers",
       meta="agent · ₹6,400/mo of it looks unused"),
    _w("runway", "ops", "shipped", "agent", title="Runway recalculated — 11 months at current burn",
       meta="5:40am · no action needed yet"),
]

WORK_SEED = {w["id"]: dict(w) for w in WORK}

SUMMARY = {
    "workspace": {"shipped_earlier": 12, "spend_label": "₹0", "spend_note": "spent · first month free"},
    **{s: {"shipped_earlier": 4, "spend_label": "₹0", "spend_note": "spent · first month free"} for s in SERVICE_IDS},
}
SUMMARY["marketing"]["shipped_earlier"] = 12


# ---- review sheets (only for the items that need you) ------------------

REVIEWS: dict[str, dict] = {
    "newsletter": {
        "head": {"avatar": "A", "human": False, "who": "Allya", "role": "with your PR expert",
                 "line": "Next week’s newsletter. Read it, then approve — nothing sends until you do."},
        "trail": [
            {"kind": "agent", "text": "Drafted by agent", "time": "6:12am"},
            {"kind": "expert", "text": "Your PR expert edited 2 lines", "time": "6:58am"},
            {"kind": "you", "text": "Waiting on you — nothing ships without this step"},
        ],
        "diff": [
            {"old": "We ran 13 marketing campaigns for SurferSearcher last month",
             "new": "The agency did 13 campaigns. In one month."},
            {"old": "Our AI-powered platform can streamline your marketing",
             "new": "You didn’t start a company to write newsletters at 11pm."},
        ],
        "drafts": [
            {"kicker": "Subject line", "title": "The agency did 13 campaigns. In one month.",
             "body": "Leads with the SurferSearcher number. No adjectives — the figure carries it.",
             "tags": ["open rate angle", "A/B ready"]},
            {"kicker": "Body", "title": "You didn’t start a company to write newsletters at 11pm.",
             "body": "Three short paragraphs. One idea each. Ends on your actual offer, not a pitch.",
             "tags": ["your voice", "expert edited"]},
            {"kicker": "P.S.", "title": "Reply with one word — the thing eating your week.",
             "body": "Asks for a single reply so you start real conversations, not track opens.",
             "tags": ["1 reply goal"]},
        ],
        "note": "After you approve, it holds for 10 minutes before actually sending — you can pull it back.",
        "approve_label": "Approve — schedule it",
    },
    "reel": {
        "head": {"avatar": "A", "human": True, "who": "Allya", "role": "with your brand expert",
                 "line": "Three cuts of the day-one story. Pick one — nothing posts until you do."},
        "trail": [
            {"kind": "agent", "text": "Agent cut 3 versions from the demo recording", "time": "5:48am"},
            {"kind": "expert", "text": "Your brand expert killed the voiceover on two", "time": "7:30am"},
            {"kind": "you", "text": "Waiting on you — you pick the cut, always"},
        ],
        "diff": [
            {"old": "“Allya is an AI-powered operational platform for founders”",
             "new": "No voiceover. Just the screen, and the clock in the corner."},
            {"old": "Ends on the logo", "new": "Ends on the ₹2,000. The number is the hook."},
        ],
        "drafts": [
            {"kicker": "Cut #1 — 22s", "title": "Day one, sped up: onboarding to first shipped task.",
             "body": "Screen only, no talking. The timestamp in the corner does the arguing.",
             "tags": ["no VO", "expert pick"]},
            {"kicker": "Cut #2 — 24s", "title": "“You didn’t start a company to write newsletters at 11pm.”",
             "body": "One line on black, then the work panel filling up. Ends on the price.",
             "tags": ["your voice", "best hook"]},
            {"kicker": "Cut #3 — 19s", "title": "Just the work panel, all day, in 19 seconds.",
             "body": "The most honest one. Weakest opening three seconds — it loses the scroll.",
             "tags": ["honest", "weak open"]},
        ],
        "note": "Approving schedules it for Wednesday 8am. It holds for 10 minutes — you can pull it back.",
        "approve_label": "Approve cut #2 — post Wednesday",
    },
    "shortlist": {
        "head": {"avatar": "P", "human": True, "who": "Your hiring expert", "role": None,
                 "line": "Six through the first screen. Here are the two I’d spend your time on."},
        "trail": [
            {"kind": "agent", "text": "Agent screened 6 candidates overnight", "time": "5:30am"},
            {"kind": "expert", "text": "Your hiring expert sat in on the top two", "time": "8:15am"},
            {"kind": "you", "text": "Waiting on you — your call, always"},
        ],
        "diff": [],
        "drafts": [
            {"kicker": "#1", "title": "Ran ops solo at a seed-stage fintech for two years.",
             "body": "Did the messy version of this job with no team. Strong on the parts you hate.",
             "tags": ["ops", "seed-stage", "available in 2 wks"]},
            {"kicker": "#2", "title": "Built the hiring pipeline at a four-person startup.",
             "body": "Less ops depth, more range. Would grow into it fast. Worth the second slot.",
             "tags": ["generalist", "fast start"]},
        ],
        "note": "The other four weren’t a fit for the JD you approved. I can share the notes if you want them.",
        "approve_label": "Book both interviews",
    },
    "presslist": {
        "head": {"avatar": "A", "human": False, "who": "Allya", "role": "with your PR expert",
                 "line": "22 journalists, matched to what you actually do. Approve before I warm them."},
        "trail": [
            {"kind": "agent", "text": "Agent built the list from 140 recent bylines", "time": "4:55am"},
            {"kind": "expert", "text": "Your PR expert cut 9 who’ve gone quiet", "time": "7:40am"},
            {"kind": "you", "text": "Waiting on you — nobody gets contacted without this"},
        ],
        "diff": [],
        "drafts": [
            {"kicker": "Tier 1 — 6 names", "title": "Cover founder tooling in India, monthly.",
             "body": "Worth a personal note from you, not from me.", "tags": ["warm first"]},
            {"kicker": "Tier 2 — 16 names", "title": "Adjacent beats: SMB software, AI adoption.",
             "body": "I’ll warm these with replies before any pitch goes out.", "tags": ["agent-warmed"]},
        ],
        "note": "Approving starts the warming, not the pitching. Pitches come back to you separately.",
        "approve_label": "Approve the list",
    },
    "leads": {
        "head": {"avatar": "A", "human": False, "who": "Allya", "role": "from last week’s signups",
                 "line": "Seven worth calling, and what to open with. Approve and I’ll draft the notes."},
        "trail": [
            {"kind": "agent", "text": "Agent enriched 40 signups", "time": "6:30am"},
            {"kind": "expert", "text": "Your sales expert ranked them by fit, not by size", "time": "8:05am"},
            {"kind": "you", "text": "Waiting on you — you call, I prepare"},
        ],
        "diff": [],
        "drafts": [
            {"kicker": "Top 3", "title": "Same stage and same problem SurferSearcher had.",
             "body": "Pre-revenue, solo, already tried an agency and bounced off the price.",
             "tags": ["best fit"]},
            {"kicker": "Next 4", "title": "Worth a call, less urgent.",
             "body": "Early revenue, currently doing it themselves at 11pm.", "tags": ["this week"]},
        ],
        "note": "Nothing is sent to any of them until you approve the opener.",
        "approve_label": "Approve — draft the openers",
    },
    "pricing-memo": {
        "head": {"avatar": "A", "human": False, "who": "Allya", "role": "with your ops expert",
                 "line": "The pricing memo. Say it once here, stop re-explaining it everywhere."},
        "trail": [
            {"kind": "agent", "text": "Agent drafted from 20 of your own answers", "time": "6:02am"},
            {"kind": "expert", "text": "Your ops expert tightened the discount section", "time": "7:20am"},
            {"kind": "you", "text": "Waiting on you — it’s your number"},
        ],
        "diff": [],
        "drafts": [
            {"kicker": "The number", "title": "₹2,000 a month. First month free.",
             "body": "Stated first, not buried. The free month is the trial, so there isn’t a second one.",
             "tags": ["canonical"]},
            {"kicker": "Discounts", "title": "No. And here’s the sentence to say instead.",
             "body": "A discount now is a renegotiation every month afterwards.", "tags": ["ops expert"]},
        ],
        "note": "Approving files it in the handbook and reuses it on the pricing page.",
        "approve_label": "Approve the memo",
    },
}


# ---- conversation ------------------------------------------------------

def _msg(mid, speaker, text, tag=None):
    return {"id": mid, "speaker": speaker, "text": text, "tag": tag}


CONVERSATIONS: dict[str, dict] = {
    "workspace": {
        "opening": {
            "messages": [_msg("w-open", "allya",
                              "Morning. While you slept, three things moved — two shipped, one’s waiting on your eyes. I never send anything without you.")],
            "chips": [
                {"label": "Review the newsletter", "action": "review", "value": "newsletter"},
                {"label": "Where’s the ops hire?", "action": "send", "value": "Where’s the ops hire?"},
            ],
        },
        "scripts": [
            (["news", "letter", "campaign", "market"], {
                "messages": [
                    _msg("w-n1", "allya", "That lives on the marketing floor — I’ll open it. Next week’s is built around the SurferSearcher result: 13 campaigns in month one."),
                    _msg("w-n2", "allya", "Subject lines, the body, and a P.S. that asks for one reply. Your PR expert already tightened two lines."),
                ],
                "chips": [{"label": "Show me the draft", "action": "review", "value": "newsletter"}],
            }),
            (["hir", "candidate", "screen", "interview", "ops hire"], {
                "messages": [
                    _msg("w-h1", "allya", "Six people are through the first screen for the ops role. I ranked them against the JD you approved, not against a résumé template."),
                    _msg("w-h2", "human", "I sat in on the top two — both worth 20 minutes. I’ve held Thursday 3pm and 4pm.", "Your hiring expert"),
                ],
                "chips": [{"label": "See the ranking", "action": "review", "value": "shortlist"}],
            }),
        ],
        "fallback": {
            "messages": [_msg("w-f", "allya",
                              "Noted. I’ll take the first pass and it’ll show up in your work panel before anything ships — you approve, then it goes out.")],
            "chips": [],
        },
    },
    "marketing": {
        "opening": {
            "messages": [_msg("m-open", "allya",
                              "Marketing ran overnight. Two things shipped, four are still moving, and two want your eyes before anything is published.")],
            "chips": [
                {"label": "What’s working this week?", "action": "send", "value": "What’s working this week?"},
                {"label": "Review the newsletter", "action": "review", "value": "newsletter"},
            ],
        },
        "scripts": [
            (["news", "letter", "email"], {
                "messages": [
                    _msg("m-n1", "allya", "Good one to get ahead of. I’ll build next week’s around the SurferSearcher result — 13 campaigns in month one reads better than anything I could invent."),
                    _msg("m-n2", "allya", "I broke it into three: subject lines, the body, and a P.S. that asks for one reply. It’s waiting in your work panel."),
                ],
                "chips": [{"label": "Show me the draft", "action": "review", "value": "newsletter"}],
            }),
            (["reel", "short", "video", "cut", "demo"], {
                "messages": [
                    _msg("m-r1", "allya", "The demo recording gave me six usable shorts. Three are cut and captioned; the other three need the pricing screen re-shot."),
                    _msg("m-r2", "human", "I killed the voiceover on two of them. The screen and the clock make the argument — talking over it makes it a pitch.", "Your brand expert"),
                ],
                "chips": [{"label": "Show me the cuts", "action": "review", "value": "reel"}],
            }),
            (["working", "perform", "week", "number", "result"], {
                "messages": [
                    _msg("m-w1", "allya", "Three things are working: story-format sends open 18% better than product-format ones, reels out-save static posts 4:1, and “show me” out-clicks “learn more” three to one."),
                    _msg("m-w2", "allya", "One isn’t: the landing hero. Six-second bounce, and the word “platform” is on it four times — you’ve never said that word out loud. Your brand expert is on the rewrite."),
                ],
                "chips": [{"label": "Show me the newsletter", "action": "review", "value": "newsletter"}],
            }),
        ],
        "fallback": {
            "messages": [_msg("m-f", "allya",
                              "Noted. I’ll take the first pass and it’ll show up in your work panel before anything is published — you approve, then it goes out.")],
            "chips": [],
        },
    },
}

# the stub services share one shape: an opening beat and a single fallback
_STUB_OPENERS = {
    "hiring": ("Screening ran overnight — six through the first round. One shortlist is waiting on you.", "shortlist"),
    "pr": ("The press list is rebuilt and one pitch is in flight. The list needs your approval before anyone hears from us.", "presslist"),
    "sales": ("40 signups enriched overnight. Seven are worth a call this week — that list needs your eyes.", "leads"),
    "ops": ("Quiet night, which is correct. The pricing memo is drafted and waiting on you.", "pricing-memo"),
}
for _sid, (_text, _work) in _STUB_OPENERS.items():
    CONVERSATIONS[_sid] = {
        "opening": {
            "messages": [_msg(f"{_sid}-open", "allya", _text)],
            "chips": [{"label": "Show me", "action": "review", "value": _work}],
        },
        "scripts": [],
        "fallback": {
            "messages": [_msg(f"{_sid}-f", "allya",
                              "Noted. I’ll take the first pass and it’ll land in your work panel before anything happens — you approve, then it moves.")],
            "chips": [],
        },
    }


# ---- knowledge ---------------------------------------------------------

def _f(fid, sid, text, period, mismatch=False):
    ago = {"today": 0, "yesterday": DAY, "last-week": DAY * 4}[period]
    return {"id": fid, "surface_id": sid, "text": text, "period": period,
            "ts": NOW - ago, "flagged": False, "mismatch": mismatch, "source": "observed"}


FACTS: list[dict] = [
    _f("k1", "workspace", "You respond to PR approvals faster than hiring decisions", "today"),
    _f("k2", "workspace", "Newsletter open rate jumped 18% after switching to story format", "today"),
    _f("k3", "workspace", "Your ops role JD got 6 applicants in 4 hours — above average", "today"),
    _f("k4", "workspace", "You haven’t looked at the sales pipeline in 5 days", "today", True),
    _f("k5", "workspace", "Morning decisions stick — your afternoon reversals are 3× higher", "today"),
    _f("k6", "workspace", "You approved the investor update without a single edit", "yesterday"),
    _f("k7", "workspace", "You asked about annual pricing — might be exploring it", "yesterday", True),
    _f("k8", "workspace", "You shipped 14 items — 9 agent, 5 expert-reviewed", "last-week"),
    _f("k9", "workspace", "Average approval time dropped from 6h to 2h", "last-week"),

    _f("m1", "marketing", "Story-format sends open 18% better than product-format ones", "today"),
    _f("m2", "marketing", "Reels out-save static posts 4:1 — the demo cut is your best asset", "today"),
    _f("m3", "marketing", "“Show me” out-clicks “Learn more” 3:1 on every surface you’ve tested", "today"),
    _f("m4", "marketing", "Pricing is your second-most-read page. People check the number first.", "today"),
    _f("m5", "marketing", "You haven’t posted on LinkedIn in 6 days — the replies dried up on day 3", "today", True),
    _f("m6", "marketing", "Posts published before 9am get 2× the replies of afternoon ones", "today"),
    _f("m7", "marketing", "The word “platform” appears 4× on the landing page and 0× in how you talk", "yesterday"),
    _f("m8", "marketing", "Two prospects quoted “fast, not cheap” back to you unprompted", "yesterday"),
    _f("m9", "marketing", "The 13-campaigns line converts better than any adjective you’ve written", "yesterday"),
    _f("m10", "marketing", "You skipped the paid experiment again — deprioritising spend until CAC is proven?", "yesterday", True),
    _f("m11", "marketing", "9 marketing items shipped — 7 agent, 2 expert-reviewed", "last-week"),
    _f("m12", "marketing", "Cold outreach replies doubled once the warm-up hit day 10", "last-week"),
    _f("m13", "marketing", "Bounce on the homepage sits at 6 seconds — the hero is doing the losing", "last-week"),
    _f("m14", "marketing", "Your best-performing post was the ugly first draft, not the polished one", "last-week"),

    _f("h1", "hiring", "Your ops JD got 6 applicants in 4 hours — above average for the role", "today"),
    _f("h2", "hiring", "You take 3× longer on hiring decisions than on anything else", "today", True),
    _f("h3", "hiring", "Referral candidates reach the second round 4× more often than board ones", "yesterday"),
    _f("h4", "hiring", "The take-home lost you two candidates who’d already passed the screen", "last-week"),

    _f("p1", "pr", "Reporters who got a reply from you first answer 3× more often", "today"),
    _f("p2", "pr", "9 of 31 contacts on the old list haven’t published in 6 months", "today"),
    _f("p3", "pr", "The pivot story gets follow-up questions; the funding angle doesn’t", "yesterday", True),
    _f("p4", "pr", "Coverage drives signups for about 48 hours, then it’s flat", "last-week"),

    _f("s1", "sales", "7 of last week’s 40 signups match the SurferSearcher profile exactly", "today"),
    _f("s2", "sales", "You haven’t opened the pipeline in 5 days", "today", True),
    _f("s3", "sales", "Calls booked within 24h of signup close 2× more often", "yesterday"),
    _f("s4", "sales", "Nobody has asked for a discount since you started leading with ₹2,000", "last-week"),

    _f("o1", "ops", "₹6,400/mo of hosting spend has had no traffic in 30 days", "today"),
    _f("o2", "ops", "Fridays with no meetings produce 2× the shipped work", "today"),
    _f("o3", "ops", "You re-explain pricing about 4 times a week in writing", "yesterday", True),
    _f("o4", "ops", "Runway is 11 months at current burn — unchanged for 3 weeks", "last-week"),
]

FACT_SEED = {f["id"]: dict(f) for f in FACTS}


# ---- schedule ----------------------------------------------------------

SCHEDULES: dict[str, list[dict]] = {
    "workspace": [
        {"id": "w1", "when": "11:00", "what": "Investor call — Meridian", "pill": "notes ready", "quiet": False},
        {"id": "w2", "when": "15:00", "what": "Ops interview — first of two", "pill": "brief ready", "quiet": False},
        {"id": "w3", "when": "—", "what": "Nothing else. I kept your afternoon clear on purpose.", "pill": None, "quiet": True},
    ],
    "marketing": [
        {"id": "m1", "when": "Tue", "what": "Newsletter — the SurferSearcher angle", "pill": "waiting on you", "quiet": False},
        {"id": "m2", "when": "Wed", "what": "Reel #1 — the day-one story", "pill": "cut, needs a pick", "quiet": False},
        {"id": "m3", "when": "Thu", "what": "Pricing memo goes public — ₹2,000, in the open", "pill": "draft ready", "quiet": False},
        {"id": "m4", "when": "Fri", "what": "Nothing scheduled. I kept it clear for launch prep.", "pill": None, "quiet": True},
    ],
    "hiring": [
        {"id": "h1", "when": "Thu", "what": "Ops interview — 3pm and 4pm", "pill": "held", "quiet": False},
        {"id": "h2", "when": "Fri", "what": "Decision on the shortlist", "pill": "your call", "quiet": False},
        {"id": "h3", "when": "—", "what": "Nothing else this week.", "pill": None, "quiet": True},
    ],
    "pr": [
        {"id": "p1", "when": "Tue", "what": "Warm-up replies go out to tier 1", "pill": "waiting on you", "quiet": False},
        {"id": "p2", "when": "Thu", "what": "Pivot-story pitch — 3 reporters", "pill": "drafted", "quiet": False},
        {"id": "p3", "when": "—", "what": "No embargoes, nothing time-boxed.", "pill": None, "quiet": True},
    ],
    "sales": [
        {"id": "s1", "when": "Tue", "what": "7 warm calls — openers drafted", "pill": "waiting on you", "quiet": False},
        {"id": "s2", "when": "Wed", "what": "CRM cleanup writes back", "pill": "running", "quiet": False},
        {"id": "s3", "when": "—", "what": "No outbound sequences this week, on purpose.", "pill": None, "quiet": True},
    ],
    "ops": [
        {"id": "o1", "when": "Wed", "what": "Hosting audit lands", "pill": "running", "quiet": False},
        {"id": "o2", "when": "Fri", "what": "Deep work — no meetings", "pill": "protected", "quiet": False},
        {"id": "o3", "when": "—", "what": "Nothing else. That’s the point of this floor.", "pill": None, "quiet": True},
    ],
}


# ---- what approving / undoing an item says -----------------------------

OUTCOMES: dict[str, dict] = {
    "newsletter": {
        "title": "Newsletter approved — goes out Tuesday 9am",
        "meta": "holds 10 min before sending",
        "toast": "Scheduled. You have 10 minutes to pull it back.",
        "reply": "Scheduled for Tuesday 9am. It holds for 10 minutes in case you change your mind — after that I’ll watch the replies and pull anything worth your time into here.",
    },
    "reel": {
        "title": "Reel #2 approved — posts Wednesday 8am",
        "meta": "holds 10 min · cross-posts to LinkedIn",
        "toast": "Scheduled. You have 10 minutes to pull it back.",
        "reply": "Wednesday 8am, then LinkedIn an hour later. I’ll watch the first two hours and tell you if the opening three seconds are losing people.",
    },
    "shortlist": {
        "title": "Both interviews booked — Thursday 3pm and 4pm",
        "meta": "each got a short note on the role",
        "toast": "Booked. Thursday 3 & 4pm are on your calendar.",
        "reply": "Done. Both are booked, and I sent each a short note so Thursday isn’t cold.",
    },
    "presslist": {
        "title": "Press list approved — 22 journalists, warming starts",
        "meta": "replies first, pitches later",
        "toast": "Approved. Warming starts, pitching doesn’t.",
        "reply": "Warming starts today — replies and reads, no pitches. Any actual pitch comes back to you first.",
    },
    "leads": {
        "title": "Openers drafted for 7 warm leads",
        "meta": "yours to send, not mine",
        "toast": "Drafted. Nothing sends without you.",
        "reply": "Openers are in your panel. I didn’t send anything — these are calls you make, I just made them easy to start.",
    },
    "pricing-memo": {
        "title": "Pricing memo approved — filed and reused",
        "meta": "now the canonical answer",
        "toast": "Filed. It’s the canonical answer now.",
        "reply": "Filed. I’ll use it verbatim anywhere pricing comes up, so you stop re-explaining it four times a week.",
    },
}

UNDO_REPLY = "Pulled it back — nothing went out. It’s in your queue again; no harm done."
REVISION_REPLY = "Tell me what’s off and I’ll have a new pass in your panel within the hour. Nothing moves in the meantime."


# ---- the gate ----------------------------------------------------------
#
# Dummy sign-in: a couple of seeded accounts and one shared demo password
# (override with DEMO_PASSWORD). Anything else is a 401, which is what drives
# the error state the sign-in design was built around. No hashing, no
# sessions table, no expiry — tokens live in a dict until the process restarts.

DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "allya")

USERS: dict[str, dict] = {
    "sanshat@zeroto10.ai": {
        "id": "u_founder",
        "email": "sanshat@zeroto10.ai",
        "name": "Sanshat Bhatia",
        "company": "ZeroTo10",
    },
    "demo@zeroto10.ai": {
        "id": "u_demo",
        "email": "demo@zeroto10.ai",
        "name": "Demo founder",
        "company": "ZeroTo10",
    },
}

# token -> user id, for as long as the process lives
TOKENS: dict[str, str] = {}

# The graph behind the gate: not the workspace brain (departments and live
# work) but the company as an outsider meets it.
GATE_BRAIN_NODES = [
    _node("co", "ZeroTo10", 0, "core"),
    _node("product", "Product", 1, "product", "co"),
    *[_node(f"p{i}", lbl, 2, "product", "product")
      for i, lbl in enumerate(["Allya", "Agents", "Experts", "Onboarding"], 1)],
    _node("market", "Market", 1, "market", "co"),
    *[_node(f"m{i}", lbl, 2, "market", "market")
      for i, lbl in enumerate(["Who it is for", "Market size", "Competition"], 1)],
    _node("traction", "Traction", 1, "traction", "co"),
    *[_node(f"t{i}", lbl, 2, "traction", "traction")
      for i, lbl in enumerate(["Stage", "Proof", "Roadmap"], 1)],
    _node("model", "Model", 1, "model", "co"),
    *[_node(f"o{i}", lbl, 2, "model", "model")
      for i, lbl in enumerate(["Pricing", "Unit economics", "Go-to-market"], 1)],
    _node("team", "Team", 1, "team", "co"),
    *[_node(f"e{i}", lbl, 2, "team", "team")
      for i, lbl in enumerate(["Founders", "Origin"], 1)],
]

# three strands that skip the hub, so it reads as a business and not a filing
# cabinet: what you sell prices itself, what you've proven is what the market
# rewarded, and the model is what the traction pays for
GATE = {
    "headline": "Welcome back to ZeroTo10.",
    "lede": "Sign in and Allya picks up where you left off — the work in flight, the decisions waiting on you, the whole company map.",
    "footnote": "We’re currently rolling out ZeroTo10.ai to selected users. If you’d like an account, please apply on",
    "footnote_link_label": "this link",
    "footnote_link_href": "https://www.linkedin.com/in/sanshat-bhatia",
    "brain": {
        "surface_id": "gate",
        "layout": "cluster",
        "anchor_id": "co",
        "nodes": GATE_BRAIN_NODES,
        "links": [("product", "model"), ("market", "traction"), ("model", "traction")],
    },
}
