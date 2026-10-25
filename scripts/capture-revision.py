"""Capture the ten requested views from a running local prototype."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8050/')
out=Path(__file__).resolve().parents[1]/'docs/screenshots'
out.mkdir(parents=True,exist_ok=True)
def highlight(page,selector):
 for _ in range(100):
  if page.locator('.macro-focus').count() and page.locator('.macro-focus').evaluate('(el,s)=>el.matches(s)',selector):return
  page.keyboard.press('ArrowRight')
 raise AssertionError(selector)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1024,'height':1366})
 page.goto(BASE+'index.html');page.locator('[data-selected]').wait_for();page.screenshot(path=str(out/'01-public-display-home.png'),full_page=True)
 highlight(page,'.bottom-nav a[href="animals.html"]');page.screenshot(path=str(out/'02-highlighted-navigation.png'),full_page=True)
 page.goto(BASE+'species.html?animal=water-dragon');page.locator('[data-selected]').wait_for();page.screenshot(path=str(out/'03-return-option.png'),full_page=True)
 page.goto(BASE+'index.html');page.locator('[data-selected]').wait_for();page.locator('.hero').screenshot(path=str(out/'04-local-story-no-pause.png'))
 page.goto(BASE+'activity.html?animal=brushtail');page.locator('[data-selected]').wait_for();highlight(page,'[data-game="answer"][data-index="0"]');page.keyboard.press('Enter');highlight(page,'[data-game=check]');page.keyboard.press('Enter');page.locator('.quiz-result').wait_for();page.screenshot(path=str(out/'05-animal-quiz.png'),full_page=True)
 page.set_viewport_size({'width':1280,'height':1600});page.goto(BASE+'activity.html?animal=water-dragon');page.locator('[data-selected]').wait_for();highlight(page,'[data-game="item"][data-index="0"]');page.keyboard.press('Enter');page.keyboard.press('Enter');page.screenshot(path=str(out/'06-accessible-habitat.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844})
 for route,file in [('fencepost/index.html#stories','07-fencepost-home.png'),('fencepost/index.html#opportunity/habitat-demo','08-volunteer-opportunity.png'),('fencepost/index.html#register/habitat-demo','09-prototype-registration.png'),('fencepost/index.html#update/update-pond-demo','10-community-update.png')]:
  page.goto(BASE+route);page.locator('#content h1').first.wait_for();page.wait_for_load_state('networkidle');page.screenshot(path=str(out/file),full_page=True)
 b.close()
print('Captured the ten requested views')
