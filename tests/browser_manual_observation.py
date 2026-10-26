"""Manual authoring: text, optional image, preview/edit/cancel and human review."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8110/')
ENTRY=os.environ.get('WN_TEST_ENTRY','fencepost/index.html')
def route(page,path):page.goto(BASE+ENTRY+'#'+path)
def fill(page,description):
 page.locator('#observation-form [name=behaviour]').fill('Resting near vegetation')
 page.locator('#observation-form [name=description]').fill(description)
 page.locator('#observation-form [name=publicArea]').select_option('Community garden area')
 page.locator('#observation-form [name=safeConsent]').check()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844});errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('request',lambda r:requests.append(r.url))
 route(page,'share');page.locator('#observation-form').wait_for();description='A possible blue-tongued lizard paused beside the garden mulch.';fill(page,description)
 # Nothing needs generating or external assistance to preview the public version.
 page.get_by_role('button',name='Preview submission',exact=True).click();page.get_by_role('heading',name='This is what may become public after review').wait_for();assert description in page.locator('#content').inner_text()
 page.get_by_role('button',name='Edit',exact=True).click();page.locator('#observation-form').wait_for();assert page.locator('textarea[name=description]').input_value()==description
 description='A possible blue-tongued lizard rested beside the garden mulch.';page.locator('textarea[name=description]').fill(description);page.locator('[name=safeConsent]').check();page.get_by_role('button',name='Preview submission',exact=True).click();page.get_by_role('button',name='Cancel',exact=True).click();page.get_by_role('heading',name='Wildlife stories from your neighbourhood').wait_for();route(page,'share');assert page.locator('textarea[name=description]').input_value()==''
 fill(page,description);page.get_by_role('button',name='Preview submission',exact=True).click();page.get_by_role('button',name='Send for review',exact=True).click();page.get_by_role('heading',name='Sent for review — not yet public',exact=True).wait_for()
 assert not any('/api/assistant' in u for u in requests)
 print('Guest text-only authoring, public preview, edit, cancel, clean restart and Sent for review passed',flush=True)
 route(page,'login');page.get_by_role('button',name='Use resident account',exact=True).click();page.get_by_role('button',name='Sign in',exact=True).click();page.get_by_role('heading',name='Hello, Taylor',exact=True).wait_for()
 route(page,'share');photo_text='A possible magpie foraged beside the community garden.';fill(page,photo_text);page.locator('[name=photo]').set_input_files(str(Path(__file__).resolve().parents[1]/'assets/brushtail-peeking.jpg'));page.locator('#photo-preview img').wait_for();page.get_by_role('button',name='Preview submission',exact=True).click();page.locator('#content img').wait_for();page.get_by_role('button',name='Edit',exact=True).click();page.locator('#photo-preview img').wait_for();assert page.locator('textarea[name=description]').input_value()==photo_text;page.locator('[name=safeConsent]').check();page.get_by_role('button',name='Preview submission',exact=True).click();page.get_by_role('button',name='Send for review',exact=True).click();page.get_by_role('heading',name='Sent for review — not yet public',exact=True).wait_for()
 route(page,'my-observations');page.get_by_role('heading',name='My observations',exact=True).wait_for();assert photo_text in page.locator('#content').inner_text();assert 'Awaiting review' in page.locator('#content').inner_text()
 route(page,'login');page.get_by_role('button',name='Use moderator account',exact=True).click();page.get_by_role('button',name='Sign in',exact=True).click();page.get_by_role('heading',name='Moderator dashboard',exact=True).wait_for();route(page,'moderator/pending');page.get_by_role('heading',name='Posts awaiting approval',exact=True).wait_for();form=page.locator('.moderation-form').filter(has=page.locator('textarea[name=publicText]',has_text=photo_text));assert form.count()==1;article=form.locator('xpath=..');article.locator('summary').click();article.get_by_role('button',name='View private media (moderator only)',exact=True).click();article.locator('img').wait_for()
 assert not any('/api/assistant' in u for u in requests)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 print('Resident optional photograph persists through edit, remains pending and is privately available to the moderator; no assistance request, console errors or mobile overflow',flush=True);b.close()
