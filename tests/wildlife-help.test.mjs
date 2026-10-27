import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  predefinedGuidance,
  safeFallback,
  descriptionIssue,
  starterPrompts,
  helpCategories,
  helpTransparency,
  helpSource,
  unknownExplanation,
} from "../shared/wildlife-help-policy.js";
test("six prompts select the intended predefined category, including the uncertain prompt", () => {
  assert.equal(starterPrompts.length, 6);
  assert.deepEqual(
    starterPrompts.map((text) => predefinedGuidance(text).category),
    [
      "Professional advice recommended",
      "Urgent assistance recommended",
      "Professional advice recommended",
      "Urgent assistance recommended",
      "Professional advice recommended",
      "Unable to determine",
    ],
  );
  assert.equal(
    predefinedGuidance(starterPrompts[5]).explanation,
    unknownExplanation,
  );
});
test("all four categories are reachable; unknown text receives the exact required explanation", () => {
  for (const text of [
    "not moving",
    "bleeding",
    "moving normally",
    "I noticed something",
  ])
    assert.ok(helpCategories.includes(predefinedGuidance(text).category));
  assert.equal(
    predefinedGuidance("The animal is moving normally").category,
    "Observe safely",
  );
  const unknown = predefinedGuidance("I noticed something");
  assert.equal(unknown.category, "Unable to determine");
  assert.equal(unknown.explanation, unknownExplanation);
  assert.equal(
    unknownExplanation,
    "There is not enough information to assess the situation. Observe from a safe distance, keep people and pets away, and contact a recognised wildlife organisation if you remain concerned.",
  );
});
test("risk signs take priority over otherwise normal movement", () => {
  for (const text of [
    "bleeding",
    "unable to move",
    "difficulty breathing",
    "broken wing",
    "its leg is broken",
    "trapped in a net",
    "tangled",
    "close to moving traffic",
    "not moving",
    "cannot stand",
    "moving normally but bloodied",
    "moving normally with a wound",
  ]) {
    const result = predefinedGuidance(text);
    assert.ok(
      [
        "Professional advice recommended",
        "Urgent assistance recommended",
      ].includes(result.category),
      text,
    );
  }
  assert.equal(
    predefinedGuidance("moving normally but limping").category,
    "Professional advice recommended",
  );
});
test("empty, overlong and identifying descriptions remain blocked", () => {
  for (const text of [
    "",
    "  ",
    "x".repeat(601),
    "My name is Taylor Smith",
    "name: Taylor",
    "test@example.test",
    "At 12 Acacia Street",
    "Call 0412 345 678",
    "rego ABC123",
    "-27.123456,153.123456",
  ])
    assert.ok(descriptionIssue(text), text);
  assert.equal(descriptionIssue("A possum is not moving."), null);
});
test("fixed responses preserve professional help, avoidance, uncertainty and authoritative source", () => {
  for (const text of [...starterPrompts, "moving normally"]) {
    const result = predefinedGuidance(text);
    assert.deepEqual(result, predefinedGuidance(text));
    assert.deepEqual(result.source, helpSource);
    assert.ok(result.avoid.includes("Do not touch"));
    assert.ok(result.professional);
    assert.ok(result.uncertainty.includes("unconfirmed"));
  }
  assert.equal(safeFallback().category, "Professional advice recommended");
  assert.equal(
    helpTransparency,
    "This general guidance cannot confirm whether an animal is injured. Contact a wildlife professional if you are concerned.",
  );
});
test("the feature uses no network, model language, keys or storage", async () => {
  const view = await readFile(
    new URL("../shared/wildlife-help.js", import.meta.url),
    "utf8",
  );
  const policy = await readFile(
    new URL("../shared/wildlife-help-policy.js", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(
    view + policy,
    /\bAI\b|\bmodel\b|\bfetch\s*\(|API_KEY|localStorage|sessionStorage|wildlifeHelpEndpoint|offlineGuidance|AbortController/,
  );
  assert.match(view, /Get guidance/);
  assert.match(view, /Checking the information…/);
});
