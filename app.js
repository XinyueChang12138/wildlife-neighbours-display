const stories = [
  {
    image: "assets/ringtail-shorncliffe-night.jpg",
    alt: "Possums sheltering beneath a roof at night",
    author: "@mel_k",
    time: "2 Sep · 9:14pm",
    species: "Ringtail",
    title: "The one in the jacaranda",
    text: "Heard the gutter go and there she was, just sitting in the jacaranda looking at me while I filmed. Didn't move the whole time."
  },
  {
    image: "assets/brushtail-peeking.jpg",
    alt: "A brushtail possum peeking around a tree",
    author: "@dan_h",
    time: "5 Sep · 10:30pm",
    species: "Brushtail",
    title: "Straight up the old trunk",
    text: "Pretty sure this is a different one, much bigger. Came over the back fence and went straight up the trunk without stopping."
  },
  {
    image: "assets/ringtail-brisbane-park.jpg",
    alt: "A ringtail possum watching from a branch",
    author: "@aroha_t",
    time: "8 Sep · 8:05pm",
    species: "Ringtail",
    title: "Two visitors after dark",
    text: "Two of them this time. One stayed right up the top and kept making that clicking noise the whole time; I couldn't get both of them in frame."
  },
  {
    image: "assets/brushtail-trunk.jpg",
    alt: "A brushtail possum holding onto a tree trunk",
    author: "@sione_f",
    time: "10 Sep · 2:18am",
    species: "Brushtail",
    title: "The roof visitor returns",
    text: "2am, roof, again. Caught him coming down the drainpipe on the side of the house. Absolutely unbothered by me standing there in my dressing gown."
  },
  {
    image: "assets/ringtail-rain.jpg",
    alt: "A ringtail possum among green leaves",
    author: "@mel_k",
    time: "12 Sep · 9:47pm",
    species: "Ringtail",
    title: "Along the top of the fence",
    text: "Back again tonight. Went along the top of the fence, then sat in the jacaranda for ages pulling the flowers off the end of a branch."
  },
  {
    image: "assets/brushtail-palm.jpg",
    alt: "Possums resting together among palm branches",
    author: "@mel_k",
    time: "13 Sep · 10:06pm",
    species: "Ringtail",
    title: "A familiar route through the trees",
    text: "Came along the fence about eleven, then used the same connected branches neighbours had noticed earlier in the week."
  }
];

let storyIndex = 0;
const $ = (selector) => document.querySelector(selector);

function showToast(message) {
  const toast = $("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2100);
}

function showStory(index) {
  const story = stories[index];
  if (!$("#storyImage")) return;
  $("#storyImage").src = story.image;
  $("#storyImage").alt = story.alt;
  $("#storyAuthor").textContent = story.author;
  $("#storyTime").textContent = story.time;
  $("#storySpecies").textContent = story.species.toUpperCase();
  $("#storyTitle").textContent = story.title;
  $("#storyText").textContent = story.text;
  $("#storyNumber").textContent = `${String(index + 1).padStart(2, "0")} / ${String(stories.length).padStart(2, "0")}`;
}

$("#nextStory")?.addEventListener("click", () => {
  storyIndex = (storyIndex + 1) % stories.length;
  showStory(storyIndex);
});

$("#languageButton")?.addEventListener("click", () => {
  showToast("Language: English · 中文 · العربية");
});

document.querySelectorAll("[data-answer]").forEach((button) => {
  button.addEventListener("click", () => {
    const feedback = $("#quizFeedback");
    if (feedback) feedback.textContent = button.dataset.answer === "correct"
      ? "Correct! Possums use their hand-like feet to climb."
      : "Good try. Look for five long, hand-like toes.";
  });
});

document.querySelectorAll("[data-animal-fact]").forEach((button) => {
  button.addEventListener("click", () => showToast(button.dataset.animalFact));
});

document.querySelectorAll("[data-sound]").forEach((button) => {
  button.addEventListener("click", () => {
    if ("speechSynthesis" in window) {
      speechSynthesis.cancel();
      speechSynthesis.speak(new SpeechSynthesisUtterance(button.dataset.sound));
    }
    showToast("Playing wildlife sound clue");
  });
});

document.querySelectorAll(".sound-card audio").forEach((audio) => {
  audio.addEventListener("play", () => {
    document.querySelectorAll(".sound-card audio").forEach((other) => {
      if (other !== audio) other.pause();
    });
  });
});

document.querySelectorAll("[data-reveal]").forEach((button) => {
  button.addEventListener("click", () => {
    const answer = button.parentElement.querySelector(".sound-answer");
    if (!answer) return;
    answer.textContent = button.dataset.reveal;
    answer.classList.add("revealed");
    button.textContent = "Answer revealed";
  });
});
