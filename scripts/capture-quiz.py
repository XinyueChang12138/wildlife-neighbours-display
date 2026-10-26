"""Regenerate only the quiz screenshots; leave unrelated page captures alone."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8110/')
out=Path(__file__).resolve().parents[1]/'docs/screenshots'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1280,'height':1024})
 page.goto(BASE+'activity.html?animal=brushtail');page.locator('[data-quiz-answer="1"]').click();page.locator('.quiz-feedback').wait_for();page.screenshot(path=str(out/'05-animal-quiz.png'),full_page=True)
 page.goto(BASE+'activity.html?animal=water-dragon');page.locator('[data-quiz-answer="0"].macro-focus').wait_for();page.screenshot(path=str(out/'06-multiple-choice.png'),full_page=True)
 for answer in [1,0,2]:page.locator(f'[data-quiz-answer="{answer}"]').click();page.locator('[data-quiz-action=next]').click()
 page.locator('.quiz-total').wait_for();page.screenshot(path=str(out/'17-quiz-complete.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.goto(BASE+'fencepost/index.html#activity/blue-tongue');page.locator('[data-quiz-answer="0"]').wait_for();page.screenshot(path=str(out/'18-quiz-mobile.png'),full_page=True)
 b.close()
print('Captured four quiz views')
