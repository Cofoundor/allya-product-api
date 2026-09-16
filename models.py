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


# ---- /brain: the whole memory, and correcting it ------------------------
#
# The page owns no data of its own. Everything it draws arrives from here:
# the joined graph, the words on the page, what a node is, where a thought
# may be moved to, and what you are allowed to say about it.

SuggestionKind = Literal["reword", "remove", "move", "add"]
SuggestionState = Literal["pending", "applied", "declined"]


class NodeRef(Base):
    id: str
    label: str


class MoveTarget(NodeRef):
    # which floor it sits on, so two "Pipeline"s are tellable apart
    note: Optional[str] = None


class Verb(Base):
    """One thing you can say about a node, and the words for saying it."""
    kind: SuggestionKind
    label: str
    hint: str
    # the field it needs, if it needs one
    field_label: Optional[str] = None
    placeholder: Optional[str] = None
    # shown instead of a field when the verb only needs a yes
    warn: Optional[str] = None
    # the reason field's example, which differs by what you are saying
    why_placeholder: Optional[str] = None


class BrainNodeDetail(Base):
    id: str
    label: str
    # "a thought", "a floor of the brain" — the page never names a tier
    kind_word: str
    floor_id: Optional[str] = None
    floor_label: Optional[str] = None
    # a placeholder until that floor's own setup fills it in
    provisional_note: Optional[str] = None
    work_note: Optional[str] = None
    # present only when this node is somewhere you can walk into
    explore_label: Optional[str] = None
    children: list[NodeRef] = []
    move_targets: list[MoveTarget] = []
    verbs: list[Verb] = []


class BrainFloor(Base):
    id: str
    label: str
    # everything she holds down there, directions and thoughts together
    count: int


class BrainCopy(Base):
    """Every string on /brain. The page hard-codes none of them."""
    title: str
    held_noun: str
    ring_title: str
    ring_subtitle: str
    floor_subtitle: str
    back_label: str
    hint: str
    search_placeholder: str
    search_empty: str
    rail_title: str
    rail_note: str
    ring_label: str
    inspector_empty_title: str
    inspector_empty: str
    verbs_title: str
    verbs_note: str
    why_label: str
    send_label: str
    sending_label: str
    cancel_label: str
    pending_note: str
    drawer_title: str
    drawer_empty: str
    withdraw_label: str
    offline: str
    retry: str
    loading: str
    # when the saying itself fails, rather than the reading
    send_failed: str
    withdraw_failed: str


class BrainPage(Base):
    copy: BrainCopy
    floors: list[BrainFloor]
    # the company view: hub, floors, and the shape of each
    ring: BrainGraph
    held: int


class BrainMatch(Base):
    id: str
    label: str
    where: str
    # the scope the client has to be in to open it
    scope: str


class BrainSearch(Base):
    matches: list[BrainMatch]


class BrainSuggestionIn(Base):
    # the thought itself for reword/remove/move; the PARENT for add
    node_id: str
    kind: SuggestionKind
    text: Optional[str] = Field(default=None, min_length=1, max_length=200)
    to_parent: Optional[str] = None
    why: Optional[str] = Field(default=None, max_length=400)


class BrainSuggestion(BrainSuggestionIn):
    id: str
    surface_id: str
    # what it was called when you said it, so the list still reads later
    node_label: str
    to_parent_label: Optional[str] = None
    # the server's words for both, so the drawer maps nothing
    kind_word: str
    summary: str
    state_word: str
    state: SuggestionState = "pending"
    ts: int


class BrainSuggestionList(Base):
    suggestions: list[BrainSuggestion]


class BrainSuggestionAck(Base):
    suggestion: BrainSuggestion
    # what she says back — her words, not the client's
    toast: str


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
    # who this is about. "CRM cleanup — merging 41 stale leads" is a claim
    # about 41 records, and it should be openable rather than only readable.
    person_id: Optional[str] = None
    segment_id: Optional[str] = None


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
    # the person this is a fact about, when it's about one
    person_id: Optional[str] = None


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
    # who it's with. "Pipeline review — the 7 worth a call" is a meeting
    # about seven people, and the grid should be able to open them.
    person_ids: list[str] = []


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
    # who this dot is, when it stands for people rather than work. What makes
    # a band on the funnel something you can open instead of only look at.
    person_ids: list[str] = []


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
    # how the campaign says it out loud: "Signups who never opened"
    audience: str
    # what that sentence resolves to. The audience stays prose because that's
    # how a founder thinks about it; this is who actually gets the thing.
    segment_id: Optional[str] = None
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
    segment_id: Optional[str] = None
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
    # the lenses this page can be looked at through, when it has more than one
    views: list["ViewOption"] = []


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
    """Something you could do next.

    On a brain it's a thought. On a person it's a control: `does` says who
    can take it — an agent, an expert, or you — and taking it makes a real
    work item or a real follow-up. A move nobody can take is a label, and a
    page full of labels is a dashboard."""

    id: str
    label: str
    # empty on a brain thought; on a person, who's able to take this
    does: list[str] = []
    # how it would read in the work list once dispatched
    work_title: str = ""
    # what it would say on a follow-up you keep for yourself
    own_title: str = ""


# ---- who you are -----------------------------------------------------

class User(Base):
    """The founder the product works for. There's no sign-in, so there's no
    session to hang this on — it's just who's being answered to."""

    id: str
    email: str
    name: str
    company: str


# ---- you ---------------------------------------------------------------
#
# The company has a brain; this is the other half of the record — the founder
# it answers to. A profile here is not a settings screen. It is what Allya
# knows about *you* and, more importantly, what she is allowed to do without
# coming back to you, floor by floor. Loosening that leash is the only
# irreversible thing on the page, which is why every rung says in words what
# it actually means.

# how much of a floor reaches you before it moves
Autonomy = Literal["ask", "brief", "trusted"]


class TrustLevel(Base):
    """One rung, and what picking it actually costs you."""

    id: Autonomy
    label: str
    note: str


class Trust(Base):
    """One floor's leash. `note` is the current rung read back in this
    floor's own terms — the same three rungs mean different things on
    marketing and on sales."""

    surface_id: str
    label: str
    href: str
    level: Autonomy
    note: str
    # what this floor has actually asked of you lately, so the rung is a
    # decision with evidence and not a preference
    asked: str


class Connection(Base):
    """Something outside this product that Allya acts through. `state` is
    the honest one: `attention` is a connection that still works and is
    about to stop."""

    id: str
    label: str
    account: str
    state: Literal["live", "attention", "off"]
    note: str
    action: str
    href: Optional[str] = None


class Known(Base):
    """One thing Allya holds about you. `source` is the seam that matters:
    `told` is something you said, `learned` is something she inferred from
    what you did — and only the second one owes you its evidence."""

    id: str
    text: str
    source: Literal["told", "learned"]
    note: Optional[str] = None


class Habit(Base):
    """One line about how you work. `options` empty means free text — the
    difference between a preference with a shape and one without."""

    id: str
    label: str
    value: str
    note: str
    options: list[str] = []


class StatGroup(Base):
    """A handful of numbers that answer one question about you. Three headline
    figures live on `Profile.stats`; everything else is grouped here, because
    forty numbers in a row is a dashboard and nobody reads a dashboard."""

    id: str
    label: str
    note: str
    stats: list[Stat]


class Lens(Base):
    """One way of looking at the left-hand pane. The leash never moves."""

    id: str
    label: str
    note: str


# ---- the answer book ---------------------------------------------------
#
# Everything the founder has ever typed into an onboarding, in one place and
# editable. Until now these answers were write-only: the company's six went
# into the browser's localStorage and a floor's four went into ANSWERS and
# were never read back. A founder who mistyped their revenue in week one had
# no way to correct it short of starting over.

class AnswerItem(Base):
    """One question, as it was asked, and what was said back. `learned` is
    the line Allya added to the ledger when the answer landed — the reason
    this question was worth asking at all."""

    key: str
    label: str
    question: str
    type: Literal["short", "long", "choice"]
    options: list[str] = []
    value: str
    learned: str


class AnswerGroup(Base):
    """One onboarding. `status` is honest about floors nobody has set up:
    they are `new` and the book offers the way in rather than empty fields.

    `status_label`, `empty` and `open` are derived here rather than in the
    interface: which drawer opens and what "never set up" is called are facts
    about the record, not rendering decisions."""

    id: str
    label: str
    note: str
    status: Literal["complete", "new"]
    status_label: str
    # what to say instead of fields when this one has never been run
    empty: str
    # the drawer that opens on arrival — the one everything else was built on
    open: bool
    # where to go to run (or re-run) this onboarding
    href: str
    cta: str
    items: list[AnswerItem]


class AnswerBook(Base):
    title: str
    blurb: str
    summary: str
    groups: list[AnswerGroup]


class AnswerEdit(Base):
    value: str = Field(min_length=1, max_length=4000)


class EditField(Base):
    """One editable line on the identity card. Same idea as Habit: the API
    names its own fields rather than the interface guessing at them."""

    key: Literal["name", "role", "company"]
    label: str


class ProfileUi(Base):
    know_title: str
    trust_title: str
    trust_blurb: str
    habits_title: str
    connections_title: str
    stats_title: str
    answers_title: str
    # which way of looking at the left-hand pane; the leash never moves
    lenses: list[Lens]
    # the identity card names its own fields, the way habits do
    identity: list[EditField]
    identity_note: str
    since_prefix: str
    knows_empty: str
    # What this API's enums are called in the interface — the same idea as
    # /crm/lexicon. The words belong to the vocabulary, not to the view: an
    # interface that hardcodes "you told me" has quietly forked the contract.
    source_labels: dict[str, str]
    connection_labels: dict[str, str]
    # and the words on the controls that act on this page's nouns. Forgetting
    # a memory and loosening a leash are domain verbs, not chrome.
    actions: dict[str, str]
    # the composer on this page tells her something about you rather than
    # asking her for work, so it brings its own words — including what the
    # suggestion popup calls them
    placeholder: str
    suggest_label: str
    suggestions: list[str]
    levels: list[TrustLevel]


class Profile(Base):
    """Everything the profile page renders."""

    user: User
    role: str
    since: str
    # Allya's own line about the page, in her voice
    blurb: str
    # the three that earn the top of the page
    stats: list[Stat]
    # and the rest, grouped by the question they answer
    stat_groups: list[StatGroup]
    # what she holds about you, as opposed to about the company
    knows: list[Known]
    habits: list[Habit]
    trust: list[Trust]
    connections: list[Connection]
    # The line each section puts in its own header, derived from what's under
    # it: "6 things · 2 you told me", "2 want you", "nothing yet". Derived
    # here rather than counted in the view, for the same reason the leash's
    # note is: the wording is this vocabulary's, and a view that phrases it
    # itself is a second place the contract has to be kept in step.
    summaries: dict[str, str]
    ui: ProfileUi


class ProfileEdit(Base):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    role: Optional[str] = Field(default=None, min_length=1, max_length=80)
    company: Optional[str] = Field(default=None, min_length=1, max_length=80)


class HabitEdit(Base):
    value: str = Field(min_length=1, max_length=120)


class TrustEdit(Base):
    level: Autonomy


class KnownAdd(Base):
    text: str = Field(min_length=2, max_length=240)


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
    # what the geometry measures — the axis, not the tally: "people", "₹",
    # "days since contact"
    unit: str
    # what one row in a stage is called. Not the same thing: the press radar
    # is measured in days and counted in people, and the money funnel is
    # measured in ₹ and counted in deals.
    count_noun: str = "people"
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


# where someone came from, at the grain a founder actually decides on. Not
# "the site" — which post, which campaign, whose referral.
Channel = Literal["site", "email", "whatsapp", "press", "social", "referral",
                  "job-boards", "csv", "direct"]


class TouchPoint(Base):
    """One end of the path in. `said` is the answer to "where did they come
    from" written out — "The SurferSearcher post" — because a channel id
    isn't an answer anybody wants."""

    at: int
    channel: Channel
    said: str
    campaign_id: Optional[str] = None
    direction_id: Optional[str] = None
    surface_id: Optional[str] = None


class Attribution(Base):
    """What brought them, what was in front of them when they moved, and
    everything in between.

    First touch answers "where do leads come from". Last touch answers the
    more expensive question — what actually closes them. Keeping both is the
    whole point: the channel that fills the top of the funnel is very often
    not the one that fills the bottom."""

    first: Optional[TouchPoint] = None
    last: Optional[TouchPoint] = None
    path: list[TouchPoint] = []
    converted_at: Optional[int] = None
    days_to_convert: Optional[int] = None
    # said plainly under the record: "Came from the SurferSearcher post,
    # closed after the pricing memo — 19 days."
    note: str = ""


class Followup(Base):
    """Something owed, and when by.

    A contact list tells you who exists. A CRM tells you who you owe
    something to today — which needs a date, and needs to go overdue."""

    id: str
    person_id: str
    what: str
    # YYYY-MM-DD
    due: str
    by: TouchBy
    state: Literal["open", "done", "snoozed"] = "open"
    created: str = ""
    # the work item this is waiting behind, when it was dispatched
    work_id: Optional[str] = None


class Prompt(Base):
    """One thing worth doing now, and the move that does it.

    A founder opening a book of a hundred strangers doesn't need a report,
    they need a decision. This is the shortest honest answer to "what do I
    do?" — who, why now, and one button. Never more than a few: a list of
    twenty priorities is a list of none."""

    id: str
    person_id: Optional[str] = None
    # who it's about, said the way the card shows it
    name: str = ""
    # why this one, in her voice — "Read the pricing page four times"
    why: str
    move_id: Optional[str] = None
    move_label: str = ""
    does: list[str] = []
    urgency: Literal["late", "today", "soon", "idea"] = "soon"


class OriginStat(Base):
    """One door in, and what came through it. `rate` is the number a founder
    decides on — the channel that brings the most is routinely not the one
    that converts, and a flat source count can't say so."""

    id: str
    said: str
    count: int
    worth: int
    paying: int
    rate: float


class FollowupIn(Base):
    what: str = Field(min_length=1, max_length=400)
    due: Optional[str] = None
    by: TouchBy = "you"


class FollowupPatch(Base):
    state: Optional[Literal["open", "done", "snoozed"]] = None
    due: Optional[str] = None


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
    # what brought them, short enough for a row: "The SurferSearcher post"
    origin_said: str = ""
    origin_channel: Optional[Channel] = None
    # what's owed and when — derived from the open follow-ups, so a list can
    # be sorted by who's actually overdue without reading each record
    next_step: Optional[str] = None
    next_due: Optional[str] = None
    overdue: bool = False


class PersonDetail(Person):
    """A person, opened: who they're with, what's on the table, and the whole
    trail behind them."""

    company: Optional[Company] = None
    deals: list[Deal] = []
    touches: list[Touch] = []
    segments: list[str] = []
    facts: list[str] = []
    next: list[Move] = []
    attribution: Attribution = Attribution()
    followups: list[Followup] = []


class MoveIn(Base):
    """Taking a move. `by` is the fork the whole thing turns on: hand it to
    an agent, hand it to an expert, or keep it."""

    by: TouchBy = "agent"
    due: Optional[str] = None


class MoveResult(Base):
    # what landed in the work list, when it was dispatched
    work: Optional[WorkItem] = None
    # what landed on your plate, when you kept it
    followup: Optional[Followup] = None
    touch: Touch
    toast: str


class PersonRow(Person):
    """A person as a row in the grid.

    The record on its own doesn't carry what a column needs — a company's
    name, what's on the table, how many times anyone has spoken to them.
    Joining that per row in the client would be a request each; deriving it
    here is one pass over memory, and it's what lets the table show every
    column a CRM tracks without opening anybody."""

    company_name: str = ""
    company_size: str = ""
    company_industry: str = ""
    # what they appear to be after, and the evidence that says so. An
    # inference, which is why it never travels without its reason.
    intent: str = ""
    intent_why: str = ""
    # money still open against them, across every deal
    open_value: int = 0
    deal_count: int = 0
    segment_labels: list[str] = []
    touch_count: int = 0
    # the most recent thing that happened, in its own words
    last_said: str = ""
    days_in_stage: Optional[int] = None
    # who owes the next step, when something is owed
    next_by: Optional[TouchBy] = None


class ViewOption(Base):
    """One lens on the book. The page draws a switch from these rather than
    naming the views itself."""

    id: str
    label: str
    note: str


class TableColumn(Base):
    """One column the grid can show.

    `key` names the field on a person row, which is what lets the client
    render a column it has never heard of: add one here and the grid shows
    it. Width is deliberately absent — how wide a column sits on a screen is
    the client's business, not the contract's."""

    key: str
    label: str
    # what it's for, so the picker can group two dozen of them
    group: str
    # in the default set
    on: bool = False
    # right-aligned and sorted numerically
    num: bool = False
    # allowed to wrap
    wide: bool = False


class TablePreset(Base):
    """A named set of columns. Nobody's first question is which of twenty-five
    columns they want; these are the answers. Per-user saved views replace
    this list without the client changing."""

    id: str
    label: str
    note: str
    keys: list[str]


class TableSpec(Base):
    columns: list[TableColumn]
    presets: list[TablePreset]
    # the order the picker groups columns in
    groups: list[str]


class WarmthWord(Base):
    id: Warmth
    # how the UI says it in a column: "this week", "gone quiet"
    said: str
    # the same fact with room to breathe, for a record rather than a cell:
    # "spoken to this week". Two phrasings because the screens differ, one
    # owner because the vocabulary shouldn't.
    said_full: str
    # warmest first — the client sorts by this rather than inventing an order
    rank: int


class DispatchWord(Base):
    """The three ways a move gets taken, said the way the button says it."""

    id: TouchBy
    verb: str
    note: str


class Lexicon(Base):
    """The words the interface puts on this API's enums.

    Every one of these used to be a constant in a component — three different
    spellings of the warmth words across three files, because nothing owned
    them. The vocabulary belongs with the values it describes."""

    warmth: list[WarmthWord]
    # touch kind -> the word a journey entry reads with
    touch_kinds: dict[str, str]
    # how urgent a prompt is -> what the card says
    urgency: dict[str, str]
    dispatch: list[DispatchWord]
    # surface id -> the human who covers it, in Allya's words
    experts: dict[str, str]


class PersonList(Base):
    people: list[PersonRow]
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

    # a hand-picked list rather than a rule. Every CRM has both, and they
    # answer different questions: a rule stays true as people move, a list
    # stays exactly who you chose. Set this and nothing else applies.
    person_ids: list[str] = []
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
