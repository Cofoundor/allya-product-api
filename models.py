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
