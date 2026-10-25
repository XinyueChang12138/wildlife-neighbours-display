import os
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context();page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));base=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8020/')
 page.goto(base+'fencepost/index.html#share');page.locator('#observation-form').wait_for()
 page.locator('[name=behaviour]').fill('Resting');page.locator('[name=description]').fill('A possum rested in a tree.')
 page.locator('[name=photo]').set_input_files(str(Path(__file__).resolve().parents[1]/'assets/brushtail-peeking.jpg'));page.locator('#photo-preview img').wait_for();page.locator('[name=safeConsent]').check();page.get_by_role('button',name='Preview submission').click();page.get_by_role('button',name='Send for review',exact=True).click();page.get_by_role('heading',name='Sent for review — not yet public').wait_for()
 page.goto(base+'fencepost/index.html#moderator');page.get_by_role('button',name='Use moderator account',exact=True).click();page.get_by_role('button',name='Sign in',exact=True).click();page.get_by_role('heading',name='Moderator dashboard',exact=True).wait_for();page.goto(base+'fencepost/index.html#moderator/pending');page.get_by_role('heading',name='Posts awaiting approval',exact=True).wait_for()
 form=page.locator('.moderation-form').filter(has=page.locator('textarea[name=publicText]',has_text='A possum rested in a tree.'));form.locator('xpath=..').locator('summary').click()
 page.locator('button[data-action=view-media]').last.click();page.locator('[id^=media-] img').wait_for();form.locator('[name=reason]').fill('Privacy risk: reject demonstration media.');form.get_by_role('button',name='Reject',exact=True).click();page.wait_for_timeout(200)
 assert 'A possum rested in a tree.' not in [x['storyText'] for x in page.evaluate("async()=> (await import('/shared/api.js')).stories()")]
 print('Optional image upload, private preview and rejection passed',flush=True)
 page.goto(base+'fencepost/index.html#rescue');page.locator('#observation-form').wait_for();page.locator('[name=behaviour]').fill('Possibly trapped');page.locator('[name=description]').fill('Sample welfare report');page.locator('[name=privateRescueLocation]').fill('PRIVATE TEST LOCATION');page.locator('[name=condition]').fill('Not moving');page.locator('[name=safeConsent]').check();page.get_by_role('button',name='Preview submission').click();assert 'PRIVATE TEST LOCATION' not in page.inner_text('main');page.get_by_role('button',name='Send for review',exact=True).click();page.get_by_role('heading',name='Sent for review — not yet public').wait_for();page.goto(base+'index.html');page.locator('.hero').wait_for();assert 'PRIVATE TEST LOCATION' not in page.inner_text('main')
 print('Private welfare report is hidden from preview and public display',flush=True)
 page.goto(base+'community.html');page.locator('[data-qr] svg').first.wait_for();assert '#stories' in page.locator('[data-qr]').first.get_attribute('data-qr');assert '#opportunity/habitat-demo' in page.locator('[data-qr]').nth(1).get_attribute('data-qr')
 page.locator('a.text-link').click();page.locator('dialog[open]').wait_for();page.keyboard.press('ArrowLeft');assert page.locator('dialog[open]').count()==1;page.keyboard.press('ArrowRight');page.keyboard.press('Enter');assert not page.locator('dialog[open]').count()
 print('QR targets and physical Back from phone handoff passed',flush=True)
 # The revised dedicated keyboard acceptance suite covers the full three-button journey.
 page.goto(base+'species.html?animal=brushtail');page.locator('.activity-start').click();page.locator('[data-game=answer]').first.click();page.locator('[data-game=check]').click();assert 'mostly nocturnal' in page.locator('.quiz-result').inner_text()
 print('Species activity and explanation passed',flush=True)
 assert not errors,errors;b.close()
