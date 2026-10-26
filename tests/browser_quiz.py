"""Complete multiple-choice journeys using only Back / Choose / Next."""
import json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8110/')
QUIZZES=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {quizzes} from './shared/quiz-data.js'; console.log(JSON.stringify(quizzes))"],text=True))
def selected(page,selector):
 return page.locator('[data-quiz-option].macro-focus').evaluate('(el,s)=>el.matches(s)',selector)
def choose(page,selector):
 for _ in range(10):
  if selected(page,selector):page.keyboard.press('Enter');return
  page.keyboard.press('ArrowRight')
 raise AssertionError('Unreachable with three buttons: '+selector)
def start(page,animal):
 page.goto(BASE+'activity.html?animal='+animal);page.locator('[data-quiz-answer="0"].macro-focus').wait_for()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1280,'height':900});errors=[];console_errors=[];fallback_check=[False];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' and not fallback_check[0] else None)
 for animal,questions in QUIZZES.items():
  start(page,animal);url=page.url
  assert page.locator('[data-quiz-answer]').count()==3
  assert page.locator('[draggable=true],[data-game],audio').count()==0
  assert page.locator('[data-quiz-option].macro-focus').count()==1
  page.keyboard.press('ArrowLeft');assert selected(page,'.quiz-return');assert page.url==url
  page.keyboard.press('ArrowRight');assert selected(page,'[data-quiz-answer="0"]')
  # Physical dock buttons use exactly the same movement and selection rules.
  page.locator('[data-control=back]').click();assert selected(page,'.quiz-return');assert page.url==url
  page.locator('[data-control=next]').click();assert selected(page,'[data-quiz-answer="0"]')
  page.locator('[data-control=next]').click();assert selected(page,'[data-quiz-answer="1"]')
  page.locator('[data-control=back]').click();assert selected(page,'[data-quiz-answer="0"]')
  for i,q in enumerate(questions):
   assert f'Question {i+1} of 3' in page.locator('.quiz-kicker').inner_text()
   assert page.locator('.quiz-answers button').count()==3
   for box in page.locator('.quiz-answers button').all():
    r=box.bounding_box();assert r['height']>=44 and r['width']>=44
   if i==0:
    wrong=(q['correct']+1)%3;choose(page,f'[data-quiz-answer="{wrong}"]')
    assert page.locator('.quiz-feedback h3').inner_text()=='Not quite'
    assert q['answers'][q['correct']] in page.locator('.quiz-feedback').inner_text()
    assert q['explanation'] in page.locator('.quiz-feedback').inner_text()
    assert selected(page,'[data-quiz-action=next]')
    page.keyboard.press('ArrowLeft');assert selected(page,'.quiz-return')
    page.keyboard.press('ArrowRight');assert selected(page,'[data-quiz-action=next]')
    choose(page,'[data-quiz-action=retry]');assert not page.locator('.quiz-feedback').count()
    assert selected(page,'[data-quiz-answer="0"]')
    assert f'Question {i+1} of 3' in page.locator('.quiz-kicker').inner_text()
   choose(page,f'[data-quiz-answer="{q["correct"]}"]')
   assert page.locator('.quiz-feedback h3').inner_text()=='Correct'
   assert q['explanation'] in page.locator('.quiz-feedback').inner_text()
   assert page.locator('.quiz-source a').get_attribute('href')==q['source']['url']
   page.wait_for_timeout(150);assert page.locator('.quiz-feedback').count()==1
   assert selected(page,'[data-quiz-action=next]');page.keyboard.press('Enter')
  assert page.locator('.quiz-total').inner_text()=='3 of 3 correct'
  choose(page,'[data-quiz-action=review]');assert page.locator('.quiz-review li').count()==3
  assert selected(page,'.quiz-review summary');page.keyboard.press('Enter');assert not page.locator('.quiz-review details').first.get_attribute('open')=='';page.keyboard.press('Enter');assert page.locator('.quiz-review details').first.get_attribute('open')==''
  for q in questions:assert q['explanation'] in page.locator('.quiz-review').inner_text()
  choose(page,'[data-quiz-action=summary]');assert page.locator('.quiz-total').inner_text()=='3 of 3 correct'
  choose(page,'[data-quiz-action=restart]');assert 'Question 1 of 3' in page.locator('.quiz-kicker').inner_text()
  assert selected(page,'[data-quiz-answer="0"]');assert not page.locator('.quiz-feedback,.quiz-total').count()
  choose(page,'.quiz-return');page.wait_for_url('**/species.html?animal='+animal)
  print(animal+': three-button wrapping, wrong/correct feedback, retry, all questions, review, reset and Return passed',flush=True)
 # Another animal always starts afresh, including after completion/reload.
 start(page,'magpie')
 for q in QUIZZES['magpie']:choose(page,f'[data-quiz-answer="{q["correct"]}"]');choose(page,'[data-quiz-action=next]')
 choose(page,'a[href="animals.html"]');page.wait_for_url('**/animals.html');page.locator('a[href="species.html?animal=kangaroo"]').click();page.locator('.activity-start').click();page.locator('[data-quiz-answer="0"]').wait_for();assert 'Question 1 of 3' in page.locator('.quiz-kicker').inner_text();page.reload();page.locator('[data-quiz-answer="0"].macro-focus').wait_for()
 # The volume knob must never alter question/focus state.
 before=page.locator('.quiz-content').inner_text();focus=page.locator('.macro-focus').inner_text();page.evaluate("window.dispatchEvent(new CustomEvent('wn-knob',{detail:{delta:1}}))");assert before==page.locator('.quiz-content').inner_text();assert focus==page.locator('.macro-focus').inner_text()
 # Local atlas loads, and a designed fallback replaces it if unavailable.
 assert page.locator('svg.art image').evaluate('async el => {const r=await fetch(el.getAttribute("href"));return r.ok}')
 fallback_check[0]=True
 page.route('**/neighbours-illustrations.webp',lambda route:route.abort())
 start(page,'water-dragon');page.wait_for_function('document.querySelector("svg.art image").getAttribute("href").includes("neutral-fallback.svg")');assert 'illustration unavailable' in page.locator('svg.art').get_attribute('aria-label').lower() or 'unavailable' in page.locator('svg.art').get_attribute('aria-label').lower()
 page.unroute('**/neighbours-illustrations.webp');fallback_check[0]=False
 for width,height in [(1024,768),(390,844),(768,1024)]:
  page.set_viewport_size({'width':width,'height':height});start(page,'blue-tongue');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert page.locator('[data-quiz-answer]').count()==3
 # The companion mounts the identical component; keyboard and touch both work.
 page.goto(BASE+'fencepost/index.html#activity/flying-fox');page.locator('[data-quiz-answer="0"]').wait_for();page.keyboard.press('ArrowLeft');assert page.locator('.quiz-return').evaluate('el=>el===document.activeElement');page.keyboard.press('ArrowRight');page.keyboard.press('Enter');assert page.locator('.quiz-feedback').count()==1;page.locator('[data-quiz-action=retry]').click();assert page.locator('[data-quiz-answer="0"]').evaluate('el=>el===document.activeElement');page.locator('.quiz-return').click();page.wait_for_url('**#species/flying-fox')
 reduced=browser.new_context(reduced_motion='reduce');r=reduced.new_page();r.goto(BASE+'activity.html?animal=magpie');r.locator('[data-quiz-answer="0"]').wait_for();assert r.locator('[data-quiz-answer="0"]').evaluate('el=>getComputedStyle(el).animationName')=='none';reduced.close()
 assert not errors,errors
 assert not console_errors,console_errors
 print('Another-animal and reload resets, knob isolation, artwork/fallback, iPad/mobile, companion keyboard/touch, reduced motion and no JS errors passed',flush=True)
 browser.close()
