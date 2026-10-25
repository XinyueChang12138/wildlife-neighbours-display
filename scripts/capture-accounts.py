"""Additional review images for account, comment and writer changes."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8080/')
out=Path(__file__).resolve().parents[1]/'docs/screenshots'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844})
 page.goto(BASE+'fencepost/index.html#login');page.get_by_role('heading',name='Sign in to Fencepost').wait_for();page.screenshot(path=str(out/'11-demo-login.png'),full_page=True)
 page.get_by_role('button',name='Use resident account',exact=True).click();page.get_by_role('button',name='Sign in',exact=True).click();page.get_by_role('heading',name='Hello, Taylor',exact=True).wait_for();page.screenshot(path=str(out/'12-resident-profile.png'),full_page=True)
 page.goto(BASE+'fencepost/index.html#share');page.locator('[name=description]').fill('saw a possible possum resting quietly in the park');page.get_by_role('button',name='Ask AI for writing help',exact=True).click();page.locator('#writer-consent').check();page.get_by_role('button',name='Prepare writing suggestion',exact=True).click();page.locator('#writer-suggestion').wait_for();page.screenshot(path=str(out/'15-writing-help.png'),full_page=True)
 page.goto(BASE+'fencepost/index.html#story/story-brushtail');page.locator('#comment-form').wait_for();page.screenshot(path=str(out/'16-direct-comments.png'),full_page=True)
 page.goto(BASE+'fencepost/index.html#login');page.get_by_role('button',name='Use moderator account',exact=True).click();page.get_by_role('button',name='Sign in',exact=True).click();page.get_by_role('heading',name='Moderator dashboard',exact=True).wait_for();page.set_viewport_size({'width':1080,'height':1000})
 page.goto(BASE+'fencepost/index.html#moderator/pending');page.get_by_role('heading',name='Posts awaiting approval',exact=True).wait_for();page.screenshot(path=str(out/'13-moderator-posts.png'),full_page=True)
 page.goto(BASE+'fencepost/index.html#moderator/reports');page.get_by_role('heading',name='Reported Comments',exact=True).wait_for();page.screenshot(path=str(out/'14-reported-comments.png'),full_page=True)
 b.close()
print('Captured six account/comment/writing screenshots')
