"""Response/request schemas for the Allya product API.

These are the contract. The dummy implementations behind them are throwaway;
these shapes are not — the production service should return exactly this.
"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Base(BaseModel):
    """snake_case in Python, camelCase on the wire — the client stays idiomatic
    without a translation layer on either side."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


WorkStatus = Literal["needs-you", "running", "shipped"]
Origin = Literal["agent", "expert"]
Speaker = Literal["allya", "you", "human"]
Period = Literal["today", "yesterday", "last-week"]


# ---- surfaces ----------------------------------------------------------

class SurfaceSummary(Base):
    id: str
    label: str
    note: str
    href: str
    # the node in the company brain this surface hangs off, when it has one
    node_id: Optional[str] = None


class BrainHeader(Base):
    title: str
    subtitle: str
    back_label: Optional[str] = None
    back_href: Optional[str] = None


class Lock(Base):
    """Shown when a floor is used before its setup is done. The floor is
    readable either way — this is what stops an action, not the door."""

    title: str
    blurb: str
    cta: str


class Surface(Base):
    id: str
    label: str
    # false until this floor's own onboarding is finished. The floor still
    # renders; acting on it is what prompts.
    onboarded: bool = True
    lock: Optional[Lock] = None
    greeting: str
    hint: str
    placeholder: str
    suggestions: list[str]
    brain: BrainHeader
    # "3 marketing agents running" — the noun between the count and the verb
    status_noun: str
    knowledge_title: str
    schedule_title: str
    # group id -> what that place is, read on a node's page
    node_copy: dict[str, str]
    empty_needs: str


# ---- brain -------------------------------------------------------------

class BrainNode(Base):
    id: str
    label: str
    tier: int = Field(ge=0, le=3)
    group: str
    parent: Optional[str] = None
    # a shorter name for the canvas, where the full one won't fit the ring
    short: Optional[str] = None
    # id of a work item this node mirrors, so it breathes when that needs you
    work: Optional[str] = None
    # seeded unborn; the client grows it in
    hidden: bool = False
    # this node opens a surface of its own instead of a panel
    surface: Optional[str] = None
    # a placeholder until this floor's onboarding fills it in — drawn faintly
    provisional: bool = False


class BrainGraph(Base):
    surface_id: str
    # 'cluster' fans leaves around their own parent — the gate's graph
    layout: Literal["web", "spray", "cluster"]
    # the node the layout is built around ("co" on the workspace)
    anchor_id: str
    nodes: list[BrainNode]
    links: list[tuple[str, str]]


# ---- work --------------------------------------------------------------

class WorkItem(Base):
    id: str
    surface_id: str
    status: WorkStatus
    origin: Origin
    who: Optional[str] = None
    who_name: Optional[str] = None
    who_role: Optional[str] = None
    say: Optional[str] = None
    title: Optional[str] = None
    meta: Optional[str] = None
    undoable: bool = False


class WorkSummary(Base):
    # shipped before today — the island's counter starts from this
    shipped_earlier: int
    spend_label: str
    spend_note: str


class WorkList(Base):
    items: list[WorkItem]
    summary: WorkSummary


# ---- review sheet ------------------------------------------------------

class ReviewHead(Base):
    avatar: str
    human: bool
    who: str
    role: Optional[str] = None
    line: str


class TrailRow(Base):
    kind: Literal["agent", "expert", "you"]
    text: str
    time: Optional[str] = None


class DiffPair(Base):
    old: str
    new: str


class Draft(Base):
    kicker: str
    title: str
    body: str
    tags: list[str] = []


class Review(Base):
    work_id: str
    head: ReviewHead
    trail: list[TrailRow]
    diff: list[DiffPair] = []
    drafts: list[Draft]
    note: Optional[str] = None
    approve_label: str


# ---- conversation ------------------------------------------------------

class Message(Base):
    id: str
    speaker: Speaker
    text: str
    tag: Optional[str] = None


class Chip(Base):
    label: str
    # "send" replays the label as a message; "review" opens a work item
    action: Literal["send", "review"]
    value: str


class Reply(Base):
    messages: list[Message]
    chips: list[Chip] = []


class MessageIn(Base):
    text: str = Field(min_length=1, max_length=2000)


# ---- knowledge + schedule ---------------------------------------------

class Fact(Base):
    id: str
    surface_id: str
    text: str
    period: Period
    # unix seconds, so the client can filter by a picked date
    ts: int
    flagged: bool = False
    mismatch: bool = False
    source: str = "observed"


class FactList(Base):
    facts: list[Fact]


class FactPatch(Base):
    flagged: Optional[bool] = None
    text: Optional[str] = Field(default=None, min_length=1, max_length=400)


class ScheduleEntry(Base):
    id: str
    when: str
    what: str
    pill: Optional[str] = None
    quiet: bool = False


class Schedule(Base):
    entries: list[ScheduleEntry]


# ---- calendar ----------------------------------------------------------
#
# The schedule above is "what's on", said in prose. The calendar is the same
# company on a grid: dated, navigable a month at a time, and joined back to
# work — an entry that carries a work_id opens that item's approval sheet.

CalendarKind = Literal["meeting", "ship", "review", "deadline", "focus"]


class CalendarEvent(Base):
    id: str
    surface_id: str
    # YYYY-MM-DD, always — the client never parses a display string
    date: str
    # how the time reads: "11:00", or "All day"
    when: str
    # minutes past midnight; -1 means all-day, and sorts first
    start_minute: int = -1
    duration_min: int = 0
    what: str
    kind: CalendarKind
    origin: Origin = "agent"
    pill: Optional[str] = None
    # the work item this sits on, when there is one
    work_id: Optional[str] = None


class CalendarDay(Base):
    """One dot-carrying cell in the month grid."""

    date: str
    count: int
    # of those, how many are yours to decide — the accent dots
    needs_you: int
    kinds: list[CalendarKind] = []


class CalendarMonth(Base):
    surface_id: str
    # YYYY-MM
    month: str
    # "August 2026"
    label: str
    today: str
    # weekday the 1st falls on, Monday = 0, so the client doesn't guess
    first_weekday: int
    days_in_month: int
    # only the days that hold something
    days: list[CalendarDay]
    # the day to open on: today when it's in this month, else the first busy one
    selected: str


class DayAgenda(Base):
    surface_id: str
    date: str
    # "Tuesday 4 August"
    label: str
    events: list[CalendarEvent]
    # what to say when the day is empty
    note: Optional[str] = None


# ---- action envelopes --------------------------------------------------

class WorkAction(Base):
    item: WorkItem
    toast: str
    reply: Reply


# ---- a floor's own onboarding ------------------------------------------

class ObCluster(Base):
    """What an answer grows on the brain. `leaves_from: answer` means the
    client splits what was typed; `fixed` uses the leaves given here."""

    id: str
    label: str
    group: str
    leaves_from: Literal["answer", "fixed"] = "answer"
    leaves: list[str] = []
    max_leaves: int = 4


class ObQuestion(Base):
    key: str
    tag: str
    # the live status line under the brain while this one lands
    sub: str
    q: str
    type: Literal["short", "long", "choice"]
    placeholder: Optional[str] = None
    example: Optional[str] = None
    options: list[str] = []
    # what Allya says back — one line, or one per option for a choice
    ack: Optional[str] = None
    ack_by_option: dict[str, str] = {}
    # the ledger line this answer adds
    learned: str
    cluster: ObCluster


class ServiceOnboarding(Base):
    surface_id: str
    label: str
    status: Literal["new", "complete"]
    title: str
    lede: str
    cta: str
    questions: list[ObQuestion]
    # the beats of the settling animation at the end
    synth: list[str]
    done_title: str
    done_lede: str
    done_cta: str


class AnswersIn(Base):
    answers: dict[str, str]


class OnboardingResult(Base):
    surface_id: str
    status: Literal["complete"]
    learned: list[str]


# ---- the instrument (design mock) --------------------------------------

class InstrumentItem(Base):
    """One thing on a floor's instrument. `at`, `lane` and `value` are the
    encoding — what they mean depends on the instrument's type:

    timeline  at = -1 shipped … 0 today … +1 scheduled, lane = channel
    funnel    at = stage index, value = how many
    ladder    at = stage index, lane = role, value = how many
    radar     at = 0 spoke today … 1 gone cold, value = reach
    mass      value = money a month, state 'idle' when nobody opens it
    """

    id: str
    label: str
    at: float = 0.0
    lane: int = 0
    value: float = 0.0
    state: str = ""
    meta: str = ""


class Instrument(Base):
    surface_id: str
    type: Literal["timeline", "funnel", "ladder", "radar", "mass"]
    title: str
    # what the geometry means, said plainly under the canvas
    caption: str
    lanes: list[str] = []
    unit: str = ""
    items: list[InstrumentItem]


# ---- a direction page (design mock) ------------------------------------
#
# A floor is a service; a direction is one job inside it. These are shaped
# per direction on purpose — email marketing has sends and sequences, and
# pretending otherwise is what makes a page generic and useless.

class Stat(Base):
    id: str
    value: str
    label: str
    delta: Optional[str] = None


class Progress(Base):
    label: str
    value: int
    of: int
    note: str


class Send(Base):
    """A campaign in a list: enough to rank it, not enough to read it."""
    id: str
    subject: str
    when: str
    audience: str
    sent: int
    open_rate: float
    replies: int
    state: Literal["sent", "scheduled", "draft"] = "sent"
    # what it did, in its own words ("11 replies · 3 became calls")
    outcome: Optional[str] = None
    # the work item this campaign is waiting behind, if it is waiting on a
    # human at all. A campaign with one is pending, whatever its state.
    work_id: Optional[str] = None


class DirectionSummary(Base):
    """A direction with a room of its own. The floor's brain reads this to
    know which of its dots are places you fly into, and where they go."""
    id: str
    label: str
    href: str
    surface_id: str


class DateFact(Base):
    """One point on a campaign's clock, already said the way it reads."""
    label: str
    value: str


class Campaign(Send):
    """One campaign, opened: the row, what it said, what it did and when.

    `kpis` is a list rather than fixed fields because what's worth showing
    depends on the state — a draft has an audience and an approval, a sent
    one has opens and replies — and on the channel."""
    body: list[str] = []
    ps: Optional[str] = None
    kpis: list[Stat] = []
    dates: list[DateFact] = []


class Score(Base):
    """One reading on whether the channel itself is in good standing."""
    id: str
    label: str
    # a channel says it its own way: "94", "Green", "Tier 2 · 1k/day"
    value: str
    state: Literal["good", "watch", "bad"]
    note: str


class Health(Base):
    """The thing that decides whether any of the work above ever arrives.
    Email calls it deliverability; WhatsApp calls it quality rating."""
    title: str
    blurb: str
    scores: list[Score]
    warmup: Optional[Progress] = None
    updates: list[str]


class Nouns(Base):
    """A channel's own words. One page serves both, and neither has to
    speak the other's language."""
    one: str
    many: str
    # what the headline rate is called: "opened" / "read"
    metric: str
    automations: str
    audience_word: str


class Sequence(Base):
    id: str
    name: str
    trigger: str
    state: Literal["live", "off", "draft"]
    audience: str
    stat: str


class ChannelUi(Base):
    """Everything the page needs to dress itself. It lives here so the
    frontend holds no channel copy of its own — swap the implementation
    behind these fields and the client doesn't change."""
    # which of the floor's branch tints this direction wears
    tint: str
    # the floor it belongs to, said the way the crumb and the brain need it
    floor_label: str
    floor_href: str
    placeholder: str
    suggestions: list[str]
    know_title: str
    brain_title: str
    brain_subtitle: str
    back_label: str
    back_href: str


class EmailPage(Base):
    """A channel you can run campaigns on. Email was the first; WhatsApp is
    the same shape with its own words, its own health and its own limits.

    Campaigns are not in here: they're their own collection, because they
    are paged through, opened and created on their own."""
    id: str
    surface_id: str
    label: str
    blurb: str
    stats: list[Stat]
    # the warm-up, or whatever long-running thing is mid-flight
    progress: Optional[Progress] = None
    # the one thing waiting on you, by work id
    awaiting: Optional[str] = None
    sequences: list[Sequence]
    notes: list[str]
    # standing of the channel itself — deliverability, quality rating
    health: Optional[Health] = None
    nouns: Nouns
    ui: ChannelUi


# ---- the interview, and what it produces -------------------------------

class Question(Base):
    key: Literal["audience", "point", "proof", "ask", "when"]
    tag: str
    ask: str
    # 'answer' → the chip is the answer; 'starter' → it only opens the
    # sentence, because the two questions that carry a claim must be the
    # founder's own words
    chips_are: Literal["answer", "starter"]
    options: list[str]


class Answers(Base):
    audience: Optional[str] = None
    point: Optional[str] = None
    proof: Optional[str] = None
    ask: Optional[str] = None
    when: Optional[str] = None


class Ack(Base):
    """What Allya says back when an answer lands."""
    text: str


class Draft(Base):
    """A campaign written out of five answers, not yet created."""
    subjects: list[str]
    preview: str
    body: list[str]
    ps: Optional[str] = None
    audience: str
    when: str
    # what was applied without being asked, and why
    rules: list[str]
    next: list[str]


class Idea(Base):
    """A thought on the channel's brain."""
    id: str
    label: str
    note: str
    state: Literal["live", "draft", "idea"]
    moves: list["Move"]
    # what it hands the interview as "the one thing"
    seed: str = ""
    work: Optional[str] = None


class Move(Base):
    id: str
    label: str


# ---- the gate ----------------------------------------------------------

class Credentials(Base):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=200)


class User(Base):
    id: str
    email: str
    name: str
    company: str


class Session(Base):
    token: str
    user: User


class Gate(Base):
    """Everything the sign-in page renders — including the graph that drifts
    behind it, which is the company as an outsider meets it rather than the
    workspace brain."""

    headline: str
    lede: str
    footnote: str
    footnote_link_label: str
    footnote_link_href: str
    brain: BrainGraph


# ---- the people layer --------------------------------------------------
#
# Every floor acts on people, and until now no floor could name one. The
# funnel on sales, the ladder on hiring and the radar on PR are the same
# object drawn three ways: a person, at a stage, last touched on a date.
# So there is one record here, not one per department.

PersonKind = Literal["customer", "prospect", "journalist", "candidate", "investor", "partner"]

# what happened, in the fewest kinds that still read differently
TouchKind = Literal[
    "signup", "email", "whatsapp", "call", "meeting", "payment",
    "churn", "note", "press", "application", "stage", "import",
]

# who did it. Wider than Origin, because on a person's timeline the
# founder's own moves belong next to the agent's — same grammar as TrailRow.
TouchBy = Literal["agent", "expert", "you"]

# how long since anyone spoke to them, said as a word rather than a number
Warmth = Literal["warm", "cooling", "cold", "never"]

DealState = Literal["open", "won", "lost"]
SourceState = Literal["connected", "available", "error"]


class Stage(Base):
    """One band of a pipeline. `at` is the lane index the instruments already
    encode with, so a stage and a funnel band are the same number."""

    id: str
    label: str
    at: int
    kind: Literal["open", "won", "lost", "dormant"] = "open"
    note: str = ""


class Pipeline(Base):
    """A named ordered set of stages. The sales funnel, the hiring ladder and
    the press radar are this, with different stages and different geometry.

    `counts` is derived on every read, never stored — the moment a stored
    count and the people disagree, the funnel is decoration."""

    id: str
    label: str
    person_kind: PersonKind
    surface_id: str
    geometry: Literal["funnel", "ladder", "radar"]
    # what a number on this pipeline means: "people", "₹", "days since contact"
    unit: str
    stages: list[Stage]
    counts: dict[str, int] = {}
    # money in the open stages, when the pipeline carries money at all
    value: Optional[int] = None


class Company(Base):
    """The account a person belongs to. Optional on purpose: a founder selling
    self-serve has people and no companies, and shouldn't be made to invent
    them."""

    id: str
    name: str
    domain: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    stage_id: Optional[str] = None
    people_count: int = 0
    value: Optional[int] = None
    note: str = ""


class Deal(Base):
    """What's actually on the table. Drawn as a band on the money funnel, not
    as a card on a board — a founder with four deals doesn't need a Kanban."""

    id: str
    person_id: Optional[str] = None
    company_id: Optional[str] = None
    title: str
    value: int
    currency: str = "INR"
    pipeline_id: str = "deals"
    stage_id: str
    state: DealState = "open"
    opened: str
    expected_close: Optional[str] = None
    work_id: Optional[str] = None
    note: str = ""


class Touch(Base):
    """One thing that happened to one person — the journey's atom.

    `text` is already said the way it reads ("Opened the win-back note twice,
    didn't reply"). Nothing downstream composes a sentence out of fields."""

    id: str
    person_id: str
    at: int
    kind: TouchKind
    by: TouchBy
    text: str
    # "your sales expert" — never a name we made up
    who: Optional[str] = None
    channel: Optional[str] = None
    work_id: Optional[str] = None
    campaign_id: Optional[str] = None
    direction_id: Optional[str] = None
    surface_id: Optional[str] = None


class StageChange(Base):
    at: int
    from_id: Optional[str] = None
    to_id: str
    by: TouchBy
    note: str = ""


class Journey(Base):
    """Everything that ever happened to one person, in one place. This is the
    whole point of the layer."""

    person_id: str
    name: str
    touches: list[Touch]
    stages: list[StageChange]
    opened: str
    note: str = ""


class Person(Base):
    """One human, whatever they are to you. A journalist and a lead and a
    candidate are the same record with a different kind — which is what lets
    PR, sales and hiring read the same book."""

    id: str
    name: str
    kinds: list[PersonKind]
    email: Optional[str] = None
    phone: Optional[str] = None
    handle: Optional[str] = None
    company_id: Optional[str] = None
    pipeline_id: str
    stage_id: str
    warmth: Warmth = "never"
    # which source put them here: "product-signups", "csv", "site"
    source: str = ""
    # who has been working them — the 85/15 seam, on the customer record
    owner: TouchBy = "agent"
    tags: list[str] = []
    value: Optional[int] = None
    created: str = ""
    last_touch_at: Optional[int] = None
    # Allya's one-line read, in her voice. Not a field the founder fills in.
    note: str = ""


class PersonDetail(Person):
    """A person, opened: who they're with, what's on the table, and the whole
    trail behind them."""

    company: Optional[Company] = None
    deals: list[Deal] = []
    touches: list[Touch] = []
    segments: list[str] = []
    facts: list[str] = []
    next: list[Move] = []


class PersonList(Base):
    people: list[Person]
    total: int
    cursor: Optional[str] = None
    # what the filter narrowed to, said plainly above the list
    caption: str = ""


class PersonIn(Base):
    name: str = Field(min_length=1, max_length=120)
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=40)
    handle: Optional[str] = Field(default=None, max_length=80)
    kinds: list[PersonKind] = ["prospect"]
    company: Optional[str] = Field(default=None, max_length=120)
    stage_id: Optional[str] = None
    note: str = Field(default="", max_length=400)


class PersonPatch(Base):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    email: Optional[str] = Field(default=None, max_length=254)
    phone: Optional[str] = Field(default=None, max_length=40)
    handle: Optional[str] = Field(default=None, max_length=80)
    kinds: Optional[list[PersonKind]] = None
    tags: Optional[list[str]] = None
    note: Optional[str] = Field(default=None, max_length=400)


class TouchIn(Base):
    kind: TouchKind = "note"
    text: str = Field(min_length=1, max_length=2000)
    by: TouchBy = "you"


class StageIn(Base):
    stage_id: str
    note: str = Field(default="", max_length=400)


class DealIn(Base):
    person_id: Optional[str] = None
    company_id: Optional[str] = None
    title: str = Field(min_length=1, max_length=160)
    value: int = Field(ge=0)
    stage_id: Optional[str] = None
    expected_close: Optional[str] = None
    note: str = Field(default="", max_length=400)


class DealPatch(Base):
    stage_id: Optional[str] = None
    state: Optional[DealState] = None
    value: Optional[int] = Field(default=None, ge=0)
    expected_close: Optional[str] = None
    note: Optional[str] = Field(default=None, max_length=400)


class SegmentRule(Base):
    """A segment said as a filter rather than a sentence. Empty lists mean
    'don't narrow on this', so an all-empty rule is everyone."""

    kinds: list[PersonKind] = []
    stage_ids: list[str] = []
    warmth: list[Warmth] = []
    tags: list[str] = []
    sources: list[str] = []
    # nobody has spoken to them in this many days
    not_touched_days: Optional[int] = None
    # they have at least one touch of this kind
    touched_kind: Optional[TouchKind] = None
    # they have none of this kind — "never opened anything"
    never_kind: Optional[TouchKind] = None


class Segment(Base):
    """What `audience` used to be a sentence about. A campaign still says
    "Signups who never opened" out loud; this is what that resolves to."""

    id: str
    label: str
    rule: SegmentRule
    count: int = 0
    # recomputed on read, rather than a list frozen when it was made
    live: bool = True
    note: str = ""


class SegmentIn(Base):
    label: str = Field(min_length=1, max_length=120)
    rule: SegmentRule
    note: str = Field(default="", max_length=400)


class DupeRow(Base):
    """Two rows that are one person. `keep` is what the merge would leave."""

    row: int
    incoming: str
    existing_id: str
    existing: str
    matched_on: Literal["email", "phone", "handle", "name"]
    keep: str


class ImportPreview(Base):
    """What a file would do, before it does it. Nothing is stored by the call
    that returns this."""

    columns: list[str]
    # column heading -> the field we think it is
    mapping: dict[str, str]
    rows_total: int
    rows_ready: int
    duplicates: list[DupeRow] = []
    problems: list[str] = []
    sample: list[dict[str, str]] = []


class ImportIn(Base):
    csv: str = Field(min_length=1)
    mapping: dict[str, str] = {}
    kind: PersonKind = "prospect"
    # merge onto the existing record, or leave the incoming row out
    on_duplicate: Literal["merge", "skip"] = "merge"
    segment_label: Optional[str] = Field(default=None, max_length=120)


class ImportResult(Base):
    added: int
    merged: int
    skipped: int
    segment_id: Optional[str] = None
    learned: list[str] = []


class IngestIn(Base):
    """One event from somewhere else — a signup, a payment, an open, a reply.
    Resolved onto a person by email, then phone, then handle; a miss creates
    one, because a touch with nobody to hang on is a touch we lose."""

    kind: TouchKind
    source: str
    email: Optional[str] = None
    phone: Optional[str] = None
    handle: Optional[str] = None
    name: Optional[str] = None
    at: Optional[int] = None
    text: Optional[str] = Field(default=None, max_length=2000)
    campaign_id: Optional[str] = None
    meta: dict[str, str] = {}


class IngestResult(Base):
    person_id: str
    created: bool
    touch_id: str
    stage_id: str
    # said the way the feed says it: "Moved to In conversation"
    note: str = ""


class Source(Base):
    """Where the people come from, and when it last brought any."""

    id: str
    label: str
    state: SourceState
    blurb: str
    last_sync: Optional[str] = None
    count: Optional[int] = None
    note: str = ""


class CrmPage(Base):
    """The people layer, dressed. Same shape as a channel page on purpose —
    the studio shell reads both."""

    id: str
    label: str
    blurb: str
    stats: list[Stat]
    progress: Optional[Progress] = None
    # the one thing waiting on you, by work id
    awaiting: Optional[str] = None
    pipelines: list[Pipeline]
    segments: list[Segment]
    sources: list[Source]
    notes: list[str]
    nouns: Nouns
    ui: ChannelUi
