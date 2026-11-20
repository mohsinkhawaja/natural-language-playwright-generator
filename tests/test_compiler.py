import ast
import json
from pathlib import Path

import pytest

from intent_qa.compiler import compile_scenario
from intent_qa.scenario import Opcode, ScenarioError, parse_scenario


def test_compiles_readable_reviewable_code():
    scenario = Path("examples/place-order.txt").read_text("utf-8")
    plan = parse_scenario(scenario)
    assert [step.opcode for step in plan] == [
        Opcode.OPEN,
        Opcode.ENTER,
        Opcode.ENTER,
        Opcode.CLICK,
        Opcode.CHECK,
    ]
    source = compile_scenario(scenario)
    parsed = ast.parse(source)
    assert "Order received for Mina" in source
    assert {
        node.name for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)
    } == {"test_order_scenario"}


def test_user_input_can_only_become_a_literal():
    value = """'); print("data"); #"""
    source = compile_scenario(
        "Open the order demo.\n"
        f'Enter {json.dumps(value)} in "Customer name".\n'
        'Check that "Order status" says "Ready".\n'
    )
    calls = [node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call)]
    fill = next(
        node
        for node in calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "fill"
    )
    assert ast.literal_eval(fill.args[0]) == value
    assert not any(
        isinstance(node.func, ast.Name) and node.func.id == "print" for node in calls
    )


@pytest.mark.parametrize(
    ("steps", "error"),
    [
        ('Open "https://example.invalid".', "Line 1"),
        ('Open the order demo.\nClick "Unknown".', "Unknown demo target"),
        ("Open the order demo.\nOpen the order demo.", "exactly once"),
        ('Open the order demo.\nClick "Place order".', "final step"),
        ('Click "Place order".\nCheck that "Order status" says "Ready".', "first step"),
        ('Open the order demo.\nEnter "\\uD800" in "Customer name".', "unsupported"),
        ("Open the order demo.\n" + 'Click "Place order".\n' * 20, "exceeds 20"),
    ],
)
def test_rejects_unknown_or_unbounded_instructions(steps, error):
    with pytest.raises(ScenarioError, match=error):
        compile_scenario(steps)
