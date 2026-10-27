"""Capture contact options and confirmations without activating a telephone link."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8200/')
out=Path(__file__).resolve().parents[1]/'docs/screenshots'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':1600})
 page.goto(BASE+'help.html');page.locator('.assistance-contacts').wait_for();page.locator('.assistance-contacts').screenshot(path=str(out/'21-assistance-contacts.png'))
 page.set_viewport_size({'width':1280,'height':1024})
 for ident,name in [('rspca-qld','22-wildlife-call-confirmation.png'),('triple-zero','23-emergency-call-confirmation.png')]:
  page.locator('[data-contact-id='+ident+']').click();page.locator('.contact-dialog[open]').wait_for();page.screenshot(path=str(out/name));page.get_by_role('button',name='Cancel',exact=True).click()
 b.close()
print('Captured contact options and two confirmation dialogs; no calls placed')
