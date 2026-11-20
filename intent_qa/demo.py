import os
from contextlib import contextmanager

from playwright.sync_api import sync_playwright

ORDER_FORM = """<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Order demo</title>
<h1>Order demo</h1>
<form>
  <label>Customer name <input type="text" id="customer"></label>
  <label>Order note <textarea id="note"></textarea></label>
  <button type="submit">Place order</button>
</form>
<output role="status" aria-label="Order status">Ready</output>
<script>
  document.querySelector('form').onsubmit = (event) => {
    event.preventDefault();
    const customer = document.querySelector('#customer').value.trim();
    document.querySelector('output').textContent = customer
      ? 'Order received for ' + customer
      : 'Customer name is required';
  };
</script>
</html>"""


@contextmanager
def open_demo():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get("QA_BROWSER_EXECUTABLE"), headless=True
        )
        try:
            page = browser.new_page()
            page.set_default_timeout(3000)
            page.set_content(ORDER_FORM)
            yield page
        finally:
            browser.close()
