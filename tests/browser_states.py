import os
from pathlib import Path
from playwright.sync_api import sync_playwright
base=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8020/')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=b.new_context(viewport={'width':390,'height':844})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(base+'fencepost/index.html#moderator');page.get_by_role('button',name='Enter local demo moderator').click();page.get_by_role('heading',name='Human moderation').wait_for()
 f=page.locator('#outcome-form');f.locator('[name=title]').fill('Sample park preparation');f.locator('[name=completedAt]').fill('2026-01-01');f.locator('[name=actionsCompleted]').fill('Sample volunteers prepared native seedlings.');f.locator('[name=communityMessage]').fill('Sample update; no measured impact is claimed.');f.locator('[name=checked]').check();f.locator('[name=outcomePhoto]').set_input_files(str(Path(__file__).resolve().parents[1]/'assets/brushtail-peeking.jpg'));f.get_by_role('button',name='Publish Community Update').click();page.get_by_text('Community Update published.',exact=True).wait_for()
 page.goto(base+'index.html');page.locator('.outcome summary').filter(has_text='Sample park preparation').wait_for();page.locator('.outcome summary').click();page.locator('.outcome img').wait_for();print('Community Update and reviewed image publication passed',flush=True)
 # Missing image fallback.
 awaitable=page.evaluate("async()=>{const m=await import('./shared/ui.js');const img=document.createElement('img');document.querySelector('main').append(img);m.setupImages(document);img.src='assets/does-not-exist.jpg';return true;}")
 page.wait_for_function("Array.from(document.images).some(i=>i.src.endsWith('/assets/placeholder.svg'))")
 # Empty feed.
 page.evaluate("()=>{const s=JSON.parse(localStorage.getItem('wn-demo-v2'));s.stories=[];localStorage.setItem('wn-demo-v2',JSON.stringify(s));}");page.reload();page.get_by_text('No approved stories are available yet.',exact=True).wait_for();print('Missing image and empty feed states passed',flush=True)
 # Software knob only changes volume; Next remains navigation.
 context2=b.new_context();p2=context2.new_page()
 def software(route):
  response=route.fetch();text=response.text().replace('mode: "system"','mode: "software"');route.fulfill(response=response,body=text)
 p2.route('**/shared/config.js',software);p2.goto(base+'animals.html');p2.locator('[data-selected]').wait_for();before=p2.locator('[data-selected]').get_attribute('href');p2.evaluate("window.dispatchEvent(new CustomEvent('wn-knob',{detail:{delta:1}}))");assert p2.locator('[data-selected]').get_attribute('href')==before;assert '80%' in p2.locator('#volume-state').inner_text();assert abs(float(p2.evaluate("sessionStorage.getItem('wn-volume')"))-.8)<.001;print('Software knob volume and unchanged selection passed',flush=True)
 # Configured backend failure fails closed rather than using local demo content.
 context3=b.new_context();p3=context3.new_page()
 def connected(route):
  response=route.fetch();text=response.text().replace('supabaseUrl: ""','supabaseUrl: "https://backend.invalid"').replace('supabaseAnonKey: ""','supabaseAnonKey: "test-anon"');route.fulfill(response=response,body=text)
 p3.route('**/shared/config.js',connected);p3.route('https://backend.invalid/**',lambda r:r.abort());p3.goto(base+'index.html');p3.get_by_role('heading',name='We could not load the latest stories.').wait_for();assert not p3.locator('.hero').count();print('Backend failure fails closed passed',flush=True)
 assert not errors,errors;b.close()
