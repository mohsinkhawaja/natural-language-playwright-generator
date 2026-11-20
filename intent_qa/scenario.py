import json
import re
from dataclasses import dataclass
from enum import Enum

QUOTED = r'"(?:[^"\\]|\\.)*"'
MAX_STEPS = 20
MAX_VALUE = 200
DEMO = "Open the order demo"
TEXT_FIELDS = frozenset({"Customer name", "Order note"})
BUTTONS = frozenset({"Place order"})
STATUSES = frozenset({"Order status"})


class ScenarioError(ValueError):
    """A line is outside the supported scenario grammar or demo contract."""


class Opcode(Enum):
    OPEN = "open"
    ENTER = "enter"
    CLICK = "click"
    CHECK = "check"


@dataclass(frozen=True)
class Action:
    opcode: Opcode
    target: str = ""
    value: str = ""


def _quoted(raw: str) -> str:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ScenarioError("Invalid JSON string inside quotes") from exc
    if len(value) > MAX_VALUE or any(
        ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in value
    ):
        raise ScenarioError(
            "Quoted value exceeds limit or contains unsupported characters"
        )
    return value


def _known(raw: str, allowed: frozenset[str]) -> str:
    value = _quoted(raw)
    if value not in allowed:
        raise ScenarioError(
            f"Unknown demo target {value!r}. Use one of {', '.join(sorted(allowed))}."
        )
    return value


def _parse_line(text: str) -> Action:
    if text == DEMO:
        return Action(Opcode.OPEN)
    enter = re.fullmatch(rf"Enter ({QUOTED}) in ({QUOTED})", text)
    if enter:
        return Action(Opcode.ENTER, _known(enter[2], TEXT_FIELDS), _quoted(enter[1]))
    click = re.fullmatch(rf"Click ({QUOTED})", text)
    if click:
        return Action(Opcode.CLICK, _known(click[1], BUTTONS))
    check = re.fullmatch(rf"Check that ({QUOTED}) says ({QUOTED})", text)
    if check:
        return Action(Opcode.CHECK, _known(check[1], STATUSES), _quoted(check[2]))
    raise ScenarioError("Use an Open, Enter, Click, or Check sentence from the README")


def parse_scenario(source: str) -> tuple[Action, ...]:
    if len(source) > 10_000:
        raise ScenarioError("Scenario exceeds 10,000 characters")
    steps = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if len(steps) == MAX_STEPS:
            raise ScenarioError(f"Scenario exceeds {MAX_STEPS} steps")
        try:
            steps.append(_parse_line(line.removesuffix(".")))
        except ScenarioError as exc:
            raise ScenarioError(f"Line {number}: {exc}") from exc
    if not steps or steps[0].opcode is not Opcode.OPEN:
        raise ScenarioError("The first step must open the bundled demo")
    if any(step.opcode is Opcode.OPEN for step in steps[1:]):
        raise ScenarioError("Open appears exactly once")
    if steps[-1].opcode is not Opcode.CHECK:
        raise ScenarioError("The final step must check a result")
    return tuple(steps)
