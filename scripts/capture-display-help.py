"""Capture only the public help box and its predefined result."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8140/')
out=Path(__file__).resolve().parents[1]/'docs/screenshots'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1100})
 page.goto(BASE+'help.html');page.locator('#wildlife-description').wait_for();page.screenshot(path=str(out/'19-display-help.png'),full_page=True)
 page.locator('[data-help-prompt="1"]').click();page.locator('[data-help-action=ask]').click();page.locator('.wildlife-response').wait_for();page.screenshot(path=str(out/'20-display-help-response.png'),full_page=True)
 b.close()
print('Captured Wildlife Help entry and predefined result')
