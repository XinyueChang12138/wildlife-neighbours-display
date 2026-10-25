const stories = [
  { image: 'assets/brushtail-peeking.jpg', alt: 'A brushtail possum peeking around a tree', title: 'A quiet visitor after dark.', species: 'Possible brushtail possum', text: 'A resident noticed a possible brushtail possum resting beside a tree near the local park around 8:30 pm.', area: 'General park area only', time: 'Around 8:30 pm', fact: 'Brushtail possums are mostly active at night.', source: 'https://australian.museum/learn/animals/mammals/common-brushtail-possum/' },
  { image: 'assets/ringtail-brisbane-park.jpg', alt: 'A ringtail possum watching from a tree', title: 'An evening in the branches.', species: 'Possible common ringtail possum', text: 'A neighbour noticed a possible ringtail possum sitting among branches near a local green space around 8 pm.', area: 'Local green space only', time: 'Around 8 pm', fact: 'Ringtail possums use their prehensile tails to grip branches.', source: 'https://australian.museum/learn/animals/mammals/common-ringtail-possum/' },
  { image: 'assets/brushtail-trunk.jpg', alt: 'A brushtail possum holding onto a tree trunk', title: 'A night-time climber.', species: 'Possible brushtail possum', text: 'A resident noticed a possible brushtail possum climbing a tree in the neighbourhood late at night.', area: 'Neighbourhood trees only', time: 'Late at night', fact: 'Brushtail possums use sharp claws to climb trees.', source: 'https://australian.museum/learn/animals/mammals/common-brushtail-possum/' }
];
const $ = (selector) => document.querySelector(selector);
let storyIndex = 0;
let paused = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let rotationTimer;
function showStory(index) {
  if (!$('#storyImage')) return;
  window.speechSynthesis?.cancel();
  if ($('#audioStatus')) $('#audioStatus').textContent = '';
  const s = stories[index];
  $('#storyImage').src = s.image;
  $('#storyImage').alt = s.alt;
  for (const [id, field] of Object.entries({storyTitle:'title',storySpecies:'species',storyText:'text',storyArea:'area',storyTime:'time',storyFact:'fact'})) $(`#${id}`).textContent = s[field];
  $('#factSource').href = s.source;
  $('#storyNumber').textContent = `${String(index + 1).padStart(2,'0')} / 03`;
}
function scheduleRotation() {
  clearInterval(rotationTimer);
  if (!paused && $('#storyImage')) rotationTimer = setInterval(() => {
    if (!document.hidden) { storyIndex = (storyIndex + 1) % stories.length; showStory(storyIndex); }
  }, 20000);
}
function updatePause() {
  if (!$('#pauseStory')) return;
  $('#pauseStory').textContent = paused ? 'Resume rotation' : 'Pause rotation';
  $('#pauseStory').setAttribute('aria-pressed', String(paused));
  scheduleRotation();
}
$('#nextStory')?.addEventListener('click', () => { storyIndex = (storyIndex + 1) % stories.length; showStory(storyIndex); scheduleRotation(); });
$('#pauseStory')?.addEventListener('click', () => { paused = !paused; updatePause(); });
updatePause();

if ($('#animalName')) {
  const ringtail = new URLSearchParams(location.search).get('animal') === 'ringtail';
  if (ringtail) {
    $('#animalName').textContent = 'Common ringtail possum';
    $('#animalImage').src = 'assets/ringtail-brisbane-park.jpg';
    $('#animalImage').alt = 'Ringtail possum in a tree';
    $('#animalIntro').textContent = 'Look for a curled tail. Watch quietly from a distance.';
    $('#speciesSource').href = 'https://australian.museum/learn/animals/mammals/common-ringtail-possum/';
    $('#familyPrompt').textContent = 'What makes a ringtail’s tail so useful?';
    $('.answers').innerHTML = '<button id="revealFact">Reveal a behaviour fact</button>';
    $('#revealFact').addEventListener('click', () => { $('#familyFeedback').textContent = 'Its prehensile tail grips branches as it climbs.'; });
  } else {
    document.querySelectorAll('[data-choice]').forEach(button => button.addEventListener('click', () => {
      $('#familyFeedback').textContent = button.dataset.choice === 'safe' ? 'Yes. Stay back, keep pets away and let it move on.' : 'Try giving it space. Human food can harm wildlife.';
    }));
  }
}
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.bottom-nav a').forEach(link => {
  if (link.getAttribute('href') === currentPage || (currentPage === 'species.html' && link.getAttribute('href') === 'animals.html')) link.setAttribute('aria-current','page');
});
// Touch, keyboard and pointer activity restart the two-minute kiosk timeout.
let idleTimer;
function resetIdle() {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => {
    if (currentPage !== 'index.html') location.replace('index.html');
    else { storyIndex = 0; showStory(0); paused = window.matchMedia('(prefers-reduced-motion: reduce)').matches; updatePause(); }
  }, 120000);
}
['pointerdown','pointermove','keydown','touchstart','scroll'].forEach(event => window.addEventListener(event, resetIdle, {passive:true}));
resetIdle();

$('#listenStory')?.addEventListener('click', () => {
  if (!('speechSynthesis' in window)) {
    $('#audioStatus').textContent = 'Audio is unavailable in this browser. Read the story above.';
    return;
  }
  window.speechSynthesis.cancel();
  paused = true;
  updatePause();
  const story = stories[storyIndex];
  const utterance = new SpeechSynthesisUtterance(`${story.text} Wildlife fact: ${story.fact} Give wildlife space. Never feed, touch or follow animals.`);
  utterance.onerror = () => { $('#audioStatus').textContent = 'Audio could not play. Read the story above.'; };
  window.speechSynthesis.speak(utterance);
});
