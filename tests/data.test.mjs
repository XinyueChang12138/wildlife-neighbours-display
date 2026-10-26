import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import {
  sampleStories,
  opportunity,
  isVerifiedOpportunity,
} from "../shared/data.js";
class MemoryStorage {
  m = new Map();
  getItem(k) {
    return this.m.get(k) ?? null;
  }
  setItem(k, v) {
    this.m.set(k, String(v));
  }
  removeItem(k) {
    this.m.delete(k);
  }
}
globalThis.localStorage = new MemoryStorage();
globalThis.sessionStorage = new MemoryStorage();
globalThis.window = new EventTarget();
const api = await import("../shared/api.js");
beforeEach(async () => {
  await api.login("moderator@fencepost.demo", "moderator123");
  api.resetDemo();
  api.logout();
});
test("six sample species and conservative opportunity verification", () => {
  assert.equal(sampleStories.length, 6);
  assert.equal(isVerifiedOpportunity(opportunity), false);
  assert.equal(
    isVerifiedOpportunity({
      ...opportunity,
      status: "verified",
      organiserVerified: true,
    }),
    false,
  );
});
test("pending and private rescue fields never enter public projection", async () => {
  const receipt = await api.submit({
    possibleSpecies: "not-sure",
    publicArea: "General park area",
    approximateTime: "Around dusk",
    behaviour: "Resting",
    description: "Private test observation",
    privateRescueLocation: "SECRET ADDRESS",
    injuryConcern: true,
  });
  const feed = await api.stories();
  assert.ok(!JSON.stringify(feed).includes(receipt.id));
  assert.ok(!JSON.stringify(feed).includes("SECRET ADDRESS"));
  assert.ok(
    feed.every((s) => !("nickname" in s) && !("privateRescueLocation" in s)),
  );
});
test("moderation requires role, full checks and reason; rejection removes approved story", async () => {
  const r = await api.submit({
    possibleSpecies: "not-sure",
    publicArea: "General park area",
    approximateTime: "Around dusk",
    behaviour: "Resting",
    description: "An animal rested.",
    injuryConcern: false,
  });
  const payload = {
    id: r.id,
    action: "approve",
    reason: "Reviewed for privacy",
    publicText: "A possible animal rested in the park.",
    approvedPublicArea: "General park area",
    approvedSpecies: "not-sure",
    privacyChecks: {
      face: true,
      house: true,
      plate: true,
      location: true,
      welfare: true,
    },
    mediaApproved: false,
  };
  await assert.rejects(api.moderate(payload), /Moderator access/);
  await api.login("moderator@fencepost.demo", "moderator123");
  await assert.rejects(
    api.moderate({ ...payload, privacyChecks: {} }),
    /privacy/,
  );
  await api.moderate(payload);
  assert.ok((await api.stories()).some((s) => s.sourceObservationId === r.id));
  await api.moderate({
    ...payload,
    action: "reject",
    reason: "Contributor requested removal",
  });
  assert.ok(!(await api.stories()).some((s) => s.sourceObservationId === r.id));
  const q = await api.queue();
  assert.equal(q.records.length, 2);
  assert.equal(q.records[0].moderatorId, "wildlife-moderator");
});
test("comments publish immediately for signed-in users and retain author ownership", async () => {
  await assert.rejects(
    api.addComment(sampleStories[0].id, "A quiet encounter."),
    /Sign in/,
  );
  await api.login("resident@fencepost.demo", "resident123");
  const before = (await api.comments(sampleStories[0].id)).length;
  const c = await api.addComment(sampleStories[0].id, "A quiet encounter.");
  assert.equal(c.status, "visible");
  assert.equal((await api.comments(sampleStories[0].id)).length, before + 1);
  await api.editComment(c.id, "I watched quietly from the path.");
  assert.ok(
    (await api.comments(sampleStories[0].id)).some(
      (x) => x.body === "I watched quietly from the path.",
    ),
  );
  await assert.rejects(
    api.editComment("comment-neighbour-demo", "Changed by someone else."),
    /own/,
  );
  await api.deleteComment(c.id);
  assert.ok(
    !(await api.comments(sampleStories[0].id)).some((x) => x.id === c.id),
  );
  await assert.rejects(
    api.addComment("private-id", "Not public"),
    /unavailable/,
  );
});
test("broad areas and approximate time are constrained", () => {
  assert.throws(() =>
    api.validateObservation({
      possibleSpecies: "brushtail",
      publicArea: "123 Test Street",
      approximateTime: "8:31:02",
      behaviour: "Resting",
      description: "A test",
    }),
  );
});
test("publishing an outcome completes the activity and disables registration", async () => {
  await api.login("moderator@fencepost.demo", "moderator123");
  await api.saveOutcome({
    opportunityId: "habitat-demo",
    title: "Sample completed task",
    publicArea: "General park area",
    completedAt: "2026-01-01",
    actionsCompleted: "Sample planting preparation.",
    communityMessage: "No measured impact claim.",
    published: true,
    sample: true,
  });
  const current = (await api.opportunities()).find(
    (o) => o.id === "habitat-demo",
  );
  assert.equal(current.status, "completed");
  assert.equal(current.registrationOpen, false);
  assert.ok(
    (await api.outcomes()).some((o) => o.title === "Sample completed task"),
  );
});

test("new exhibition samples are labelled and additive demo migration preserves work", async () => {
  const old = api.initialState();
  old.catalogVersion = 2;
  old.outcomes = [];
  old.observations.push({
    id: "preserve-this",
    privateRescueLocation: "PRIVATE PRESERVED",
    status: "pending",
  });
  localStorage.setItem("wn-demo-v2", JSON.stringify(old));
  const feed = await api.stories();
  assert.equal(feed.length, 6);
  await api.login("moderator@fencepost.demo", "moderator123");
  assert.ok(
    (await api.queue()).observations.some((o) => o.id === "preserve-this"),
  );
  const updates = await api.outcomes();
  assert.equal(updates.length, 4);
  assert.ok(
    updates.every(
      (o) =>
        o.sample && o.whyItMatters && o.approvedImage && o.noWildlifeHandling,
    ),
  );
  assert.ok(!JSON.stringify(feed).includes("PRIVATE PRESERVED"));
});
test("revised mappings, multiple-choice quizzes and artwork cover the required journeys", async () => {
  const { config } = await import("../shared/config.js");
  const { quizzes } = await import("../shared/activities.js");
  const { artwork } = await import("../shared/ui.js");
  assert.deepEqual(config.keys, {
    back: "ArrowLeft",
    choose: "Enter",
    next: "ArrowRight",
  });
  assert.equal(Object.keys(quizzes).length, 6);
  assert.ok(Object.values(quizzes).every((questions) => questions.length === 3));
  assert.equal(Object.keys(artwork).length, 12);
});
