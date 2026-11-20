import argparse
import sys
from pathlib import Path

from .compiler import compile_scenario
from .scenario import ScenarioError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile plain-English demo steps to a pytest test"
    )
    parser.add_argument("scenario", type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.output.suffix != ".py":
            raise ScenarioError("Output must be a Python .py file")
        if args.scenario.resolve() == args.output.resolve():
            raise ScenarioError(
                "Scenario input and generated output must be different files"
            )
        output = compile_scenario(args.scenario.read_text("utf-8-sig"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as file:
            file.write(output)
    except (ScenarioError, OSError, UnicodeError) as exc:
        print(f"Cannot generate test: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
