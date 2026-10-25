import os
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=b.new_context(viewport={'width':1440,'height':1100})
 page=ctx.new_page();page.clock.install();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 base=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8020/')
 page.goto(base+'fencepost/index.html#share')
 page.locator('#observation-form').wait_for()
 page.locator('[name=possibleSpecies]').select_option('not-sure')
 page.locator('[name=behaviour]').fill('Sitting among branches')
 page.locator('[name=description]').fill('A mystery animal rested in the park trees.')
 page.locator('[name=safeConsent]').check();page.get_by_role('button',name='Preview submission').click()
 page.get_by_role('button',name='Send for review',exact=True).click();page.get_by_role('heading',name='Sent for review — not yet public').wait_for()
 page.goto(base+'index.html');page.locator('.hero').wait_for();assert 'mystery animal' not in page.inner_text('main')
 print('Text-only Not sure submission remains private')
 page.goto(base+'fencepost/index.html#moderator');page.get_by_role('button',name='Enter local demo moderator').click()
 page.get_by_role('heading',name='Human moderation').wait_for()
 form=page.locator('.moderation-form').filter(has=page.locator('textarea[name=publicText]',has_text='A mystery animal'))
 form.locator('xpath=..').locator('summary').click()
 for k in ['face','house','plate','location','welfare']:form.locator('[name='+k+']').check()
 form.locator('[name=reason]').fill('Privacy reviewed; broad area only.')
 form.get_by_role('button',name='Approve and publish').click()
 page.wait_for_timeout(200)
 page.goto(base+'index.html');page.get_by_text('A mystery animal rested in the park trees.',exact=True).wait_for()
 assert 'DEMO PRIVATE LOCATION' not in page.inner_text('main')
 print('Moderator approval appears in public feed without private location')
 page.goto(base+'fencepost/index.html#register/habitat-demo');page.locator('#registration-form').wait_for()
 page.get_by_role('button',name='Record prototype registration').click();assert 'Check the marked fields' in page.inner_text('#feedback')
 page.locator('[name=nickname]').fill('Demo helper');page.locator('[name=email]').fill('demo@example.test')
 for k in ['prototypeConsent','wildlifeConsent','safetyConsent']:page.locator('[name='+k+']').check()
 page.get_by_role('button',name='Record prototype registration').click();page.wait_for_url('**#registrations')
 page.get_by_role('heading',name='My prototype registrations').wait_for();assert 'WN-DEMO-' in page.inner_text('main')
 page.reload();page.get_by_role('button',name='Cancel',exact=True).click();page.get_by_role('button',name='Restore',exact=True).wait_for();page.get_by_role('button',name='Restore',exact=True).click()
 page.get_by_role('button',name='Edit',exact=True).click();page.locator('[name=nickname]').fill('Edited helper')
 for k in ['prototypeConsent','wildlifeConsent','safetyConsent']:page.locator('[name='+k+']').check()
 page.get_by_role('button',name='Record prototype registration').click();page.get_by_text('Edited helper · demo@example.test').wait_for()
 print('Registration validation, persistence, edit, cancel and restore passed')
 for route in ['index.html','animals.html','species.html?animal=magpie','help.html','community.html']:
  page.goto(base+route);page.locator('[data-selected]').first.wait_for()
  page.keyboard.press('ArrowRight');assert page.locator('.macro-focus').count()==1
  before=page.url;page.keyboard.press('ArrowLeft');assert page.url==before
  if route!='index.html':page.locator('.return-options a').first.click();page.wait_for_url('**/animals.html' if route.startswith('species') else '**/index.html')
 page.goto(base+'species.html?animal=magpie');page.locator('h1').filter(has_text='Australian magpie').wait_for()
 page.locator('[data-selected]').first.wait_for();page.clock.fast_forward(121000);page.wait_for_url('**/index.html')
 print('Three-key focus and idle return passed')
 page.set_viewport_size({'width':390,'height':844})
 for route in ['index.html','community.html','animals.html','help.html','fencepost/index.html#share','fencepost/index.html#community']:
  page.goto(base+route);page.wait_for_timeout(150)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),route
 print('Mobile overflow passed')
 assert not errors,errors
 b.close()
