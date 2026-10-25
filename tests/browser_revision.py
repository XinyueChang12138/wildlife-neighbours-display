"""Revised three-control, carousel, quiz and content acceptance checks."""
import os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8050/')
def highlight(page,selector):
 for _ in range(100):
  current=page.locator('.macro-focus')
  if current.count() and current.evaluate('(el,selector)=>el.matches(selector)',selector):return
  page.keyboard.press('ArrowRight')
 raise AssertionError('Could not reach '+selector+' using Next')
def choose(page,selector):
 highlight(page,selector);page.keyboard.press('Enter')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1024,'height':768})
 page=context.new_page();page.clock.install();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(BASE+'animals.html');page.locator('[data-selected]').wait_for()
 first=page.locator('.macro-focus').get_attribute('href');url=page.url
 page.keyboard.press('ArrowLeft');assert page.url==url;assert page.locator('.macro-focus').get_attribute('href')=='community.html'
 page.keyboard.press('ArrowRight');assert page.locator('.macro-focus').get_attribute('href')==first
 page.keyboard.press('Enter');page.wait_for_url('**/index.html')
 assert page.get_by_role('button',name='Pause rotation',exact=True).count()==0
 position=page.locator('.story-position').inner_text();page.keyboard.press('ArrowRight');assert page.locator('.story-position').inner_text()==position
 choose(page,'[data-action="next"]');assert page.locator('.story-position').inner_text()!=position
 current=page.locator('.story-position').inner_text();page.clock.fast_forward(44000);assert page.locator('.story-position').inner_text()==current
 page.keyboard.press('ArrowLeft');page.clock.fast_forward(44000);assert page.locator('.story-position').inner_text()==current
 page.clock.fast_forward(2000);assert page.locator('.story-position').inner_text()!=current
 choose(page,'a[href^="story.html"]');page.wait_for_url('**/story.html?id=*');page.locator('.full-story').wait_for();title=page.locator('h1').inner_text();page.clock.fast_forward(180000);assert '/story.html?' in page.url;assert page.locator('h1').inner_text()==title
 choose(page,'.return-options a:first-child');page.wait_for_url('**/index.html')
 print('Back/Next wrapping, selectable Return, idle-only rotation and full-story reading passed',flush=True)
 page.goto(BASE+'activity.html?animal=brushtail');page.locator('[data-selected]').wait_for();choose(page,'[data-game="answer"][data-index="0"]');choose(page,'[data-game="check"]');assert 'mostly nocturnal' in page.locator('.quiz-result').inner_text();choose(page,'[data-game="reset"]');assert not page.locator('.quiz-result').count()
 page.goto(BASE+'activity.html?animal=water-dragon');page.locator('[data-selected]').wait_for()
 for i,zone in enumerate([0,0,0,1,1,1]):
  choose(page,f'[data-game="item"][data-index="{i}"]');choose(page,f'[data-game="zone"][data-index="{zone}"]');assert 'Placed' in page.locator('.game-announcement').inner_text()
 choose(page,'[data-game="check"]');assert 'Thoughtful choices!' in page.locator('.quiz-result').inner_text()
 # Pick up a placed item again, and move it to another destination.
 choose(page,'[data-game="item"][data-index="0"]');choose(page,'[data-game="zone"][data-index="1"]');assert 'Needs safe management' in page.locator('[data-game="item"][data-index="0"]').inner_text()
 choose(page,'.activity-links a:last-child');page.wait_for_url('**/species.html?animal=water-dragon')
 print('Keyboard-only quiz, pick/place/reposition habitat game and animal Return passed',flush=True)
 page.goto(BASE+'activity.html?animal=flying-fox');page.locator('[data-selected]').wait_for()
 for i in range(3):choose(page,f'[data-game="item"][data-index="{i}"]');choose(page,f'[data-game="zone"][data-index="{i}"]')
 choose(page,'[data-game="check"]');assert 'Thoughtful choices!' in page.locator('.quiz-result').inner_text()
 for route in ['animals.html','species.html?animal=magpie','activity.html?animal=blue-tongue','help.html','community.html','updates.html','update.html?id=update-route-demo','story.html?id=story-brushtail']:
  page.goto(BASE+route);page.locator('[data-selected]').first.wait_for();assert page.locator('.return-options a').count()==2,route
  assert not page.locator('main').get_by_text('placeholder',exact=False).count(),route
 # A real pointer gesture starts the drag before scrolling to the destination.
 page.goto(BASE+'activity.html?animal=water-dragon');source=page.locator('[data-game=item]').first;source.wait_for();source.scroll_into_view_if_needed();r=source.bounding_box();page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);page.mouse.down();page.mouse.move(r['x']+r['width']/2+15,r['y']+r['height']/2+15,steps=5);target=page.locator('[data-game=zone]').first;target.scroll_into_view_if_needed();t=target.bounding_box();page.mouse.move(t['x']+t['width']/2,t['y']+t['height']/2,steps=8);page.mouse.move(t['x']+t['width']/2+2,t['y']+t['height']/2+2);page.mouse.up();assert 'Placed Native shrub' in page.locator('.game-announcement').inner_text()
 print('All secondary routes have selectable Return and Home options; mixed match activity passed',flush=True)
 page.goto(BASE+'updates.html');page.locator('.update-card').first.wait_for();assert page.locator('.update-card').count()==4
 page.goto(BASE+'update.html?id=update-pond-demo');page.get_by_role('heading',name='Caring for the park pond',exact=True).wait_for();assert 'does not describe an activity that really occurred' in page.inner_text('main');assert 'No wildlife was handled' in page.inner_text('main')
 page.goto(BASE+'fencepost/index.html#stories');page.get_by_role('heading',name='Wildlife stories from your neighbourhood').wait_for();assert page.locator('.featured-story').count()==1;assert page.locator('.guidance-card').count()==1;assert page.locator('.opportunity-card').count()==4;assert page.locator('.update-card').count()==4
 page.goto(BASE+'fencepost/index.html#opportunity/pond-care-demo');page.get_by_role('heading',name='Care for the park pond',exact=True).wait_for();page.get_by_role('link',name='Register interest — prototype',exact=True).click();page.locator('#registration-form').wait_for();page.locator('[name=nickname]').fill('Sample helper');page.locator('[name=email]').fill('sample@example.test')
 for key in ['prototypeConsent','wildlifeConsent','safetyConsent']:page.locator('[name='+key+']').check()
 page.get_by_role('button',name='Record prototype registration').click();page.get_by_role('heading',name='My prototype registrations').wait_for();assert 'WN-DEMO-' in page.inner_text('main')
 print('Four sample updates, mobile hierarchy and a secondary-opportunity registration passed',flush=True)
 page.set_viewport_size({'width':390,'height':844})
 for route in ['index.html','activity.html?animal=water-dragon','community.html','update.html?id=update-route-demo','fencepost/index.html#stories','fencepost/index.html#activity/water-dragon','fencepost/index.html#register/garden-care-demo']:
  page.goto(BASE+route);page.wait_for_timeout(200);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),route
 assert not errors,errors
 reduced=browser.new_context(reduced_motion='reduce');other=reduced.new_page();other.clock.install();other.goto(BASE+'index.html');other.locator('.story-position').wait_for();before=other.locator('.story-position').inner_text();other.clock.fast_forward(60000);assert before==other.locator('.story-position').inner_text()
 print('Mobile/iPad layout, reduced motion and no JavaScript page errors passed',flush=True)
 browser.close()
