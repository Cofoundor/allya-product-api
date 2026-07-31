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
