"""In-memory seed for the dummy API.

Everything the two brain surfaces render lives here. Swap these dicts for real
queries and the contract in models.py does not change.

House rules carried over from the product: leaves are live thoughts, not
service names; proof points are the real ones (SurferSearcher's 13 campaigns,
Mili's 28 tasks, ₹2,000/mo first month free); humans are referred to
generically — "your brand expert" — never by an invented name.
"""

import datetime
import re
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
    ("whatsapp", "WhatsApp", "WhatsApp", [
        ("wa_festive", "Festive offer — waiting on Meta"),
        ("wa_tier", "280 numbers off the 10k tier"),
        ("wa_quality", "Quality back to green"),
        ("wa_quiet", "Ask the quiet 30-day list one question"),
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
        ("newsletters", "Newsletters", "Newsletters", [
            ("nl_next", "The note that's waiting on the list"),
            ("nl_replies", "Every piece came from a reply"),
            ("nl_8am", "Reporters open you at 8am"),
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


# ---- calendar ----------------------------------------------------------
#
# Dated twins of the schedule above. Offsets are relative to today so the
# month always has something in it whenever this runs; the ones that mirror a
# work item carry its id, which is what makes a cell openable.

TODAY = datetime.date.today()


def _ce(eid, sid, off, when, minute, what, kind, origin="agent", pill=None, work=None, dur=0):
    return {
        "id": eid,
        "surface_id": sid,
        "date": (TODAY + datetime.timedelta(days=off)).isoformat(),
        "when": when,
        "start_minute": minute,
        "duration_min": dur,
        "what": what,
        "kind": kind,
        "origin": origin,
        "pill": pill,
        "work_id": work,
    }


CALENDAR: list[dict] = [
    # the company's own — not owned by any one floor
    _ce("c-runway", "workspace", -6, "09:30", 570, "Runway review — 11 months at current burn", "meeting", dur=45),
    _ce("c-retro", "workspace", -8, "09:00", 540, "Launch-week retro", "meeting", dur=60),
    _ce("c-invest", "workspace", 0, "11:00", 660, "Investor call — Meridian", "meeting", pill="notes ready", dur=45),
    _ce("c-ops", "workspace", 0, "15:00", 900, "Ops interview — first of two", "meeting", pill="brief ready", dur=45),
    _ce("c-allhands", "workspace", 3, "16:30", 990, "All-hands — the pivot, said once", "meeting", dur=30),
    _ce("c-board", "workspace", 9, "10:00", 600, "Board update goes out", "ship", pill="drafted"),

    _ce("cm-li", "marketing", 0, "07:05", 425, "LinkedIn post shipped — the pivot lesson", "ship", work="linkedin"),
    _ce("cm-ret", "marketing", 0, "06:20", 380, "Retargeting audience rebuilt", "ship", work="retarget"),
    _ce("cm-news", "marketing", 1, "09:00", 540, "Newsletter — the SurferSearcher angle", "ship",
        "expert", "waiting on you", "newsletter"),
    _ce("cm-reel", "marketing", 2, "08:00", 480, "Reel #1 — the day-one story", "ship",
        "expert", "needs a pick", "reel"),
    _ce("cm-shorts", "marketing", 2, "14:00", 840, "6 shorts land for review", "review", work="shorts"),
    _ce("cm-hero", "marketing", 4, "11:30", 690, "Landing hero — final pass with your brand expert", "review",
        "expert", None, "hero", 60),
    _ce("cm-warm", "marketing", 10, "All day", -1, "Warm-up finishes — 200 addresses", "ship", work="warmup"),

    _ce("ch-jd", "hiring", 0, "07:15", 435, "Ops-hire JD posted to three boards", "ship", work="jd-posted"),
    _ce("ch-int1", "hiring", 3, "15:00", 900, "Ops interview — candidate one", "meeting",
        "expert", "held", "shortlist", 45),
    _ce("ch-int2", "hiring", 3, "16:00", 960, "Ops interview — candidate two", "meeting",
        "expert", "held", "shortlist", 45),
    _ce("ch-dec", "hiring", 4, "12:00", 720, "Decision on the shortlist", "deadline", pill="your call"),

    _ce("cp-tc", "pr", 0, "06:50", 410, "TechCrunch follow-up sent", "ship", work="coverage"),
    _ce("cp-warm", "pr", 1, "10:00", 600, "Warm-up replies go out to tier 1", "ship",
        "expert", "waiting on you", "presslist"),
    _ce("cp-pitch", "pr", 3, "11:00", 660, "Pivot-story pitch — 3 reporters", "meeting",
        "expert", None, "pitch", 30),
    _ce("cp-embargo", "pr", 8, "All day", -1, "Embargo lifts on the funding note", "deadline"),

    _ce("cs-win", "sales", 0, "06:05", 365, "Win-back note sent to 12 churned users", "ship", work="winback"),
    _ce("cs-calls", "sales", 1, "13:00", 780, "7 warm calls — openers drafted", "meeting",
        "agent", "waiting on you", "leads", 90),
    _ce("cs-crm", "sales", 2, "All day", -1, "CRM cleanup writes back", "ship", work="crm"),
    _ce("cs-pipe", "sales", 7, "09:30", 570, "Pipeline review — the 7 worth a call", "meeting", dur=30),

    _ce("co-runway", "ops", 0, "05:40", 340, "Runway recalculated — 11 months", "ship", work="runway"),
    _ce("co-host", "ops", 2, "All day", -1, "Hosting audit lands", "review", work="hosting"),
    _ce("co-price", "ops", 3, "All day", -1, "Pricing memo goes into the handbook", "ship",
        "expert", "draft ready", "pricing-memo"),
    _ce("co-focus", "ops", 4, "All day", -1, "Deep work — no meetings", "focus", pill="protected"),
]

EMPTY_DAY = "Nothing on this day. I’ll keep it that way unless you tell me otherwise."


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


# ---- each floor's own onboarding ---------------------------------------
#
# The company onboarding maps the business. This is the floor-level one: four
# questions that make a service usable, in the same shape and the same voice.
# Which floors are set up lives here for as long as the process does.

ONBOARDED: dict[str, bool] = {s: False for s in SERVICE_IDS}
ANSWERS: dict[str, dict[str, str]] = {}


def _q(key, tag, sub, q, kind, cluster_label, learned, **kw):
    i = kw.pop("i", 1)
    return {
        "key": key, "tag": tag, "sub": sub, "q": q, "type": kind, "learned": learned,
        "cluster": {
            "id": key, "label": cluster_label, "group": f"b{i}",
            "leaves_from": kw.pop("leaves_from", "answer"),
            "leaves": kw.pop("leaves", []), "max_leaves": kw.pop("max_leaves", 4),
        },
        **kw,
    }


SERVICE_ONBOARDING: dict[str, dict] = {
    "marketing": {
        "title": "Set up marketing",
        "lede": "Four questions. I already know your company — this is the part that’s only about how the market hears you.",
        "cta": "Start",
        "synth": [
            "Reading how you reach people…",
            "Placing your story against your market…",
            "Choosing which channels are worth your week…",
            "Marketing is set up.",
        ],
        "done_title": "Marketing is yours now.",
        "done_lede": "The floor is filled in and the agents can start. Nothing publishes without you.",
        "done_cta": "Open marketing",
        "questions": [
            _q("channels", "Your channels", "Mapping where you show up",
               "Where does your marketing actually happen today? List everything, even the ones you’ve given up on.",
               "long", "Channels", "Mapped where your marketing happens", i=1,
               placeholder="e.g. LinkedIn, a newsletter nobody reads, one reel that did well…",
               example="LinkedIn posts, an email list of 400, and a landing page.",
               ack="Good — I can see where you already have ground, and where you don’t."),
            _q("story", "Your story", "Sharpening the one line",
               "In one line, what do you want people to say about you when you’re not in the room?",
               "short", "Story", "Learned the line you want repeated", i=2,
               placeholder="e.g. they ship faster than anyone that cheap",
               ack="That’s the sentence everything else has to earn. I’ll hold you to it."),
            _q("audience", "Who hears it", "Placing your audience",
               "Who are you trying to reach — and who are you happy to ignore?",
               "short", "Audience", "Know who you’re talking to", i=3,
               placeholder="e.g. solo founders pre-revenue; not enterprise",
               ack="Noted. Ignoring the wrong people is most of the work."),
            _q("spend", "The budget", "Sizing what’s possible",
               "How much are you spending on marketing right now?",
               "choice", "Spend", "Know what you can actually spend", i=4,
               options=["Nothing yet", "Under ₹10k a month", "₹10k–50k a month", "More than that"],
               leaves_from="fixed", leaves=["Paid", "Organic"],
               ack_by_option={
                   "Nothing yet": "Then everything I do starts organic. That’s the right order anyway.",
                   "Under ₹10k a month": "Small and testable. I won’t spend it until the organic version works.",
                   "₹10k–50k a month": "Enough to test properly. I’ll keep it honest against CAC.",
                   "More than that": "Then the question is what to stop, not what to start.",
               }),
        ],
    },
    "hiring": {
        "title": "Set up HR",
        "lede": "Four questions about who joins and how. It’s the part I can’t guess from your company alone.",
        "cta": "Start",
        "synth": ["Reading the roles…", "Learning your bar…", "Shaping day one…", "Hiring is set up."],
        "done_title": "Hiring is yours now.",
        "done_lede": "Screening can start. Nobody gets an offer without you.",
        "done_cta": "Open hiring",
        "questions": [
            _q("roles", "The roles", "Mapping who you need",
               "Who are you trying to hire in the next six months? Titles, or just what needs doing.",
               "long", "Roles", "Mapped the roles you need", i=1,
               placeholder="e.g. someone to run ops, a designer eventually, maybe a second engineer",
               ack="That’s enough to start ranking people against, rather than against a template."),
            _q("bar", "Your bar", "Learning what good looks like",
               "What makes someone great on your team — not on paper, in practice?",
               "short", "The bar", "Learned what good looks like here", i=2,
               placeholder="e.g. they close things without being chased",
               ack="That’s a real bar. Résumés don’t show it, so I’ll screen for it directly."),
            _q("how", "How you hire", "Placing your pipeline",
               "How do people reach you today?",
               "choice", "Pipeline", "Know where candidates come from", i=3,
               options=["Job boards", "Referrals", "Agencies", "Haven’t hired yet"],
               leaves_from="fixed", leaves=["Inbound", "Referral"],
               ack_by_option={
                   "Job boards": "Volume, then. Screening is where I earn my keep.",
                   "Referrals": "Best signal there is. I’ll help you ask more often.",
                   "Agencies": "Expensive. Let’s see what we can do before renewing that.",
                   "Haven’t hired yet": "Clean slate. We’ll do the first one properly.",
               }),
            _q("dayone", "Day one", "Shaping the first week",
               "What does day one look like for someone joining?",
               "short", "Day one", "Know what you promise on day one", i=4,
               placeholder="e.g. nothing formal yet — they just start",
               ack="Then that’s the first thing worth fixing. The first week sets the year."),
        ],
    },
    "pr": {
        "title": "Set up PR",
        "lede": "Four questions about the story and who should carry it.",
        "cta": "Start",
        "synth": ["Reading your story…", "Checking what’s provable…", "Matching it to who writes…", "PR is set up."],
        "done_title": "PR is yours now.",
        "done_lede": "I’ll warm the right people. Nothing gets pitched without you.",
        "done_cta": "Open PR",
        "questions": [
            _q("story", "The story", "Finding the angle",
               "What’s the story you want written about you? Not the pitch — the thing that’s actually interesting.",
               "long", "Angle", "Found the story worth telling", i=1,
               placeholder="e.g. we replaced a ₹3L/mo agency with ₹2,000 and it worked",
               ack="That’s an angle, not an announcement. Much easier to place."),
            _q("proof", "The proof", "Checking what holds up",
               "What have you done that a journalist could actually check?",
               "short", "Proof", "Know what’s provable", i=2,
               placeholder="e.g. 13 campaigns for one client in month one",
               ack="Good — numbers survive editing. Adjectives don’t."),
            _q("who", "Who reads it", "Placing the audience",
               "Who needs to read it for it to have been worth doing?",
               "choice", "Readers", "Know who the coverage is for", i=3,
               options=["Founders", "Investors", "Customers", "Everyone"],
               leaves_from="fixed", leaves=["Trade", "Mainstream"],
               ack_by_option={
                   "Founders": "Then trade press and founder communities beat mainstream every time.",
                   "Investors": "A narrower list, and a slower one. Worth doing properly.",
                   "Customers": "Then coverage is a sales asset. I’ll treat it that way.",
                   "Everyone": "Nobody, then. I’ll pick one and we’ll aim there first.",
               }),
            _q("known", "Who you know", "Mapping relationships",
               "Which publications or writers already matter to you — or already know you?",
               "short", "Relationships", "Mapped who already knows you", i=4,
               placeholder="e.g. nobody yet, but two reporters replied once",
               ack="A reply is a relationship. I’ll start there rather than cold."),
        ],
    },
    "sales": {
        "title": "Set up sales",
        "lede": "Four questions about how money actually arrives.",
        "cta": "Start",
        "synth": ["Reading the motion…", "Learning who buys…", "Placing the number…", "Sales is set up."],
        "done_title": "Sales is yours now.",
        "done_lede": "I’ll enrich, rank and prepare. You make the calls.",
        "done_cta": "Open sales",
        "questions": [
            _q("motion", "The motion", "Mapping how a sale happens",
               "Walk me through how a sale actually happens today — from first contact to money.",
               "long", "Motion", "Mapped how a sale happens", i=1,
               placeholder="e.g. they DM me, we talk for 20 minutes, they start",
               ack="Short and human. I’ll keep it that way rather than bolting a funnel onto it."),
            _q("icp", "Who buys", "Profiling the buyer",
               "Who buys fastest — and what do they have in common?",
               "short", "Buyer", "Know who closes fastest", i=2,
               placeholder="e.g. solo founders who already tried an agency",
               ack="That’s a pattern I can go and find more of."),
            _q("price", "The number", "Placing your pricing",
               "What do you charge, and how?",
               "short", "Pricing", "Know the number and the shape", i=3,
               placeholder="e.g. ₹2,000 a month, first month free",
               ack="Clear. I’ll lead with it rather than hide it — hiding it costs you calls."),
            _q("source", "Where they come from", "Sizing the pipeline",
               "Where do most of your leads come from right now?",
               "choice", "Sources", "Know where leads come from", i=4,
               options=["Referrals", "Inbound", "Outbound", "Nowhere yet"],
               leaves_from="fixed", leaves=["Warm", "Cold"],
               ack_by_option={
                   "Referrals": "Best margin there is. I’ll make asking systematic.",
                   "Inbound": "Then content and search are doing sales work. Worth funding.",
                   "Outbound": "Fine, as long as it’s warm. Cold sequences burn the list.",
                   "Nowhere yet": "Then we build one channel properly before adding a second.",
               }),
        ],
    },
    "ops": {
        "title": "Set up finance & ops",
        "lede": "Four questions about where the money and the time go.",
        "cta": "Start",
        "synth": ["Reading the spend…", "Checking the runway…", "Finding what’s idle…", "Finance is set up."],
        "done_title": "Finance is yours now.",
        "done_lede": "I’ll watch the spend and the calendar. Quiet is the correct state here.",
        "done_cta": "Open finance",
        "questions": [
            _q("spend", "The money", "Mapping where it goes",
               "Where does the money go each month? Rough is fine.",
               "long", "Spend", "Mapped where the money goes", i=1,
               placeholder="e.g. hosting, two contractors, a lot of tools I forgot about",
               ack="That last part is where the savings usually are. I’ll go looking."),
            _q("runway", "The runway", "Placing the horizon",
               "How long is your runway at the current burn?",
               "short", "Runway", "Know how long you have", i=2,
               placeholder="e.g. about 11 months",
               ack="Noted. Every decision below this changes depending on that number."),
            _q("idle", "What’s idle", "Finding the waste",
               "What are you paying for that you barely use?",
               "short", "Idle", "Know what’s being wasted", i=3,
               placeholder="e.g. two analytics tools and a CRM seat for someone who left",
               ack="I’ll audit those properly and bring you a list, not a lecture."),
            _q("track", "How you track it", "Placing your books",
               "How do you keep track of spend today?",
               "choice", "Books", "Know how spend is tracked", i=4,
               options=["A spreadsheet", "An accountant", "An app", "Not really"],
               leaves_from="fixed", leaves=["Recorded", "Reviewed"],
               ack_by_option={
                   "A spreadsheet": "Works until it doesn’t. I’ll keep it current for you.",
                   "An accountant": "Good. I’ll make sure they get clean numbers, not a shoebox.",
                   "An app": "Fine — I’ll read from it rather than adding a second one.",
                   "Not really": "Then that’s first. You can’t cut what you can’t see.",
               }),
        ],
    },
}

# what a floor says when you try to act on it before it's set up
def _name(sid: str) -> str:
    """Sentence case, except for the ones that are initials."""
    label = SURFACES[sid]["label"]
    return label if label.isupper() else label.lower()


LOCKS: dict[str, dict] = {
    s: {
        "title": f"{SURFACES[s]['label']} isn’t set up yet.",
        "blurb": "You can look around all you like. Before I start doing anything here, I need four answers — it takes about a minute.",
        "cta": f"Set up {_name(s)}",
    }
    for s in SERVICE_IDS
}


# ---- the instrument (design mock) --------------------------------------
#
# Each floor gets a geometry that MEANS something, rather than a graph that
# just looks busy: where a thing sits is the information. Same payload shape
# for all five; the type says how to read `at`, `lane` and `value`.

def _i(iid, label, meta, at=0.0, lane=0, value=0.0, state=""):
    return {"id": iid, "label": label, "meta": meta, "at": at, "lane": lane,
            "value": value, "state": state}


INSTRUMENTS: dict[str, dict] = {
    "marketing": {
        "type": "timeline", "title": "The week",
        "caption": "Left is out the door, right is still coming. Height is the channel.",
        "lanes": ["LinkedIn", "Email", "Video", "Site"],
        "items": [
            _i("linkedin", "The pivot lesson", "shipped 7:05am · 1.4k views", -0.72, 0, 3, "shipped"),
            _i("retarget", "Pricing-page retargeting", "shipped 6:20am · 1,900 people", -0.48, 3, 2, "shipped"),
            _i("warmup", "Warming 200 addresses", "day 4 of 14 · 0 bounces", 0.08, 1, 2, "running"),
            _i("shorts", "Six shorts from the demo", "4 rendered, captions next", 0.18, 2, 2, "running"),
            _i("hero", "Landing hero, 5 variants", "brand expert on the final pass", 0.34, 3, 2, "running"),
            _i("newsletter", "Next week’s newsletter", "waiting on you · Tuesday 9am", 0.5, 1, 4, "needs-you"),
            _i("reel", "Reel: the day-one story", "waiting on you · Wednesday", 0.62, 2, 4, "needs-you"),
            _i("memo", "Pricing memo goes public", "drafted · Thursday", 0.8, 3, 2, "scheduled"),
            _i("thread", "13 campaigns, month one", "queued · Friday", 0.92, 0, 2, "scheduled"),
        ],
    },
    "sales": {
        "type": "funnel", "title": "The funnel",
        "caption": "Each band is a stage. The size of a dot is how many people are in it.",
        "lanes": ["Signed up", "In conversation", "Worth a call", "Paying"],
        "unit": "people",
        "items": [
            _i("signups", "Last week’s signups", "40 enriched overnight", 0, 0, 40, "running"),
            _i("cold", "Never opened anything", "18 · leave them alone for now", 0, 0, 18, "idle"),
            _i("talking", "Mid-conversation", "6 · answered the first email", 1, 0, 6, "running"),
            _i("leads", "Worth a call this week", "7 · openers drafted, waiting on you", 2, 0, 7, "needs-you"),
            _i("agency", "Tried an agency, bounced off price", "3 · closest to SurferSearcher", 2, 0, 3, "needs-you"),
            _i("won", "Paying", "2 closed this month · ₹2,000 each", 3, 0, 2, "shipped"),
        ],
    },
    "hiring": {
        "type": "ladder", "title": "The ladder",
        "caption": "One column per role. Rungs are stages — the top rung is your call.",
        "lanes": ["Ops", "Design", "Engineering"],
        "unit": "people",
        "items": [
            _i("ops-app", "Applied", "6 in 4 hours · above average", 0, 0, 6, "running"),
            _i("ops-screen", "Through the screen", "2 the agent ranked against your JD", 1, 0, 2, "running"),
            _i("ops-you", "Your call", "Thursday 3pm and 4pm are held", 2, 0, 2, "needs-you"),
            _i("des-app", "Applied", "not posted yet", 0, 1, 0, "idle"),
            _i("des-brief", "Brief half-written", "you said designer first", 1, 1, 1, "idle"),
            _i("eng-app", "Applied", "not started — deliberately", 0, 2, 0, "idle"),
        ],
    },
    "pr": {
        "type": "radar", "title": "Who’s warm",
        "caption": "The middle is someone you spoke to this week. The edge is someone going cold.",
        "unit": "days since contact",
        "items": [
            _i("tc", "TechCrunch — follow-up sent", "2 days ago · no reply yet, that’s normal", 0.18, 0, 3, "running"),
            _i("r1", "Replied to your last note", "5 days ago · warmest thing you have", 0.26, 0, 3, "shipped"),
            _i("r2", "Read it, didn’t reply", "11 days ago", 0.44, 0, 2, "running"),
            _i("r3", "Covers founder tooling monthly", "3 weeks ago · worth a personal note", 0.62, 0, 3, "needs-you"),
            _i("r4", "Asked for the deck once", "6 weeks ago", 0.74, 0, 2, "idle"),
            _i("r5", "Nine on the list have gone quiet", "6 months · your PR expert cut them", 0.94, 0, 2, "idle"),
            _i("r6", "New: writes about AI adoption", "never contacted", 0.86, 0, 2, "idle"),
        ],
    },
    "ops": {
        "type": "mass", "title": "Where it goes",
        "caption": "Every circle is money out each month. The faint ones nobody has opened.",
        "unit": "₹ a month",
        "items": [
            _i("people", "Two contractors", "₹45,000 · the biggest thing you buy", 0, 0, 45000, "active"),
            _i("hosting", "Hosting, four providers", "₹6,400 · no traffic in 30 days", 0, 0, 6400, "idle"),
            _i("tools", "Design and docs tools", "₹3,200", 0, 0, 3200, "active"),
            _i("analytics", "Two analytics tools", "₹1,800 · you use one", 0, 0, 1800, "idle"),
            _i("crm", "A CRM seat", "₹900 · belongs to someone who left", 0, 0, 900, "idle"),
            _i("domains", "Domains and email", "₹400", 0, 0, 400, "active"),
        ],
    },
}


# ---- the email direction page (design mock) ----------------------------
#
# One job inside marketing, at the depth a founder actually works: the list,
# what went out and what it did, and the things that run without you.

EMAIL_PAGE = {
    "id": "email",
    "surface_id": "marketing",
    "label": "Email",
    "blurb": "The channel you own. Nobody can throttle it, so it has to be worth opening.",
    "stats": [
        {"id": "list", "value": "412", "label": "on the list", "delta": "+38 this month"},
        {"id": "open", "value": "41%", "label": "opened the last one", "delta": "+7 vs the one before"},
        {"id": "reply", "value": "11", "label": "replied", "delta": "3 became calls"},
        {"id": "unsub", "value": "2", "label": "left", "delta": None},
        {"id": "clicks", "value": "18%", "label": "clicked something", "delta": "+3 vs the one before"},
        {"id": "sends", "value": "4", "label": "sends this month", "delta": "1 queued"},
    ],
    "progress": {
        "label": "Warming 200 cold addresses",
        "value": 4,
        "of": 14,
        "note": "0 bounces so far · nothing sends to them until day 14",
    },
    "awaiting": "newsletter",
    "campaigns": [
        {"id": "s-next", "subject": "The agency did 13 campaigns. In one month.",
         "when": "Tuesday 9am", "audience": "Everyone", "sent": 0, "open_rate": 0, "replies": 0,
         "state": "scheduled",
         "body": [
             "An agency quoted you ₹80,000 a month and a two-week turnaround per campaign.",
             "We ran 13 in the first month. Not because anyone worked harder — because nobody had to wait for anybody.",
         ],
         "ps": "P.S. — reply with one word if you want the breakdown.",
         "outcome": "your PR expert's edits are in — read it before it ships",
         "work_id": "newsletter"},
        {"id": "s1", "subject": "You didn’t start a company to write newsletters at 11pm",
         "when": "last Tuesday", "audience": "Everyone", "sent": 374, "open_rate": 0.41, "replies": 11,
         "state": "sent",
         "body": [
             "It’s 11pm and you’re writing a newsletter. Again.",
             "Nobody starts a company for this part. The work that only you can do got pushed to tomorrow, and tomorrow it will get pushed again.",
         ],
         "ps": "P.S. — one word back and I’ll show you what this week could look like.",
         "outcome": "41% opened · 11 replies · 3 became calls"},
        {"id": "s2", "subject": "What ₹2,000 a month actually buys you",
         "when": "2 weeks ago", "audience": "Everyone", "sent": 351, "open_rate": 0.34, "replies": 4,
         "state": "sent",
         "body": [
             "₹2,000 a month is less than one freelancer’s invoice for one landing page.",
             "Here is what it covered last month: 13 campaigns, 6 shorts, a rebuilt CRM, and two hires screened.",
         ],
         "ps": None,
         "outcome": "34% opened · 4 replies"},
        {"id": "s3", "subject": "Introducing our AI-powered operations platform",
         "when": "3 weeks ago", "audience": "Everyone", "sent": 340, "open_rate": 0.23, "replies": 0,
         "state": "sent",
         "body": [
             "We’re excited to introduce our AI-powered operations platform, built to streamline your workflows end to end.",
         ],
         "ps": None,
         "outcome": "23% opened · 0 replies — your worst send"},
        {"id": "s4", "subject": "28 tasks in 30 days — how Mili did it",
         "when": "a month ago", "audience": "Everyone", "sent": 318, "open_rate": 0.39, "replies": 7,
         "state": "sent",
         "body": [
             "28 tasks in 30 days, one founder, no hires.",
             "The list is boring on purpose: invoices chased, a JD posted, six candidates screened, a press list rebuilt.",
         ],
         "ps": "P.S. — want the list? One word.",
         "outcome": "39% opened · 7 replies"},
    ],
    "health": {
        "title": "Can you actually reach them",
        "blurb": "None of the work above matters if it lands in spam. This is the channel’s own standing.",
        "scores": [
            {"id": "domain", "label": "Domain reputation", "value": "94", "state": "good",
             "note": "Google Postmaster · high, steady for 3 weeks"},
            {"id": "spf", "label": "SPF · DKIM · DMARC", "value": "All three", "state": "good",
             "note": "DMARC is at p=none — tighten it once the warm-up is done"},
            {"id": "spam", "label": "Spam rate", "value": "0.04%", "state": "good",
             "note": "the line you don’t want to cross is 0.3%"},
            {"id": "bounce", "label": "Bounce rate", "value": "1.2%", "state": "watch",
             "note": "up from 0.4% — the cold 200 are dragging it"},
        ],
        "updates": [
            "Day 4 of 14 on the cold 200 — 0 bounces so far.",
            "Sending volume stepped up to 40 a day; nothing sends to the cold list until day 14.",
            "One address hard-bounced on the main list and was removed automatically.",
        ],
    },
    "nouns": {
        "one": "send", "many": "sends", "metric": "opened",
        "automations": "sequences", "audience_word": "list",
    },
    "ui": {
        "tint": "b4",
        "floor_label": "Marketing",
        "floor_href": "/marketing",
        "placeholder": "Direct Allya — what should this one say?",
        "suggestions": [
            "Write next week’s newsletter",
            "Win back the quiet ones",
            "A plain send, from me",
        ],
        "know_title": "What I know about your emails",
        "brain_title": "The brain · email",
        "brain_subtitle": "touch a thought",
        "back_label": "Back to marketing",
        "back_href": "/marketing",
    },
    "work_ids": ["newsletter", "warmup"],
    "sequences": [
        {"id": "welcome", "name": "Welcome", "trigger": "on signup", "state": "live",
         "audience": "38 this month", "stat": "62% open · 5 replies"},
        {"id": "day3", "name": "Day-3 nudge", "trigger": "3 days after signup, if quiet", "state": "live",
         "audience": "22 this month", "stat": "31% open · 1 reply — too polite"},
        {"id": "winback", "name": "Win-back", "trigger": "60 days quiet", "state": "draft",
         "audience": "40 would qualify", "stat": "waiting on your approval"},
        {"id": "ps", "name": "One-reply P.S.", "trigger": "every send", "state": "live",
         "audience": "every send", "stat": "most of your replies start here"},
    ],
    "notes": [
        "Story-format sends open 18% better than product-format ones.",
        "The one that led with “AI-powered platform” is your worst send ever — 23%.",
        "Replies come from the P.S., not the body. Keep asking for one word.",
        "Sends before 9am get read; sends after 4pm don’t.",
    ],
}

# The same shape, a different channel. WhatsApp is not email with shorter
# lines: you send templates that Meta approves, your number carries a quality
# rating, and how many you may send in a day is a tier you earn. Everything
# that differs is a field that differs, not a comment.

WHATSAPP_PAGE = {
    "id": "whatsapp",
    "surface_id": "marketing",
    "label": "WhatsApp",
    "blurb": "Where your customers already are. Read in minutes — which is exactly why you don’t get to waste it.",
    "stats": [
        {"id": "list", "value": "268", "label": "opted in", "delta": "+52 this month"},
        {"id": "open", "value": "88%", "label": "read the last one", "delta": "+2 vs the one before"},
        {"id": "reply", "value": "34", "label": "replied", "delta": "9 became calls"},
        {"id": "unsub", "value": "6", "label": "blocked or opted out", "delta": None},
        {"id": "speed", "value": "4 min", "label": "median time to read", "delta": "email takes a day"},
        {"id": "sends", "value": "3", "label": "broadcasts this month", "delta": "1 waiting on Meta"},
    ],
    "progress": {
        "label": "Earning the next messaging tier",
        "value": 720,
        "of": 1000,
        "note": "720 unique numbers in 24h · 1,000 unlocks the 10k tier",
    },
    "awaiting": None,
    "campaigns": [
        {"id": "w-next", "subject": "Festive offer — first month free",
         "when": "Friday 11am", "audience": "Opted in · everyone", "sent": 0, "open_rate": 0, "replies": 0,
         "state": "draft",
         "body": [
             "Hi {{1}} — the first month is on us this festive season.",
             "Reply START and I’ll set it up on your account today.",
         ],
         "ps": None,
         "outcome": "template submitted to Meta · awaiting approval"},
        {"id": "w1", "subject": "Your weekly numbers are in",
         "when": "last Friday", "audience": "Opted in · everyone", "sent": 241, "open_rate": 0.88, "replies": 34,
         "state": "sent",
         "body": [
             "Hi {{1}} — 3 campaigns went out this week and 2 are still running.",
             "Say NUMBERS and I’ll send the one-pager.",
         ],
         "ps": None,
         "outcome": "88% read · 34 replies · 9 became calls"},
        {"id": "w2", "subject": "One question about last month",
         "when": "3 weeks ago", "audience": "Quiet 30+ days", "sent": 96, "open_rate": 0.71, "replies": 12,
         "state": "sent",
         "body": [
             "Hi {{1}} — you stopped opening these. Was it the timing, or the content?",
             "One word back is enough. It changes what I send you next.",
         ],
         "ps": None,
         "outcome": "71% read · 12 replies — the highest reply rate you have"},
        {"id": "w3", "subject": "We’ve launched something new!!",
         "when": "last month", "audience": "Opted in · everyone", "sent": 230, "open_rate": 0.52, "replies": 1,
         "state": "sent",
         "body": [
             "🎉 BIG NEWS!! We’ve just launched our brand new AI platform!! Check it out now!!",
         ],
         "ps": None,
         "outcome": "52% read · 1 reply · 4 blocks — the send that cost you quality"},
    ],
    "sequences": [
        {"id": "optin", "name": "Opt-in confirm", "trigger": "on first message", "state": "live",
         "audience": "52 this month", "stat": "instant · 0 complaints"},
        {"id": "abandon", "name": "Left mid-signup", "trigger": "2 hours after a stalled signup", "state": "live",
         "audience": "31 this month", "stat": "64% read · 8 finished"},
        {"id": "renew", "name": "Renewal nudge", "trigger": "7 days before renewal", "state": "draft",
         "audience": "18 would qualify", "stat": "template not submitted yet"},
        {"id": "wa_ps", "name": "One-word reply", "trigger": "every broadcast", "state": "live",
         "audience": "every broadcast", "stat": "where every reply starts"},
    ],
    "notes": [
        "Replies come in under 4 minutes here. Email takes a day.",
        "The all-caps launch broadcast is the only thing that ever got you blocked.",
        "Utility templates get approved in an hour; marketing ones take a day.",
        "Broadcasts after 8pm read fine but reply at half the rate.",
    ],
    "health": {
        "title": "Your number’s standing with Meta",
        "blurb": "Quality is a rating, not an opinion. Drop to red and the sending limit drops with it.",
        "scores": [
            {"id": "quality", "label": "Quality rating", "value": "Green", "state": "good",
             "note": "high · recovered after the launch broadcast"},
            {"id": "tier", "label": "Messaging limit", "value": "1,000 / day", "state": "watch",
             "note": "720 of 1,000 unique numbers reached — the next tier is 10k"},
            {"id": "number", "label": "Number status", "value": "Connected", "state": "good",
             "note": "verified business · display name approved"},
            {"id": "templates", "label": "Templates", "value": "6 live · 1 pending", "state": "watch",
             "note": "the festive offer is with Meta — usually a day for marketing"},
        ],
        "updates": [
            "Quality came back to green 9 days after the launch broadcast.",
            "720 unique numbers in the last 24h — 280 more and the limit goes to 10k.",
            "One template was rejected for using “FREE!!” in the header; rewritten and resubmitted.",
        ],
    },
    "nouns": {
        "one": "broadcast", "many": "broadcasts", "metric": "read",
        "automations": "automations", "audience_word": "opt-in list",
    },
    "ui": {
        "tint": "b1",
        "floor_label": "Marketing",
        "floor_href": "/marketing",
        "placeholder": "Direct Allya — what should this broadcast say?",
        "suggestions": [
            "Write the festive offer",
            "Ask the quiet ones one question",
            "A utility template, not marketing",
        ],
        "know_title": "What I know about your WhatsApp",
        "brain_title": "The brain · whatsapp",
        "brain_subtitle": "touch a thought",
        "back_label": "Back to marketing",
        "back_href": "/marketing",
    },
    "work_ids": [],
}

DIRECTIONS: dict[str, dict] = {"email": EMAIL_PAGE, "whatsapp": WHATSAPP_PAGE}


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


# ---- the interview, the thoughts, and the writing ----------------------
#
# All three used to live in the frontend, which meant the client was
# inventing questions, ideas and campaign copy. They belong here: this is
# the contract a real generator replaces, one function at a time.

_QUESTIONS = [
    {"key": "audience", "tag": "Who it goes to", "chips_are": "answer",
     "ask": "Who is this one for? Everyone, or a slice of the list."},
    {"key": "point", "tag": "The one thing", "chips_are": "starter",
     "ask": "What does it have to say? One sentence, in your words — I write around it, "
            "I don’t replace it."},
    {"key": "proof", "tag": "What backs it", "chips_are": "starter",
     "ask": "What backs it up? A number, someone’s words, a before and after — or nothing "
            "yet, which is fine."},
    {"key": "ask", "tag": "The ask", "chips_are": "answer",
     "ask": "And at the end — what do you want them to do?"},
    {"key": "when", "tag": "When it goes", "chips_are": "answer",
     "ask": "When should it go out?"},
]

_STARTERS = {
    "point": ["We just shipped ", "I got this wrong: ", "Here’s what changed this month: "],
    "proof": ["The number is ", "A customer put it better: ", "Before, ", "Nothing yet"],
}


def _stat(page: dict, sid: str):
    return next((s["value"] for s in page["stats"] if s["id"] == sid), None)


def _seq(page: dict, sid: str):
    return next((q for q in page["sequences"] if q["id"] == sid), None)


def questions_for(page: dict) -> list[dict]:
    """The five, with the options this channel can actually offer."""
    nouns, out = page["nouns"], []
    for q in _QUESTIONS:
        opts = _STARTERS.get(q["key"], [])
        if q["key"] == "audience":
            listed = _stat(page, "list")
            first = _seq(page, "welcome") or _seq(page, "optin")
            quiet = _seq(page, "winback") or _seq(page, "renew")
            opts = [
                f"Everyone — {listed} on the {nouns['audience_word']}" if listed else "Everyone",
                f"New this month — {first['audience']}" if first else "New this month",
                f"Gone quiet — {quiet['audience']}" if quiet else "The ones who went quiet",
            ]
        elif q["key"] == "ask":
            opts = ["Reply with one word", "Book a call", "Start the free month",
                    "Nothing — just read it"]
        elif q["key"] == "when":
            opts = ["Tuesday, 9am", "Tomorrow, 8am", "Hold it until I say"]
        out.append({**q, "options": opts})
    return out


def ack_for(key: str, answer: str) -> str:
    a = (answer or "").lower()
    if key == "audience":
        return f"{answer}. Good — that changes how blunt I can be."
    if key == "point":
        return "That’s the spine of it. Everything else hangs off that line."
    if key == "proof":
        if a.startswith("nothing"):
            return "Then we say it plain. A claim with no proof reads better naked than dressed up."
        return "Good. That goes right under the opening line, before anyone decides to stop reading."
    if key == "ask":
        if a.startswith("reply"):
            return "One-word replies are where your replies actually come from. That goes at the end."
        return f"“{answer}” it is — once, at the end, not three times through."
    return "Right. Give me a moment and I’ll write it."


# thoughts nobody has started yet — craft, not claims about the business
_UNPURSUED = [
    {"id": "i-split", "label": "Split the list by what they open", "state": "idea",
     "note": "One list is one guess. Two lists are two guesses you can check.",
     "moves": [{"id": "i-split-1", "label": "Openers of the last three"},
               {"id": "i-split-2", "label": "Everyone else"}],
     "seed": "The people who open everything should hear something different from the "
             "people who never do."},
    {"id": "i-plain", "label": "A plain one, from you", "state": "idea",
     "note": "No header, no template. The ones that read like a person get answered.",
     "moves": [{"id": "i-plain-1", "label": "No template"},
               {"id": "i-plain-2", "label": "Signed by you"}],
     "seed": ""},
    {"id": "i-one", "label": "Ask the quiet ones one question", "state": "idea",
     "note": "Not a campaign — a question. The answers are worth more than the opens.",
     "moves": [{"id": "i-one-1", "label": "One line, one question"}],
     "seed": "I want to know why you stopped opening these."},
]


def ideas_for(page: dict) -> list[dict]:
    """What this channel is doing, as thoughts — then what it isn't."""
    out = []
    nxt = next((c for c in page["campaigns"] if c["state"] != "sent"), None)
    if nxt:
        out.append({
            "id": "i-next", "label": f"The next {page['nouns']['one']}", "state": "draft",
            "note": f"{nxt['subject']} — {nxt['when']}, to {nxt['audience'].lower()}",
            "moves": [{"id": "i-next-when", "label": nxt["when"]},
                      {"id": "i-next-who", "label": nxt["audience"]}],
            "seed": nxt["subject"], "work": page.get("awaiting"),
        })
    for q in page["sequences"]:
        out.append({
            "id": f"i-{q['id']}", "label": q["name"],
            "note": f"{q['trigger']} · {q['stat']}",
            "state": "live" if q["state"] == "live" else "draft",
            "moves": [{"id": f"i-{q['id']}-t", "label": q["trigger"]},
                      {"id": f"i-{q['id']}-a", "label": q["audience"]}],
            "seed": "",
        })
    if page.get("progress"):
        p = page["progress"]
        out.append({
            "id": "i-warm", "label": p["label"], "state": "live",
            "note": f"{p['value']} of {p['of']} · {p['note']}",
            "moves": [{"id": "i-warm-1", "label": f"{p['value']} of {p['of']}"}],
            "seed": "",
        })
    return out + _UNPURSUED


def _strip(text: str) -> str:
    return " ".join((text or "").split()).rstrip(".…")


def _first_clause(text: str) -> str:
    cut = re.split(r"\s*[—–,;:]\s*", _strip(text))[0]
    return cut if len(cut) >= 12 else _strip(text)


def _ask_line(ask: str):
    a = (ask or "").lower()
    if a.startswith("reply"):
        return ("If that’s you, say so — one word is enough.",
                "P.S. — reply with one word and I’ll know it landed.")
    if a.startswith("book"):
        return ("If it’s worth twenty minutes, book a time and we’ll talk it through.", None)
    if a.startswith("start"):
        return ("The first month is free, if you want to see it on your own work.", None)
    return ("Nothing to do with this one. It’s just worth knowing.", None)


def compose(page: dict, answers: dict) -> dict:
    """Turn five answers into something readable.

    Every claim in the result is a sentence the founder typed; this only
    decides order, framing and what goes in the subject line. Swap this for
    a generator and the response shape stays exactly the same.
    """
    point = _strip(answers.get("point") or "")
    proof = _strip(answers.get("proof") or "")
    has_proof = bool(proof) and not proof.lower().startswith("nothing")
    close, ps = _ask_line(answers.get("ask") or "")

    subjects, seen = [], set()
    for s in (point, _first_clause(point), proof if has_proof else ""):
        if s and s not in seen:
            seen.add(s)
            subjects.append(s)

    return {
        "subjects": subjects[:3],
        "preview": proof if has_proof else _first_clause(point),
        "body": [s for s in (point, proof if has_proof else "", close) if s],
        "ps": ps,
        "audience": answers.get("audience") or f"Everyone on the {page['nouns']['audience_word']}",
        "when": answers.get("when") or "Hold it until I say",
        # the standing rules are what this channel has learned about itself
        "rules": page["notes"],
        "next": [
            "Your brand expert reads it before anyone else does.",
            "It comes back to you with whatever they changed, marked.",
            f"Nothing {'sends' if page['id'] == 'email' else 'goes out'} until you approve it.",
        ],
    }


_created = 0


def add_campaign(page: dict, draft: dict, subject=None) -> dict:
    """Queue one. In-memory on purpose — the contract is the point."""
    global _created
    _created += 1
    row = {
        "id": f"{page['id']}-new-{_created}",
        "subject": subject or (draft["subjects"][0] if draft["subjects"] else "Untitled"),
        "when": draft["when"], "audience": draft["audience"],
        "sent": 0, "open_rate": 0.0, "replies": 0, "state": "draft",
        "body": draft["body"], "ps": draft["ps"],
        "outcome": "queued for review — nothing goes out until you approve it",
    }
    page["campaigns"].insert(0, row)
    return row


# ---- what a campaign is made of, opened ---------------------------------
#
# Numbers a row doesn't carry (clicks, unsubscribes, bounces) and the three
# points on its clock. Keyed by campaign id so the seed above stays readable.

CAMPAIGN_FACTS: dict[str, dict] = {
    # email
    "s-next": {"clicked": 0, "left": 0, "bad": 0,
               "created": "4 Aug, 6:10pm", "scheduled": "12 Aug, 9:00am", "sent_on": None},
    "s1": {"clicked": 63, "left": 1, "bad": 2,
           "created": "27 Jul, 9:40pm", "scheduled": "29 Jul, 9:00am", "sent_on": "29 Jul, 9:00am"},
    "s2": {"clicked": 41, "left": 1, "bad": 3,
           "created": "20 Jul, 11:02am", "scheduled": "22 Jul, 9:00am", "sent_on": "22 Jul, 9:04am"},
    "s3": {"clicked": 12, "left": 4, "bad": 5,
           "created": "13 Jul, 3:20pm", "scheduled": "15 Jul, 4:30pm", "sent_on": "15 Jul, 4:31pm"},
    "s4": {"clicked": 58, "left": 0, "bad": 1,
           "created": "2 Jul, 8:15am", "scheduled": "4 Jul, 9:00am", "sent_on": "4 Jul, 9:00am"},
    # whatsapp
    "w-next": {"clicked": 0, "left": 0, "bad": 0,
               "created": "5 Aug, 10:05am", "scheduled": "8 Aug, 11:00am", "sent_on": None},
    "w1": {"clicked": 51, "left": 1, "bad": 0,
           "created": "31 Jul, 7:50pm", "scheduled": "1 Aug, 11:00am", "sent_on": "1 Aug, 11:00am"},
    "w2": {"clicked": 9, "left": 0, "bad": 1,
           "created": "14 Jul, 9:12am", "scheduled": "15 Jul, 10:30am", "sent_on": "15 Jul, 10:30am"},
    "w3": {"clicked": 18, "left": 2, "bad": 4,
           "created": "3 Jul, 5:40pm", "scheduled": "5 Jul, 8:30pm", "sent_on": "5 Jul, 8:31pm"},
}


def _pct(x: float) -> str:
    return f"{round(x * 100)}%"


def campaign_detail(page: dict, row: dict) -> dict:
    """A campaign with the numbers and the dates that only matter once
    you've opened it. What's worth showing depends on the state: a draft
    has an audience and an approval, one that's out has opens and replies."""
    f = CAMPAIGN_FACTS.get(row["id"], {})
    nouns, out = page["nouns"], row["state"] == "sent"
    n, wa = row["sent"], page["id"] == "whatsapp"

    if out:
        opened = round(row["open_rate"] * n)
        kpis = [
            {"id": "delivered", "value": str(n), "label": "delivered",
             "delta": f"{f.get('bad', 0)} {'undelivered' if wa else 'bounced'}"},
            {"id": "opened", "value": _pct(row["open_rate"]), "label": nouns["metric"],
             "delta": f"{opened} of {n}"},
            {"id": "clicked", "value": str(f.get("clicked", 0)),
             "label": "clicked something",
             "delta": _pct(f.get("clicked", 0) / n) + " of delivered" if n else None},
            {"id": "replied", "value": str(row["replies"]), "label": "replied",
             "delta": _pct(row["replies"] / n) + " of delivered" if n else None},
            # each channel already names this its own way in its stats
            {"id": "left", "value": str(f.get("left", 0)),
             "label": next((x["label"] for x in page["stats"] if x["id"] == "unsub"), "left"),
             "delta": None},
            {"id": "window", "value": row["when"], "label": "went out", "delta": row["audience"]},
        ]
    else:
        # nothing has happened to it yet, so the readings are what it's
        # aimed at and what this channel usually does — their own numbers,
        # which is the only honest benchmark for one that hasn't gone out
        done = [c for c in page["campaigns"] if c["state"] == "sent"]
        last = done[0] if done else None
        best = max(done, key=lambda c: c["open_rate"], default=None)
        listed = _stat(page, "list")
        list_label = next((s["label"] for s in page["stats"] if s["id"] == "list"), "on the list")
        kpis = [
            {"id": "reach", "value": listed or "—", "label": list_label,
             "delta": f"this one goes to {row['audience'].lower()}"},
            {"id": "when", "value": row["when"], "label": "goes",
             "delta": "holds 10 min after you approve"},
            # the outcome is already the line under the tiles — saying it
            # twice in one screen is worse than saying it once
            {"id": "state", "value": row["state"], "label": "where it is", "delta": None},
            {"id": "words", "value": str(sum(len(p.split()) for p in row.get("body", []))),
             "label": "words", "delta": f"{len(row.get('body', []))} paragraphs"},
            {"id": "last", "value": _pct(last["open_rate"]) if last else "—",
             "label": f"your last one {nouns['metric']}", "delta": last["subject"] if last else None},
            {"id": "best", "value": _pct(best["open_rate"]) if best else "—",
             "label": f"best you've {nouns['metric']}", "delta": best["subject"] if best else None},
        ]

    dates = [d for d in (
        {"label": "Written", "value": f.get("created")},
        {"label": "Scheduled for", "value": f.get("scheduled")},
        {"label": "Went out", "value": f.get("sent_on")},
    ) if d["value"]]

    return {**row, "kpis": kpis, "dates": dates}


# A third channel, on a different floor. The press newsletter is not
# marketing email with a different list: nobody opts in, every name is a
# person with a beat, and the thing you're measuring is whether a reporter
# replies — not whether a cohort converts.

NEWSLETTERS_PAGE = {
    "id": "newsletters",
    "surface_id": "pr",
    "label": "Newsletters",
    "blurb": "The note that goes to people who write for a living. They owe you nothing, so it has to be worth their four minutes.",
    "stats": [
        {"id": "list", "value": "84", "label": "on the press list", "delta": "+6 this month"},
        {"id": "open", "value": "52%", "label": "opened the last one", "delta": "+4 vs the one before"},
        {"id": "reply", "value": "7", "label": "replied", "delta": "2 asked for more"},
        {"id": "unsub", "value": "3", "label": "asked to be dropped", "delta": None},
        {"id": "clicks", "value": "24%", "label": "clicked the proof", "delta": "+9 vs the one before"},
        {"id": "coverage", "value": "2", "label": "pieces this quarter", "delta": "both from replies"},
    ],
    "progress": {
        "label": "Warming 12 reporters before the next pitch",
        "value": 5,
        "of": 12,
        "note": "one reply each · nothing is pitched until they've heard from you twice",
    },
    "awaiting": "presslist",
    "campaigns": [
        {"id": "n-next", "subject": "What changed since the last note",
         "when": "Thursday 8am", "audience": "Press list · everyone", "sent": 0, "open_rate": 0, "replies": 0,
         "state": "draft",
         "body": [
             "Two things moved since I last wrote: 13 campaigns shipped in a month, and the first month is now free.",
             "No ask. If either is useful for something you're writing, the numbers are attached.",
         ],
         "ps": "P.S. — reply STOP and I'll take you off this, no hard feelings.",
         "outcome": "waiting on the refreshed press list",
         "work_id": "presslist"},
        {"id": "n1", "subject": "13 campaigns in one month, and what broke",
         "when": "3 weeks ago", "audience": "Press list · everyone", "sent": 78, "open_rate": 0.52, "replies": 7,
         "state": "sent",
         "body": [
             "An agency quoted ₹80,000 a month and two weeks per campaign. We ran 13 in the first month.",
             "The part nobody writes about: two of them were bad, and one went out with the wrong subject line.",
         ],
         "ps": "P.S. — happy to walk anyone through the numbers, on or off record.",
         "outcome": "52% opened · 7 replies · 2 became pieces"},
        {"id": "n2", "subject": "A founder tool priced like a phone bill",
         "when": "2 months ago", "audience": "Press list · everyone", "sent": 71, "open_rate": 0.44, "replies": 3,
         "state": "sent",
         "body": [
             "₹2,000 a month, first month free. That's the whole pricing page.",
             "The interesting question isn't the price — it's what a founder stops paying for.",
         ],
         "ps": None,
         "outcome": "44% opened · 3 replies · 1 became a piece"},
        {"id": "n3", "subject": "PRESS RELEASE: Zeroto10 announces AI platform",
         "when": "4 months ago", "audience": "Press list · everyone", "sent": 64, "open_rate": 0.19, "replies": 0,
         "state": "sent",
         "body": [
             "FOR IMMEDIATE RELEASE — Zeroto10 today announced the launch of its AI-powered operational platform for founders.",
         ],
         "ps": None,
         "outcome": "19% opened · 0 replies · 3 asked to be dropped",
        },
    ],
    "sequences": [
        {"id": "welcome", "name": "New reporter note", "trigger": "when a name is added", "state": "live",
         "audience": "6 this month", "stat": "71% open · 2 replies"},
        {"id": "winback", "name": "Second touch", "trigger": "10 days after a first note, if quiet", "state": "draft",
         "audience": "12 would qualify", "stat": "waiting on your approval"},
        {"id": "thanks", "name": "Coverage thank-you", "trigger": "when a piece runs", "state": "live",
         "audience": "every piece", "stat": "where the second piece usually comes from"},
    ],
    "notes": [
        "The press release is the worst thing you have ever sent — 19%, and three drops.",
        "Every piece you have won came from a reply, not a pitch.",
        "Reporters open you at 8am. Nothing after 11am gets read the same day.",
        "Naming what broke gets more replies than naming what worked.",
    ],
    "health": {
        "title": "Whether reporters still want to hear from you",
        "blurb": "A press list is 84 people who can stop reading you forever. This is how close you are to that.",
        "scores": [
            {"id": "drops", "label": "Asked to be dropped", "value": "3 of 84", "state": "watch",
             "note": "all three after the press release — that format costs you names"},
            {"id": "reply", "label": "Reply rate", "value": "9%", "state": "good",
             "note": "anything above 5% on a cold press list is unusual"},
            {"id": "fresh", "label": "List freshness", "value": "11 stale", "state": "watch",
             "note": "11 names have changed beat or outlet since you added them"},
            {"id": "cadence", "label": "Cadence", "value": "Every 3 weeks", "state": "good",
             "note": "often enough to be remembered, rare enough not to be muted"},
        ],
        "updates": [
            "5 of 12 reporters have replied once — nothing is pitched to them until the second touch.",
            "Two names bounced at their old outlet and were moved, not deleted.",
            "The next note is held until the press list refresh you have waiting.",
        ],
    },
    "nouns": {
        "one": "note", "many": "notes", "metric": "opened",
        "automations": "follow-ups", "audience_word": "press list",
    },
    "ui": {
        "tint": "b3",
        "floor_label": "PR",
        "floor_href": "/pr",
        "placeholder": "Direct Allya — what should the press hear?",
        "suggestions": [
            "Write the next press note",
            "Say what broke, not what worked",
            "A note to the 12 being warmed",
        ],
        "know_title": "What I know about your press notes",
        "brain_title": "The brain · newsletters",
        "brain_subtitle": "touch a thought",
        "back_label": "Back to PR",
        "back_href": "/pr",
    },
    "work_ids": ["presslist", "pr_warm", "coverage"],
}

DIRECTIONS["newsletters"] = NEWSLETTERS_PAGE

CAMPAIGN_FACTS.update({
    "n-next": {"clicked": 0, "left": 0, "bad": 0,
               "created": "3 Aug, 7:20am", "scheduled": "13 Aug, 8:00am", "sent_on": None},
    "n1": {"clicked": 19, "left": 0, "bad": 1,
           "created": "12 Jul, 6:05am", "scheduled": "15 Jul, 8:00am", "sent_on": "15 Jul, 8:00am"},
    "n2": {"clicked": 12, "left": 0, "bad": 2,
           "created": "2 Jun, 9:30pm", "scheduled": "5 Jun, 8:00am", "sent_on": "5 Jun, 8:02am"},
    "n3": {"clicked": 3, "left": 3, "bad": 4,
           "created": "8 Apr, 2:15pm", "scheduled": "10 Apr, 12:00pm", "sent_on": "10 Apr, 12:00pm"},
})
