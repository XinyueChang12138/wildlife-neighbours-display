"""Confirm-before-dial on display and companion; never place a real call."""
import os
from playwright.sync_api import sync_playwright
BASE=os.environ.get('WN_TEST_BASE','http://127.0.0.1:8200/')
def highlight(page,selector):
 for _ in range(70):
  focus=page.locator('.macro-focus')
  if focus.count() and focus.evaluate('(el,s)=>el.matches(s)',selector):return
  page.keyboard.press('ArrowRight')
 raise AssertionError('Not reachable: '+selector)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1024,'height':768});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 # Observe normal browser activation, then stop confirmed links in this test only.
 # This tests the tel handoff without opening an external app or placing a call.
 page.add_init_script("""window.telEvents=[];document.addEventListener('click',event=>{const link=event.target.closest('a[href^="tel:"]');if(!link)return;window.telEvents.push({href:link.getAttribute('href'),confirmed:link.hasAttribute('data-contact-confirm'),prevented:event.defaultPrevented});if(link.hasAttribute('data-contact-confirm'))event.preventDefault();});""")
 page.goto(BASE+'help.html');page.locator('[data-selected]').wait_for();assert page.locator('.assistance-contacts .contact-card').count()==2
 assert 'Do not call 000 only because an animal appears injured.' in page.locator('.contact-emergency').inner_text()
 assert 'Triple Zero' not in page.locator('.contact-wildlife').inner_text()
 for ident,href,title,body in [('rspca-qld','tel:1300264625','Call RSPCA Queensland?','Use this contact for specialist advice about injured, sick, orphaned or trapped wildlife.'),('triple-zero','tel:000','Call Triple Zero?','Only continue if someone is seriously injured, in immediate danger or urgent police, fire or ambulance assistance is required.')]:
  selector=f'[data-contact-id="{ident}"]';link=page.locator(selector);assert link.get_attribute('href')==href;r=link.bounding_box();assert r['height']>=44 and r['width']>=44
  before=len(page.evaluate('telEvents'));highlight(page,selector);url=page.url;page.keyboard.press('ArrowLeft');assert page.url==url;highlight(page,selector);page.keyboard.press('Enter');dialog=page.locator('.contact-dialog[open]');dialog.wait_for();assert dialog.locator('h2').inner_text()==title;assert dialog.locator('p').inner_text()==body;assert dialog.locator('[data-contact-cancel].macro-focus').count()==1
  event=page.evaluate('telEvents.at(-1)');assert event=={'href':href,'confirmed':False,'prevented':True};assert len(page.evaluate('telEvents'))==before+1
  page.keyboard.press('ArrowRight');assert dialog.locator('[data-contact-confirm].macro-focus').count()==1
  page.keyboard.press('ArrowRight');assert dialog.locator('[data-contact-cancel].macro-focus').count()==1
  page.keyboard.press('ArrowLeft');assert dialog.locator('[data-contact-confirm].macro-focus').count()==1
  assert dialog.locator('[data-contact-confirm]').get_attribute('href')==href;page.keyboard.press('Enter');assert page.evaluate('telEvents.at(-1)')=={'href':href,'confirmed':True,'prevented':False}
  dialog.get_by_role('button',name='Cancel',exact=True).click();assert not page.locator('.contact-dialog').count();assert link.evaluate('el=>el===document.activeElement')
  link.click();page.locator('.contact-dialog[open]').wait_for();page.keyboard.press('Escape');assert not page.locator('.contact-dialog').count();assert link.evaluate('el=>el===document.activeElement')
 print('Display: central numbers, clear purposes, phone targets, confirmation before tel activation, physical wrap/Choose, touch Cancel/Escape and restored focus passed',flush=True)
 page.set_viewport_size({'width':390,'height':844});page.goto(BASE+'fencepost/index.html#help');page.locator('[data-contact-id=rspca-qld]').wait_for();assert page.locator('.assistance-contacts .contact-card').count()==2
 for ident,href in [('rspca-qld','tel:1300264625'),('triple-zero','tel:000')]:
  page.locator('[data-contact-id='+ident+']').click();dialog=page.locator('.contact-dialog[open]');dialog.wait_for();assert dialog.locator('[data-contact-cancel]').evaluate('el=>el===document.activeElement');page.keyboard.press('ArrowLeft');assert dialog.locator('[data-contact-confirm]').evaluate('el=>el===document.activeElement');page.keyboard.press('Enter');assert page.evaluate('telEvents.at(-1)')=={'href':href,'confirmed':True,'prevented':False};dialog.get_by_role('button',name='Cancel',exact=True).click()
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors
 print('Companion: shared contacts, touch confirmation, keyboard controls, safe tel handoff, mobile layout and no console/page errors passed',flush=True);b.close()
