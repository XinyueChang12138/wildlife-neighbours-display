"""Public-display guidance only: three-button controls, privacy and safe fallback."""
import os,json
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8140/')
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
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1024,'height':768});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 page.goto(BASE+'help.html');page.locator('[data-selected]').wait_for();assert page.get_by_role('heading',name='Stay safe. Ask a wildlife rescuer.',exact=True).count()==1;assert page.locator('.wildlife-help').count()==1;assert not page.locator('main [data-action=guidance]').count();assert 'Choose a situation' not in page.locator('main').inner_text();assert page.get_by_role('heading',name='Professional contacts',exact=True).count()==1;assert 'Do not touch, feed or chase wildlife.' in page.locator('main').inner_text();assert 'Observe safely. Never approach, feed or handle wildlife.' in page.locator('footer').inner_text();assert page.locator('[data-qr]').count()>=1
 choose(page,'[data-help-action=ask]');assert 'Describe what you noticed or select one of the prompts below.' in page.locator('.wildlife-help-status').inner_text()
 for i in range(6):
  choose(page,f'[data-help-prompt="{i}"]');expected=page.locator(f'[data-help-prompt="{i}"]').inner_text();assert page.locator('#wildlife-description').input_value()==expected;choose(page,'[data-help-action=ask]');page.locator('.wildlife-response').wait_for();assert 'AI is currently unavailable.' in page.locator('.wildlife-offline').inner_text();assert page.locator('.wildlife-response h3').inner_text() in ['Professional advice recommended','Urgent assistance recommended'];assert page.locator('.wildlife-response dt').count()==3;assert 'unconfirmed' in page.locator('.wildlife-response').inner_text();assert page.locator('.wildlife-response a').get_attribute('href').startswith('https://www.qld.gov.au/')
 print('Old cards removed; heading, introduction, contacts, QR and footer preserved; six keyboard starter prompts and offline guidance passed',flush=True)
 choose(page,'#wildlife-description');url=page.url;page.keyboard.press('ArrowLeft');assert page.url==url;page.keyboard.press('ArrowRight');assert page.locator('#wildlife-description.macro-focus').count()==1
 fill(page,'I can see bleeding from a wing');choose(page,'[data-help-action=ask]');page.locator('.wildlife-response h3').filter(has_text='Urgent assistance recommended').wait_for();choose(page,'[data-help-action=clear]');assert page.locator('#wildlife-description').input_value()=='';assert not page.locator('.wildlife-response').count()
 fill(page,'email me at person@example.test');choose(page,'[data-help-action=ask]');assert 'Remove names' in page.locator('.wildlife-help-status').inner_text();assert not page.locator('.wildlife-response').count();choose(page,'[data-help-action=restart]');assert page.locator('#wildlife-description').input_value()==''
 # Exercise the API boundary with invalid output and a delayed mocked valid response.
 def config(route):
  response=route.fetch();body=response.text().replace('wildlifeHelpEndpoint: ""','wildlifeHelpEndpoint: "/api/wildlife-help"');route.fulfill(response=response,body=body)
 page.route('**/shared/config.js',config);page.reload();page.locator('#wildlife-description').wait_for();calls=[]
 def invalid(route):calls.append(route.request.post_data_json);route.fulfill(content_type='application/json',body=json.dumps({'category':'Definitely healthy','phone':'invented'}))
 page.route('**/api/wildlife-help',invalid);fill(page,'An animal is moving but seems unusual');choose(page,'[data-help-action=ask]');page.locator('.wildlife-response').get_by_text('The system could not assess this situation reliably.',exact=False).wait_for();assert page.locator('.wildlife-response h3').inner_text()=='Professional advice recommended';assert calls==[{'signs':['unusual']}]
 page.unroute('**/api/wildlife-help',invalid)
 good=page.evaluate("async()=>{const p=await import('./shared/wildlife-help-policy.js');return p.makeGuidance('moving normally',{category:'Observe safely',reason:'moving'});}")
 def live(route):calls.append(route.request.post_data_json);route.fulfill(content_type='application/json',body=json.dumps(good))
 page.route('**/api/wildlife-help',live);fill(page,'A possum is moving normally');choose(page,'[data-help-action=ask]');page.locator('.wildlife-response h3').filter(has_text='Observe safely').wait_for();assert not page.locator('.wildlife-offline').count();assert calls[-1]=={'signs':['moving']}
 page.unroute('**/api/wildlife-help',live)
 # A stalled request is cancelled by Start again; late results cannot reappear.
 page.evaluate("() => { window.fetch=(url,options)=>new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(new DOMException('Cancelled','AbortError')))); }");fill(page,'bleeding');choose(page,'[data-help-action=ask]');assert page.locator('[data-help-action=ask]').is_disabled();assert page.locator('.wildlife-help-status').inner_text()=='Reviewing your description…';choose(page,'[data-help-action=restart]');assert page.locator('#wildlife-description').input_value()=='';assert page.locator('[data-help-action=ask]').is_enabled()
 page.unroute('**/api/wildlife-help');page.unroute('**/shared/config.js');page.reload();page.locator('#wildlife-description').wait_for();fill(page,'not moving');choose(page,'.wildlife-actions a');page.wait_for_url('**/index.html');page.goto(BASE+'help.html');page.locator('#wildlife-description').wait_for();assert page.locator('#wildlife-description').input_value()==''
 print('Typing, privacy block, generic-sign-only requests, invalid/live responses, loading lock, Start again cancellation and Return passed',flush=True)
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');fill(page,'trapped');page.evaluate("window.dispatchEvent(new Event('wn-idle'))");assert page.locator('#wildlife-description').input_value()=='';assert not page.locator('.wildlife-response').count()
 fill(page,'bleeding');page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));delete document.hidden;");assert page.locator('#wildlife-description').input_value()==''
 page.clock.install();fill(page,'bleeding');page.keyboard.press('ArrowRight');page.clock.fast_forward(121000);page.wait_for_url('**/index.html');page.goto(BASE+'help.html');page.locator('#wildlife-description').wait_for();assert page.locator('#wildlife-description').input_value()==''
 assert not page.evaluate("JSON.stringify({...localStorage,...sessionStorage}).includes('bleeding')")
 page.goto(BASE+'fencepost/index.html#share');page.locator('#observation-form').wait_for();assert not page.locator('.wildlife-help').count();assert 'Ask AI' not in page.locator('main').inner_text()
 assert not errors,errors
 print('Mobile layout, idle clearing/home return, no storage, companion writing-helper removal and no console/page errors passed',flush=True);b.close()
