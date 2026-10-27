import { test } from "node:test";
import assert from "node:assert/strict";
import {
  descriptionIssue,
  safetySignals,
  signsDescription,
  validateSigns,
  validateSelection,
  makeGuidance,
  offlineGuidance,
  safeFallback,
  validateGuidance,
  starterPrompts,
  helpSource,
  fallbackExplanation,
} from "../shared/wildlife-help-policy.js";
test("all six starter prompts provide varied conservative offline guidance with a fixed official source", () => {
  assert.equal(starterPrompts.length, 6);
  const results = starterPrompts.map(offlineGuidance);
  assert.ok(
    results.every(
      (r) =>
        r.category !== "Observe safely" &&
        r.source === helpSource &&
        r.explanation.includes(fallbackExplanation),
    ),
  );
  assert.ok(new Set(results.map((r) => r.explanation)).size >= 5);
});
test("high-risk signs override every model category and never become Observe safely", () => {
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
    assert.ok(safetySignals(text).length, text);
    for (const category of [
      "Observe safely",
      "Unable to determine",
      "Professional advice recommended",
    ]) {
      const result = makeGuidance(text, { category, reason: "uncertain" });
      assert.ok(
        [
          "Professional advice recommended",
          "Urgent assistance recommended",
        ].includes(result.category),
        text,
      );
    }
  }
});
test("empty, overlong and identifying text is blocked before a request", () => {
  for (const value of [
    "",
    "  ",
    "x".repeat(601),
    "My name is Taylor Smith",
    "name: Taylor",
    "Email me at test@example.test",
    "At 12 Acacia Street",
    "Call 0412 345 678",
    "rego ABC123",
    "-27.123456,153.123456",
  ])
    assert.ok(descriptionIssue(value), value);
  assert.equal(descriptionIssue("A possum is not moving."), null);
});
test("only generic sign codes cross the boundary and normalise consistently", () => {
  const raw = "Taylor saw a bleeding animal near a private address";
  const codes = safetySignals(raw);
  assert.deepEqual(codes, ["bleeding"]);
  assert.equal(signsDescription(codes), "bleeding");
  assert.ok(validateSigns(codes));
  assert.ok(!validateSigns(["Taylor"]));
  assert.ok(!validateSigns(["bleeding", "bleeding"]));
  assert.ok(!validateSigns("bleeding"));
});
test("model output is restricted to supported reasons and categories; invalid prose/contact fields fail closed", () => {
  assert.equal(
    validateSelection(
      { category: "Healthy", reason: "moving" },
      "moving normally",
    ),
    null,
  );
  assert.equal(
    validateSelection(
      { category: "Observe safely", reason: "moving", phone: "123" },
      "moving normally",
    ),
    null,
  );
  assert.equal(
    validateSelection(
      { category: "Professional advice recommended", reason: "bleeding" },
      "not sure",
    ),
    null,
  );
  assert.ok(
    validateSelection(
      { category: "Unable to determine", reason: "uncertain" },
      "not sure",
    ),
  );
  const good = offlineGuidance("trapped");
  assert.deepEqual(validateGuidance(good, "trapped"), good);
  assert.equal(
    validateGuidance({ ...good, now: "Pick it up" }, "trapped"),
    null,
  );
  assert.equal(
    safeFallback("not sure").category,
    "Professional advice recommended",
  );
  assert.equal(safeFallback("not sure").explanation, fallbackExplanation);
  assert.notEqual(
    makeGuidance("not sure", {
      category: "Observe safely",
      reason: "uncertain",
    }).category,
    "Observe safely",
  );
});
