"""Local Wildlife Help: predefined responses, privacy and three-button controls."""
import os,re
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8180/')
def highlight(page,selector):
 if (selector=='#wildlife-description' or 'data-help-prompt' in selector or selector=='[data-help-action=ask]') and page.locator('[data-help-action=edit]').is_visible():choose(page,'[data-help-action=edit]')
 for _ in range(60):
  focus=page.locator('.macro-focus')
  if focus.count() and focus.evaluate('(el,s)=>el.matches(s)',selector):return
  page.keyboard.press('ArrowRight')
 raise AssertionError('Unreachable: '+selector)
def choose(page,selector):highlight(page,selector);page.keyboard.press('Enter')
def fill(page,text):
 if page.locator('[data-help-action=edit]').is_visible():choose(page,'[data-help-action=edit]')
 page.locator('#wildlife-description').fill(text)
def clean_copy(page):assert not re.search(r'\bAI\b',page.locator('body').inner_text(),re.I)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1024,'height':768});errors=[];calls=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('request',lambda r:calls.append(r.url))
 page.goto(BASE+'help.html');page.locator('[data-selected]').wait_for();clean_copy(page)
 assert page.get_by_role('heading',name='Stay safe. Ask a wildlife rescuer.',exact=True).count()==1
 assert page.get_by_role('heading',name='Professional contacts',exact=True).count()==1
 assert page.locator('[data-qr]').count()>=1;assert not page.locator('main [data-action=guidance]').count()
 assert page.get_by_text('Wildlife Help',exact=True).count()==1
 assert page.get_by_text('Tell us what you can safely see, or select one of the common situations below.',exact=True).count()==1
 notice='This general guidance cannot confirm whether an animal is injured. Contact a wildlife professional if you are concerned.'
 assert page.get_by_text(notice,exact=True).count()==1
 choose(page,'[data-help-action=ask]');assert 'Describe what you noticed' in page.locator('.wildlife-help-status').inner_text()
 categories=['Professional advice recommended','Urgent assistance recommended','Professional advice recommended','Urgent assistance recommended','Professional advice recommended','Unable to determine']
 for i,category in enumerate(categories):
  choose(page,f'[data-help-prompt="{i}"]');expected=page.locator(f'[data-help-prompt="{i}"]').inner_text();assert page.locator('#wildlife-description').input_value()==expected
  choose(page,'[data-help-action=ask]');page.locator('.wildlife-response').wait_for();assert page.locator('.wildlife-response h3').inner_text()==category;clean_copy(page)
  assert page.locator('.wildlife-response dt').count()==3;assert page.locator('.wildlife-response a').get_attribute('href').startswith('https://www.qld.gov.au/')
 assert page.locator('.wildlife-response p').filter(has_text='There is not enough information to assess the situation.').count()==1
 choose(page,'[data-help-action=edit]');assert page.locator('#wildlife-description').input_value()=='I cannot tell if it is hurt'
 choose(page,'#wildlife-description');url=page.url;page.keyboard.press('ArrowLeft');assert page.url==url;page.keyboard.press('ArrowRight');assert page.locator('#wildlife-description.macro-focus').count()==1
 fill(page,'The animal is moving normally');choose(page,'[data-help-action=ask]');page.locator('.wildlife-response h3').filter(has_text='Observe safely').wait_for();clean_copy(page)
 fill(page,'moving normally but bleeding');choose(page,'[data-help-action=ask]');page.locator('.wildlife-response h3').filter(has_text='Urgent assistance recommended').wait_for()
 choose(page,'[data-help-action=clear]');assert page.locator('#wildlife-description').input_value()=='';assert not page.locator('.wildlife-response').count()
 fill(page,'Email me at person@example.test');choose(page,'[data-help-action=ask]');assert 'Remove names' in page.locator('.wildlife-help-status').inner_text();choose(page,'[data-help-action=restart]');assert page.locator('#wildlife-description').input_value()==''
 print('Exact wording, all prompts/categories, no visible model wording, typing, keyboard controls, editing, clearing and privacy checks passed',flush=True)
 page.clock.install();fill(page,'not moving');choose(page,'[data-help-action=ask]');assert page.locator('[data-help-action=ask]').is_disabled();assert page.locator('.wildlife-help-status').inner_text()=='Checking the information…';choose(page,'[data-help-action=restart]');page.clock.fast_forward(300);assert not page.locator('.wildlife-response').count();assert page.locator('#wildlife-description').input_value()==''
 fill(page,'not moving');page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));delete document.hidden;");assert page.locator('#wildlife-description').input_value()==''
 fill(page,'bleeding');page.evaluate("window.dispatchEvent(new Event('wn-idle'))");assert page.locator('#wildlife-description').input_value()==''
 fill(page,'bleeding');page.keyboard.press('ArrowRight');page.clock.fast_forward(121000);page.wait_for_url('**/index.html');page.goto(BASE+'help.html');page.locator('#wildlife-description').wait_for();assert page.locator('#wildlife-description').input_value()==''
 fill(page,'trapped');choose(page,'.wildlife-actions a');page.wait_for_url('**/index.html');page.goto(BASE+'help.html');page.locator('#wildlife-description').wait_for();assert page.locator('#wildlife-description').input_value()==''
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');clean_copy(page)
 assert not any('/api/' in url for url in calls),calls
 assert not page.evaluate("JSON.stringify({...localStorage,...sessionStorage}).includes('bleeding')")
 assert not errors,errors
 print('Loading lock/cancellation, visibility and idle clearing, Return, mobile layout, zero API requests/storage and no console/page errors passed',flush=True);b.close()
