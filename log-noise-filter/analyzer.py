"""
================================================================================
Log Noise Filter for Developers  — v2  (Functional Edition)
================================================================================
Author  : Senior Systems Engineer
Purpose : Analyze large application log files and produce structured error
          reports that help developers quickly identify the most important
          failures.

New in v2 — additional functional concepts over v1:
  • Maybe / Result monads          – explicit failure handling without exceptions
  • Function composition (compose) – point-free pipeline construction
  • Transducer pattern             – composable, single-pass data transformation
  • operator module                – attrgetter / itemgetter as first-class fns
  • itertools.groupby              – declarative grouping without loops
  • itertools.chain / islice       – lazy sequence algebra
  • Running reduce (scan)          – cumulative frequency timeline
  • Monoid / fold pattern          – accumulation via an identity + combine fn
  • flip / compose2 utilities      – currying / composition helpers
  • Point-free predicate algebra   – all_of / any_of / negate combinators
  • Lazy property (cached_property)– memoised attribute on a data class
  • dataclass with __post_init__   – immutable validated value object
  • Custom Iterator class          – __iter__ / __next__ protocol
  • Infinite generator + islice    – rank stream sliced on demand
  • starmap                        – map over argument tuples
  • accumulate                     – itertools running totals
  • takewhile / dropwhile          – lazy conditional slicing
  • compress                       – data-driven filtering
  • product / combinations         – combinatoric generators (pattern pairs)
  • ChainMap                       – layered config as immutable view

Usage   : python log_analyzer_v2.py [logfile]
          [logfile] --rare-threshold=N --top-n=N
          If no file is given the built-in sample dataset is used.
================================================================================
"""

# ---------------------------------------------------------------------------
# Standard-library imports only
# ---------------------------------------------------------------------------
import re
import sys
import os
import functools
import itertools
import operator
import collections
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    Any, Callable, Dict, FrozenSet, Generic, Iterator,
    List, Optional, Tuple, TypeVar
)

T = TypeVar("T")
U = TypeVar("U")

# ===========================================================================
# 1.  DATA MODEL
#     namedtuple (immutable) · dataclass with validation · frozenset
# ===========================================================================

from collections import namedtuple

# Immutable raw log record
LogEntry = namedtuple("LogEntry", ["timestamp", "level", "message", "raw"])

# Immutable analysis result record
GroupedError = namedtuple("GroupedError", ["message", "count", "is_rare", "is_new"])


@dataclass(frozen=True)          # frozen=True  →  immutable after construction
class AnalysisConfig:
    """
    Validated, immutable configuration object.
    frozen dataclass = value object; __post_init__ enforces invariants.
    """
    rare_threshold: int = 2
    top_n: int = 10
    filepath: Optional[str] = None

    def __post_init__(self):     # validation in constructor
        if self.rare_threshold < 1:
            raise ValueError("rare_threshold must be >= 1")
        if self.top_n < 1:
            raise ValueError("top_n must be >= 1")


# ===========================================================================
# 2.  MAYBE MONAD
#     Explicit optional-value handling without None checks scattered everywhere
# ===========================================================================

class Maybe(Generic[T]):
    """
    Minimal Maybe monad.
    Nothing()  — represents absence of a value (failed computation).
    Just(v)    — wraps a present value.

    Concepts demonstrated:
      • Monad bind (flat_map)
      • Functor map
      • Generic class
      • Functions as objects passed to map/bind
    """
    __slots__ = ("_value", "_has_value")

    def __init__(self, value: Optional[T], has_value: bool):
        object.__setattr__(self, "_value",     value)
        object.__setattr__(self, "_has_value", has_value)

    # --- constructors ---
    @classmethod
    def just(cls, value: T) -> "Maybe[T]":
        return cls(value, True)

    @classmethod
    def nothing(cls) -> "Maybe[T]":
        return cls(None, False)

    @classmethod
    def of(cls, value: Optional[T]) -> "Maybe[T]":
        return cls.nothing() if value is None else cls.just(value)

    # --- functor map: applies fn if value present ---
    def map(self, fn: Callable[[T], U]) -> "Maybe[U]":   # fn as object
        if self._has_value:
            return Maybe.just(fn(self._value))
        return Maybe.nothing()

    # --- monad bind / flat_map ---
    def flat_map(self, fn: Callable[[T], "Maybe[U]"]) -> "Maybe[U]":
        if self._has_value:
            return fn(self._value)
        return Maybe.nothing()

    def get_or_else(self, default: T) -> T:
        return self._value if self._has_value else default

    def is_present(self) -> bool:
        return self._has_value

    def __repr__(self):
        return f"Just({self._value!r})" if self._has_value else "Nothing()"


# ===========================================================================
# 3.  RESULT MONAD
#     Wraps a computation that can succeed (Ok) or fail (Err)
# ===========================================================================

class Result(Generic[T]):
    """
    Result monad: Ok(value) | Err(reason).
    Replaces try/except at call sites; errors flow as values.

    Concepts: Generic, Functor map, Monad bind, functions as objects.
    """
    __slots__ = ("_value", "_error", "_ok")

    def __init__(self, value, error, ok: bool):
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_error", error)
        object.__setattr__(self, "_ok",    ok)

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value, None, True)

    @classmethod
    def err(cls, reason: str) -> "Result[T]":
        return cls(None, reason, False)

    def map(self, fn: Callable[[T], U]) -> "Result[U]":
        return Result.ok(fn(self._value)) if self._ok else self

    def flat_map(self, fn: Callable[[T], "Result[U]"]) -> "Result[U]":
        return fn(self._value) if self._ok else self

    def get_or_else(self, default: T) -> T:
        return self._value if self._ok else default

    def is_ok(self) -> bool:
        return self._ok

    def error(self) -> Optional[str]:
        return self._error

    def __repr__(self):
        return f"Ok({self._value!r})" if self._ok else f"Err({self._error!r})"


# ===========================================================================
# 4.  FUNCTIONAL UTILITIES
#     compose · flip · negate · all_of · any_of · scan · monoid fold
# ===========================================================================

# --- 4a. Function composition (right-to-left) ---
def compose(*fns: Callable) -> Callable:
    """
    compose(f, g, h)(x)  ==  f(g(h(x)))
    Uses functools.reduce to fold the function list (Reduce + HOF).
    """
    return functools.reduce(
        lambda f, g: lambda *a, **kw: f(g(*a, **kw)),   # reduce over fns
        fns
    )


# Pipe = left-to-right compose (more readable for data pipelines)
def pipe(*fns: Callable) -> Callable:
    """pipe(f, g, h)(x) == h(g(f(x)))"""
    return compose(*reversed(fns))                       # reversed + compose


# --- 4b. flip: swap argument order of a binary function ---
def flip(fn: Callable) -> Callable:
    """flip(f)(a, b) == f(b, a)   — useful for partial application."""
    return lambda a, b: fn(b, a)                         # Lambda + closure


# --- 4c. Predicate algebra ---
def negate(pred: Callable) -> Callable:
    """Return a predicate that is the logical NOT of pred."""
    return lambda *args: not pred(*args)                 # Lambda + HOF


def all_of(*preds: Callable) -> Callable:
    """Return a predicate that is True only if all preds are True."""
    return lambda x: all(p(x) for p in preds)           # all + generator


def any_of(*preds: Callable) -> Callable:
    """Return a predicate that is True if any pred is True."""
    return lambda x: any(p(x) for p in preds)           # any + generator


# --- 4d. Currying ---
def curry(fn: Callable) -> Callable:
    """Two-argument curry: curry(f)(a)(b) == f(a, b)."""
    def outer(a):
        def inner(b):                                    # Closure over a, fn
            return fn(a, b)
        return inner
    return outer


# --- 4e. Scan (running reduce) — like Haskell scanl ---
def scan(fn: Callable, iterable, initial=None):
    """
    Yield running accumulated values.
    scan(+, [1,2,3], 0)  →  0, 1, 3, 6
    Wraps itertools.accumulate with an optional seed.
    """
    if initial is not None:
        return itertools.accumulate(iterable, fn, initial=initial)  # accumulate
    return itertools.accumulate(iterable, fn)


# --- 4f. Monoid fold ---
def monoid_fold(identity, combine: Callable, items):
    """
    Fold a sequence using a monoid (identity element + binary combine fn).
    Generalised reduce pattern.
    """
    return functools.reduce(combine, items, identity)    # reduce


# --- 4g. Partial application & operator helpers ---
get_count   = operator.itemgetter(1)                     # itemgetter as fn object
get_message = operator.itemgetter(0)                     # itemgetter
get_level   = operator.attrgetter("level")               # attrgetter as fn object
get_msg_field = operator.attrgetter("message")           # attrgetter


# ===========================================================================
# 5.  DECORATORS  (Memoization · Timed · Retry · Logged)
# ===========================================================================

def memoize(fn: Callable) -> Callable:
    """
    Memoization decorator.
    cache dict is a closure variable — Closure concept.
    """
    cache: dict = {}                                     # Closure variable
    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    wrapper.cache = cache
    return wrapper


def timed(fn: Callable) -> Callable:
    """Decorator: print elapsed wall-clock time."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start  = datetime.now()
        result = fn(*args, **kwargs)
        ms     = (datetime.now() - start).total_seconds() * 1000
        print(f"  [timer] {fn.__name__} finished in {ms:.2f}ms")
        return result
    return wrapper


def logged(fn: Callable) -> Callable:
    """Decorator: log entry/exit of a function (higher-order fn)."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"  [call]  → {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"  [call]  ← {fn.__name__}")
        return result
    return wrapper


# Stack multiple decorators — stacking is itself functional composition
def retry(times: int = 3) -> Callable:
    """Parameterised decorator factory (closure over times)."""
    def decorator(fn: Callable) -> Callable:             # Closure over times
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    if attempt == times - 1:
                        raise
                    print(f"  [retry] attempt {attempt + 1} failed: {exc}")
        return wrapper
    return decorator


# ===========================================================================
# 6.  CUSTOM ITERATOR CLASS
#     __iter__ / __next__ protocol · StopIteration
# ===========================================================================

class RankedStream:
    """
    Infinite iterator that yields (rank, item) pairs from a sequence.
    Demonstrates the iterator protocol (__iter__ / __next__).
    """
    def __init__(self, items: list):
        self._items = items                              # store reference
        self._index = 0

    def __iter__(self):                                  # Iterable protocol
        return self

    def __next__(self):                                  # Iterator protocol
        if self._index >= len(self._items):
            raise StopIteration
        rank = self._index + 1
        item = self._items[self._index]
        self._index += 1
        return (rank, item)


# ===========================================================================
# 7.  TRANSDUCER PATTERN
#     Composable, allocation-free single-pass transformation
# ===========================================================================

def mapping(fn: Callable) -> Callable:
    """Transducer: lift a map operation into reducer space."""
    def xf(reducer: Callable) -> Callable:               # Closure over fn
        def step(acc, x):
            return reducer(acc, fn(x))                   # fn as object
        return step
    return xf


def filtering(pred: Callable) -> Callable:
    """Transducer: lift a filter predicate into reducer space."""
    def xf(reducer: Callable) -> Callable:               # Closure over pred
        def step(acc, x):
            return reducer(acc, x) if pred(x) else acc
        return step
    return xf


def transduce(xform: Callable, reducer: Callable, init, iterable):
    """
    Apply a composed transducer to an iterable.
    Single pass, no intermediate allocations.
    """
    return functools.reduce(xform(reducer), iterable, init)  # reduce


# ===========================================================================
# 8.  LOG PARSING UTILITIES
# ===========================================================================

_LOG_PATTERN = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
    r"\s+(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)"
    r"\s+(?P<msg>.+)$"
)

# Pure function — no side effects, always same output for same input
def parse_line(raw: str) -> Maybe:
    """
    Parse a raw line into a Maybe[LogEntry].
    Returns Nothing on parse failure instead of None/exception.
    """
    m = _LOG_PATTERN.match(raw.strip())
    if not m:
        return Maybe.nothing()
    entry = LogEntry(
        timestamp=m.group("ts"),
        level    =m.group("level"),
        message  =m.group("msg").strip(),
        raw      =raw.rstrip(),
    )
    return Maybe.just(entry)


def safe_open_file(filepath: str) -> Result:
    """
    Wrap file open in a Result monad.
    Returns Ok(filepath) or Err(reason) — no bare exceptions.
    """
    if not os.path.isfile(filepath):
        return Result.err(f"File not found: {filepath}")
    if not os.access(filepath, os.R_OK):
        return Result.err(f"Permission denied: {filepath}")
    return Result.ok(filepath)


# ===========================================================================
# 9.  GENERATOR-BASED FILE READER
#     Generators · yield from · lazy pipelines · islice · chain
# ===========================================================================

def read_log_lines(filepath: str) -> Iterator[str]:
    """
    Lazily yield raw lines. Generator — O(1) memory regardless of file size.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        yield from fh                                    # Generator delegation


def parse_log_stream(lines: Iterator[str]) -> Iterator[LogEntry]:
    """
    Pure generator pipeline: lines → Maybe[LogEntry] → LogEntry.
    Uses map (built-in HOF), filter, and Maybe.map.
    """
    maybes  = map(parse_line, lines)                     # map (Built-in HOF)
    present = filter(Maybe.is_present, maybes)           # filter + method ref
    yield from map(lambda m: m.get_or_else(None), present)  # map + lambda


def windowed(iterable, n: int) -> Iterator[tuple]:
    """
    Sliding window generator of width n.
    Uses itertools.islice + collections.deque.
    Demonstrates: islice, deque as sequence constructor, yield.
    """
    it  = iter(iterable)                                 # explicit iterator
    win = collections.deque(itertools.islice(it, n), maxlen=n)  # islice + deque
    if len(win) == n:
        yield tuple(win)
    for item in it:
        win.append(item)
        yield tuple(win)                                 # Generator yield


def chunked(iterable, size: int) -> Iterator[list]:
    """
    Yield successive fixed-size chunks from an iterable (lazy).
    Uses iter() with sentinel + zip.
    """
    it = iter(iterable)
    sentinel = object()
    while True:
        chunk = list(itertools.islice(it, size))         # islice
        if not chunk:
            break
        yield chunk


# ===========================================================================
# 10.  NORMALISATION PIPELINE
#      compose · memoize · reduce over rules · Lambda · Slicing
# ===========================================================================

_NORM_RULES: tuple = (                                   # immutable tuple
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b[0-9a-fA-F\-]{8,}\b"),                   "<ID>"),
    (re.compile(r"\b\d+\b"),                                  "<N>"),
    (re.compile(r"\"[^\"]*\""),                               "<STR>"),
    (re.compile(r"'[^']*'"),                                  "<STR>"),
)

# Lambda as named function object
_to_lower = lambda s: s.lower().strip()                  # Lambda

# Single rule application — pure function
_apply_rule = curry(lambda rule, text: rule[0].sub(rule[1], text))  # curry + lambda


@memoize                                                 # Memoization
def normalize_message(msg: str) -> str:
    """
    Normalize via function composition pipeline.
    1. lowercase  2. apply all regex rules via reduce
    Point-free inner pipeline: compose(_to_lower) then fold over rules.
    """
    lowered = _to_lower(msg)                             # Lambda call
    # monoid_fold: identity="" would be wrong here; use reduce directly
    # Defensive copy of rules (immutable tuple is already safe — no copy needed;
    # we slice to demonstrate Slicing concept)
    active_rules = _NORM_RULES[:]                        # Slicing (tuple slice)
    return functools.reduce(
        lambda text, rule: rule[0].sub(rule[1], text),   # Lambda + reduce
        active_rules,
        lowered,
    )


# ===========================================================================
# 11.  FILTERING & EXTRACTION
#      Transducers · compress · takewhile · dropwhile · point-free predicates
# ===========================================================================

_RELEVANT_LEVELS: FrozenSet[str] = frozenset({"WARNING", "ERROR"})  # immutable

# Point-free predicate built with combinators
is_relevant  = lambda e: e.level in _RELEVANT_LEVELS    # Lambda
is_error     = lambda e: e.level == "ERROR"             # Lambda
is_warning   = lambda e: e.level == "WARNING"           # Lambda
is_any_alert = any_of(is_error, is_warning)             # Predicate combinator

def extract_relevant_entries(entries: Iterator[LogEntry]) -> List[LogEntry]:
    """
    Keep WARNING + ERROR entries using transducer pattern.
    Single-pass: filter transducer composed with identity mapping.
    """
    # Transducer: filter(is_relevant) composed with mapping(identity)
    xform = compose(
        filtering(is_relevant),                          # filtering transducer
        mapping(lambda e: e),                            # identity mapping
    )
    append_reducer = lambda acc, x: (acc.append(x), acc)[1]
    return transduce(xform, append_reducer, [], entries)


def compress_by_selector(entries: List[LogEntry], selectors) -> List[LogEntry]:
    """
    Keep entries at positions where selector is truthy.
    Uses itertools.compress — data-driven filtering.
    """
    return list(itertools.compress(entries, selectors))  # compress


# ===========================================================================
# 12.  ERROR GROUPING ENGINE
#      itertools.groupby · starmap · operator.attrgetter
# ===========================================================================

def group_entries(entries: List[LogEntry]) -> Dict[str, List[LogEntry]]:
    """
    Group by normalised message using itertools.groupby.
    entries must be sorted by key first (groupby requirement).
    Demonstrates: sorted with key fn, groupby, operator.attrgetter,
    dict comprehension, starmap.
    """
    key_fn = compose(normalize_message, get_msg_field)   # compose + attrgetter

    # Sort by normalised key so groupby works correctly
    sorted_entries = sorted(entries, key=key_fn)         # sorted (Built-in HOF)

    # groupby yields (key, group_iterator) pairs
    grouped = {
        k: list(g)
        for k, g in itertools.groupby(sorted_entries, key=key_fn)  # groupby
    }
    return grouped


def frequency_table(groups: Dict[str, List]) -> List[Tuple[str, int]]:
    """
    Build (message, count) tuples sorted descending.
    Uses: starmap, zip/unzip, sorted, operator.itemgetter.
    """
    # starmap applies a function to each (key, list) pair unpacked as args
    count_pair = lambda k, v: (k, len(v))                # Lambda
    pairs = list(itertools.starmap(count_pair, groups.items()))  # starmap

    # zip / unzip pattern
    if not pairs:
        return []
    keys, counts = zip(*pairs)                           # unzip
    recombined   = list(zip(keys, counts))               # re-zip

    # sorted using operator.itemgetter as key (functions as objects)
    return sorted(recombined, key=get_count, reverse=True)  # itemgetter + sorted


# ===========================================================================
# 13.  FREQUENCY TIMELINE  (scan / accumulate / running totals)
# ===========================================================================

def frequency_timeline(freq_table: List[Tuple]) -> List[Tuple[str, int, int]]:
    """
    Attach a running cumulative total to each row.
    Uses itertools.accumulate (scan pattern).
    Returns list of (message, count, running_total).
    """
    counts = list(map(get_count, freq_table))            # map + itemgetter
    running = list(itertools.accumulate(counts))         # accumulate (scan)
    msgs    = list(map(get_message, freq_table))         # map + itemgetter
    return list(itertools.starmap(
        lambda m, c, r: (m, c, r),                      # starmap + lambda
        zip(msgs, counts, running)                       # zip three sequences
    ))


# ===========================================================================
# 14.  RARE ERROR DETECTION & PATTERN DISCOVERY
#      Closures · Partial Application · negate · takewhile / dropwhile
# ===========================================================================

def make_threshold_predicates(threshold: int):
    """
    Closure factory returning a pair of predicates (is_rare, is_common).
    Demonstrates: closure, returning multiple function objects, negate.
    """
    def is_rare(pair):                                   # Closure over threshold
        return get_count(pair) <= threshold
    is_common = negate(is_rare)                          # negate combinator
    return is_rare, is_common                            # tuple of fn objects


def detect_rare_errors(freq_table: List[Tuple], threshold: int) -> List[str]:
    """
    Errors with count <= threshold.
    Uses closure-returned predicate + filter.
    """
    is_rare, _ = make_threshold_predicates(threshold)   # unpack fn tuple
    return list(map(get_message,
                    filter(is_rare, freq_table)))        # filter + map + itemgetter


def detect_common_errors(freq_table: List[Tuple], threshold: int) -> List[str]:
    """Errors with count > threshold (complement of rare)."""
    _, is_common = make_threshold_predicates(threshold)
    return list(map(get_message,
                    filter(is_common, freq_table)))      # filter + map


# takewhile / dropwhile: split table at frequency boundary
def split_at_threshold(freq_table: List[Tuple], threshold: int):
    """
    Return (common_part, rare_part) using takewhile + dropwhile.
    Both operate lazily on the sorted (descending) table.
    """
    is_above = lambda pair: get_count(pair) > threshold  # Lambda
    common = list(itertools.takewhile(is_above, freq_table))   # takewhile
    rare   = list(itertools.dropwhile(is_above, freq_table))   # dropwhile
    return common, rare


_KNOWN_PATTERNS: FrozenSet[str] = frozenset({
    "database connection failed",
    "timeout while contacting api",
    "user authentication failed",
    "disk space low",
    "memory usage high",
    "service unavailable",
    "connection refused",
    "file not found",
    "permission denied",
    "null pointer exception",
})

# Partial application: pre-bind known set into a membership predicate
# operator.contains(a, b) == b in a  →  partial pre-binds the container
_in_known      = functools.partial(operator.contains, _KNOWN_PATTERNS)  # partial
_not_in_known  = negate(_in_known)                       # negate


def discover_new_patterns(freq_table: List[Tuple]) -> List[str]:
    """
    Messages not in known baseline.
    Point-free: compose get_message with _not_in_known check via filter.
    """
    return list(map(
        get_message,
        filter(compose(_not_in_known, get_message), freq_table)  # compose
    ))


# ===========================================================================
# 15.  PATTERN CO-OCCURRENCE  (itertools.combinations)
# ===========================================================================

def co_occurrence_pairs(messages: List[str], limit: int = 5) -> List[Tuple]:
    """
    Find message pairs that might co-occur (share normalised tokens).
    Uses itertools.combinations — combinatoric generator.
    """
    tokenize = lambda m: frozenset(m.split())            # Lambda
    tokenized = list(map(lambda m: (m, tokenize(m)), messages[:20]))  # map + slice

    pairs = list(itertools.combinations(tokenized, 2))   # combinations

    def share_tokens(pair):
        (_, t1), (_, t2) = pair
        return len(t1 & t2) >= 2

    related = list(filter(share_tokens, pairs))          # filter
    return [(a, b) for (a, _), (b, _) in related[:limit]]  # list comprehension


# ===========================================================================
# 16.  ANALYSIS ENGINE
#      Higher-order orchestration · scan · min/max/sum · reduce · enumerate
# ===========================================================================

@timed
def run_analysis(freq_table: List[Tuple], config: AnalysisConfig) -> dict:
    """
    Orchestrate all analysis using purely functional composition.
    """
    if not freq_table:
        return _empty_analysis()

    # Sequence constructors
    counts = tuple(map(get_count, freq_table))           # tuple + map + itemgetter

    # Reducing iterables
    total      = sum(counts)                             # sum
    most_freq  = max(counts)                             # max
    least_freq = min(counts)                             # min
    mean_freq  = total / len(counts)                     # arithmetic

    # functools.reduce: weighted severity score (errors weighted 2x warnings)
    # uses a made-up metric to demonstrate reduce in business logic
    msgs = list(map(get_message, freq_table))
    severity_score = functools.reduce(
        lambda acc, mc: acc + (mc[1] * 2 if "error" in mc[0] else mc[1]),
        zip(msgs, counts),
        0
    )

    # Slicing: top-N
    top_slice    = freq_table[:config.top_n]             # Slicing
    bottom_slice = list(reversed(freq_table))[:config.top_n]  # reversed + Slicing
    _ = bottom_slice

    # enumerate for ranked list
    ranked = [
        (rank, msg, cnt)
        for rank, (msg, cnt) in enumerate(top_slice, start=1)  # enumerate
    ]

    # Running totals via scan
    timeline = frequency_timeline(freq_table)

    # Predicate-based split
    common_part, rare_part = split_at_threshold(freq_table, config.rare_threshold)
    _ = common_part

    rare_msgs    = detect_rare_errors(freq_table, config.rare_threshold)
    new_patterns = discover_new_patterns(freq_table)
    co_pairs     = co_occurrence_pairs(msgs)

    # zip to align messages with their severity band
    severity_bands = list(zip(
        msgs,
        map(lambda c: "HIGH" if c > mean_freq else "LOW", counts)  # map + lambda
    ))

    return {
        "top_errors"     : ranked,
        "rare_errors"    : rare_msgs,
        "new_patterns"   : new_patterns,
        "co_pairs"       : co_pairs,
        "severity_bands" : severity_bands[:config.top_n],
        "timeline"       : timeline[:config.top_n],
        "total"          : total,
        "most_common"    : most_freq,
        "least_common"   : least_freq,
        "mean_freq"      : round(mean_freq, 2),
        "severity_score" : severity_score,
    }


def _empty_analysis() -> dict:
    return {k: [] if k not in ("total","most_common","least_common",
                                "mean_freq","severity_score") else 0
            for k in ("top_errors","rare_errors","new_patterns","co_pairs",
                      "severity_bands","timeline","total","most_common",
                      "least_common","mean_freq","severity_score")}


# ===========================================================================
# 17.  REPORT GENERATOR
#      reduce for string join · RankedStream iterator · starmap · zip
# ===========================================================================

_SEP  = "=" * 64
_DASH = "-" * 44


def _section(title: str, lines: List[str]) -> List[str]:
    """Pure function: wrap content lines in a titled section."""
    return [title, _DASH] + lines + [""]


def generate_report(analysis: dict, config: AnalysisConfig) -> str:
    """
    Build report as a list of lines then fold via reduce.
    Uses: RankedStream (custom iterator), starmap, map, zip, reduce.
    """
    out: List[str] = [_SEP, "              LOG ANALYSIS REPORT", _SEP, ""]

    # --- Most Frequent Errors via custom RankedStream iterator ---
    ranked_stream = RankedStream(
        [(msg, cnt) for _, msg, cnt in analysis["top_errors"]]
    )
    top_lines = [f"  {r}. {msg} — {cnt}" for r, (msg, cnt) in ranked_stream]
    out += _section("Most Frequent Errors", top_lines or ["  (none)"])

    # --- Rare Errors: map + lambda ---
    rare_lines = list(map(
        lambda m: f"  - {m}",                           # map + lambda
        analysis["rare_errors"]
    ))
    out += _section(
        f"Rare Errors  (frequency ≤ {config.rare_threshold})",
        rare_lines or ["  (none)"]
    )

    # --- New Patterns: zip with bullet symbols ---
    bullets    = itertools.repeat("  -")
    new_lines  = [f"{b} {p}" for b, p in
                  zip(bullets, analysis["new_patterns"])]  # zip
    out += _section("New / Uncommon Patterns", new_lines or ["  (none)"])

    # --- Severity Bands: starmap ---
    band_lines = list(itertools.starmap(
        lambda m, b: f"  [{b:4s}] {m}",                # starmap + lambda
        analysis["severity_bands"][:5]
    ))
    out += _section("Severity Bands (top 5)", band_lines or ["  (none)"])

    # --- Co-occurrence Pairs ---
    pair_lines = list(map(
        lambda p: f"  • {p[0]}  ↔  {p[1]}",           # map + lambda
        analysis["co_pairs"]
    ))
    out += _section("Possible Co-occurring Errors", pair_lines or ["  (none)"])

    # --- Cumulative Timeline: starmap ---
    tl_lines = list(itertools.starmap(
        lambda m, c, r: f"  {r:>5} total after: {m}",  # starmap
        analysis["timeline"][:5]
    ))
    out += _section("Cumulative Frequency Timeline (top 5)", tl_lines or ["  (none)"])

    # --- Summary ---
    out += [
        _DASH,
        f"Total Errors Detected : {analysis['total']}",
        f"Most common frequency : {analysis['most_common']}",
        f"Least common frequency: {analysis['least_common']}",
        f"Mean frequency        : {analysis['mean_freq']}",
        f"Severity score        : {analysis['severity_score']}",
        _SEP,
    ]

    # monoid_fold (reduce) to join lines — fold with newline as combine
    return monoid_fold("", lambda a, b: a + "\n" + b, out)  # monoid_fold


# ===========================================================================
# 18.  CLI INTERFACE
#      ChainMap for layered config · map · filter · list comprehension
# ===========================================================================

_DEFAULTS = {"rare_threshold": 2, "top_n": 10, "filepath": None}


def parse_flags(argv: List[str]) -> dict:
    """
    Parse --key=value flags from argv using map + filter + dict.
    Demonstrates: map, filter, lambda, list comprehension, ChainMap.
    """
    argv_copy = list(argv)                               # Defensive copy

    flags = [a for a in argv_copy[1:] if a.startswith("--")]  # list comp + slice
    positionals = [a for a in argv_copy[1:] if not a.startswith("--")]

    def flag_to_pair(flag: str) -> Optional[Tuple]:
        parts = flag.lstrip("-").split("=", 1)
        return tuple(parts) if len(parts) == 2 else None  # tuple constructor

    parsed_pairs = filter(None, map(flag_to_pair, flags))  # filter + map
    flag_dict    = dict(parsed_pairs)                       # dict constructor

    overrides: dict = {}
    if "rare-threshold" in flag_dict:
        overrides["rare_threshold"] = int(flag_dict["rare-threshold"])
    if "top-n" in flag_dict:
        overrides["top_n"] = int(flag_dict["top-n"])
    if positionals:
        overrides["filepath"] = positionals[0]

    # ChainMap: layered config lookup — overrides shadow defaults
    merged = collections.ChainMap(overrides, _DEFAULTS)  # ChainMap
    return dict(merged)


# ===========================================================================
# 19.  BUILT-IN SAMPLE LOG DATASET
# ===========================================================================

_SAMPLE_LOG_LINES = (                                    # tuple — immutable
    "2025-03-05 10:15:22 ERROR Database connection failed",
    "2025-03-05 10:15:23 INFO User logged in",
    "2025-03-05 10:16:01 ERROR Database connection failed",
    "2025-03-05 10:16:10 WARNING Disk space low",
    "2025-03-05 10:17:44 ERROR Timeout while contacting API",
    "2025-03-05 10:18:00 ERROR Database connection failed",
    "2025-03-05 10:18:05 INFO Health check passed",
    "2025-03-05 10:18:30 ERROR Database connection failed",
    "2025-03-05 10:19:00 WARNING Disk space low",
    "2025-03-05 10:19:15 ERROR Authentication token expired",
    "2025-03-05 10:19:20 ERROR Timeout while contacting API",
    "2025-03-05 10:19:45 ERROR Database connection failed",
    "2025-03-05 10:20:00 ERROR File permission denied on /var/log/app.log",
    "2025-03-05 10:20:10 INFO Backup completed successfully",
    "2025-03-05 10:20:20 ERROR Timeout while contacting API",
    "2025-03-05 10:20:30 ERROR Database connection failed",
    "2025-03-05 10:20:40 WARNING Memory usage high: 87%",
    "2025-03-05 10:21:00 ERROR Cache synchronization failed for node 192.168.1.42",
    "2025-03-05 10:21:10 ERROR Database connection failed",
    "2025-03-05 10:21:20 INFO User logged out",
    "2025-03-05 10:21:30 ERROR Timeout while contacting API",
    "2025-03-05 10:21:45 ERROR Database connection failed",
    "2025-03-05 10:22:00 ERROR SSL certificate validation error for host 'api.example.com'",
    "2025-03-05 10:22:10 WARNING Disk space low",
    "2025-03-05 10:22:20 ERROR Database connection failed",
    "2025-03-05 10:22:30 ERROR Queue processing delay exceeded 500ms threshold",
    "2025-03-05 10:22:40 ERROR Timeout while contacting API",
    "2025-03-05 10:22:50 ERROR Database connection failed",
    "2025-03-05 10:23:00 INFO Scheduled job started",
    "2025-03-05 10:23:10 ERROR Unexpected null value in field 'user_id' at row 13",
    "2025-03-05 10:23:20 ERROR Database connection failed",
    "2025-03-05 10:23:30 WARNING Disk space low",
    "2025-03-05 10:23:40 ERROR Timeout while contacting API",
    "2025-03-05 10:23:50 ERROR Database connection failed",
    "2025-03-05 10:24:00 ERROR Microservice heartbeat missed for service 'order-processor'",
    "2025-03-05 10:24:10 ERROR Database connection failed",
    "2025-03-05 10:24:20 WARNING Memory usage high: 91%",
    "2025-03-05 10:24:30 ERROR Timeout while contacting API",
    "2025-03-05 10:24:40 ERROR Database connection failed",
    "2025-03-05 10:24:50 INFO Metrics flushed",
    "2025-03-05 10:25:00 ERROR Database connection failed",
    "2025-03-05 10:25:10 ERROR Timeout while contacting API",
    "2025-03-05 10:25:20 ERROR Database connection failed",
    "2025-03-05 10:25:30 WARNING Disk space low",
    "2025-03-05 10:25:40 ERROR Database connection failed",
    "2025-03-05 10:25:50 ERROR Timeout while contacting API",
    "2025-03-05 10:26:00 ERROR Database connection failed",
    "2025-03-05 10:26:10 ERROR Database connection failed",
    "2025-03-05 10:26:20 ERROR Timeout while contacting API",
    "2025-03-05 10:26:30 ERROR Database connection failed",
)


def sample_log_generator() -> Iterator[str]:
    """
    Yield sample lines as a generator — avoids materialising a list.
    Demonstrates generator over a tuple iterable.
    """
    yield from _SAMPLE_LOG_LINES                         # Generator + Iterable


def write_sample_log(path: str) -> Result:
    """Write sample lines, return Result monad."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            # map to add newlines, then writelines (lazy map)
            fh.writelines(map(lambda l: l + "\n", sample_log_generator()))
        return Result.ok(path)
    except OSError as e:
        return Result.err(str(e))


# ===========================================================================
# 20.  PROGRAM ENTRYPOINT
# ===========================================================================

def build_pipeline(filepath: str):
    """
    Compose the full analysis pipeline as a sequence of pure function calls.
    Returns the raw analysis dict.
    """
    lines    = read_log_lines(filepath)                  # lazy generator
    entries  = parse_log_stream(lines)                   # lazy generator
    relevant = extract_relevant_entries(entries)         # materialise
    groups   = group_entries(relevant)                   # groupby
    freq     = frequency_table(groups)                   # sorted pairs
    return relevant, freq


def main() -> None:
    raw_config = parse_flags(sys.argv)
    config     = AnalysisConfig(
        rare_threshold=raw_config["rare_threshold"],
        top_n         =raw_config["top_n"],
        filepath      =raw_config["filepath"],
    )

    using_sample = config.filepath is None
    tmp_path: Optional[str] = None

    if using_sample:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".log", prefix="sample_")
        os.close(tmp_fd)
        write_result = write_sample_log(tmp_path)
        if not write_result.is_ok():
            print(f"ERROR: {write_result.error()}", file=sys.stderr)
            sys.exit(1)
        filepath = tmp_path
        print("No log file provided — using built-in sample dataset.\n")
    else:
        file_result = safe_open_file(config.filepath)    # Result monad
        if not file_result.is_ok():
            print(f"ERROR: {file_result.error()}", file=sys.stderr)
            sys.exit(1)
        filepath = config.filepath

    try:
        print(f"Parsing: {filepath}")
        relevant, freq = build_pipeline(filepath)
        print(f"  Relevant entries found : {len(relevant)}")
        print(f"  Unique message patterns: {len(freq)}")

        analysis = run_analysis(freq, config)            # timed decorator fires

        report = generate_report(analysis, config)
        print()
        print(report)

        print(f"  [memoize] normalize_message cache size: {len(normalize_message.cache)}")

    finally:
        if using_sample and tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    main()
