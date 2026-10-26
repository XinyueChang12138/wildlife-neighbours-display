import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { species } from "../shared/data.js";
import { quizzes, quizSources } from "../shared/quiz-data.js";
import {
  createQuizState,
  transition,
  correctCount,
} from "../shared/quiz-state.js";

test("six animals each have three unique questions, three answers and one correct answer with a recorded source", () => {
  assert.deepEqual(
    Object.keys(quizzes),
    species.map((s) => s.id),
  );
  const prompts = new Set();
  for (const [id, questions] of Object.entries(quizzes)) {
    assert.equal(questions.length, 3);
    for (const q of questions) {
      assert.ok(!prompts.has(q.prompt));
      prompts.add(q.prompt);
      assert.equal(q.answers.length, 3);
      assert.equal(new Set(q.answers).size, 3);
      assert.ok(Number.isInteger(q.correct) && q.correct >= 0 && q.correct < 3);
      assert.ok(q.explanation.length > 40);
      assert.deepEqual(q.source, quizSources[id]);
      assert.equal(new URL(q.source.url).hostname, "australian.museum");
    }
  }
  assert.equal(prompts.size, 18);
});

test("retry clears the answer and feedback without advancing or accumulating a score", () => {
  let s = createQuizState("brushtail");
  s = transition(s, "answer", 1);
  assert.equal(correctCount(s), 1);
  assert.equal(s.selected, 1);
  assert.equal(s.feedback, true);
  assert.equal(transition(s, "answer", 0), s);
  s = transition(s, "retry");
  assert.equal(s.question, 0);
  assert.equal(s.selected, null);
  assert.equal(s.feedback, false);
  assert.equal(s.highlighted, 0);
  assert.equal(correctCount(s), 0);
  s = transition(s, "answer", 0);
  assert.equal(correctCount(s), 0);
});

test("next requires feedback, completion counts final choices, review preserves answers and restart clears everything", () => {
  let s = createQuizState("magpie");
  assert.equal(transition(s, "next"), s);
  for (let i = 0; i < 3; i++) {
    s = transition(s, "answer", quizzes.magpie[i].correct);
    s = transition(s, "next");
  }
  assert.equal(s.completed, true);
  assert.equal(correctCount(s), 3);
  s = transition(s, "review");
  assert.equal(s.reviewing, true);
  assert.equal(correctCount(s), 3);
  s = transition(s, "summary");
  assert.equal(s.reviewing, false);
  s = transition(s, "restart");
  assert.deepEqual(s, createQuizState("magpie"));
});

test("changing animal resets the entire quiz; invalid selections cannot enter state", () => {
  const start = createQuizState("kangaroo");
  assert.equal(transition(start, "answer", 3), start);
  assert.equal(transition(start, "answer", NaN), start);
  const old = transition(start, "answer", 2);
  assert.deepEqual(
    transition(old, "animal", "blue-tongue"),
    createQuizState("blue-tongue"),
  );
  assert.equal(createQuizState("unknown").speciesId, "brushtail");
});

test("quiz implementation has no dragging, matching, sound or automatic feedback timer", async () => {
  const implementation = await readFile(
    new URL("../shared/activities.js", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(
    implementation,
    /draggable|dragstart|dragover|drop-zone|setTimeout|<audio|data-game/,
  );
  assert.match(implementation, /setAttribute\("role", "status"\)/);
  assert.match(implementation, /Return to Meet the Animal/);
});
