# Natural Language to Playwright Test Generator

Translate a plain-English test scenario into a runnable Python Playwright test. The compiler has three stages: parse sentences, validate actions against the demo's named controls, then emit reviewable pytest source. The generator runs offline. It uses a constrained English grammar so output is reproducible and unsupported instructions fail with a line number.

## Run

Use Python 3.12–3.14 and an activated virtual environment.

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m intent_qa examples/place-order.txt -o artifacts/test_generated.py
python -m pytest -q tests artifacts/test_generated.py
```

Generate the negative scenario with `python -m intent_qa examples/missing-name.txt -o artifacts/test_missing_name.py`. The CLI leaves existing files intact. Use a new output filename when regenerating. Set `QA_BROWSER_EXECUTABLE` to verify against an existing Chromium-compatible executable.

## Supported sentences

Use one action per line, with optional trailing periods. Use double quotes around names and values and JSON escaping for any embedded quotes.

```text
Open the order demo.
Enter "Mina" in "Customer name".
Enter "Front desk" in "Order note".
Click "Place order".
Check that "Order status" says "Order received for Mina".
```

The first line opens the bundled order form, and the last line checks a named result. Only the bundled form's labels and actions are recognized. Scenario values become Python string literals. A sentence cannot supply source code, a locator expression, or a destination site. Review the emitted source as an ordinary test file before using it elsewhere.

`intent_qa/scenario.py` covers grammar and target validation. `intent_qa/compiler.py` renders the validated plan. `intent_qa/demo.py` executes browser fixtures independently of generation. CI exercises both generated scenarios in Chromium and uploads the JUnit report.

Reference: [Playwright locators](https://playwright.dev/python/docs/locators).

## Verified baseline

Eleven tests passed on Windows with Python 3.14.4 and Playwright 1.65.2. This includes nine compiler checks and the generated positive and negative order scenarios in headless Chrome.
