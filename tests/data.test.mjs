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
beforeEach(() => {
  api.resetDemo();
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
  await assert.rejects(api.moderate(payload), /sign-in/);
  api.demoLogin();
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
  assert.equal(q.records[0].moderatorId, "demo-moderator");
});
test("comments are moderated and only accepted on public stories", async () => {
  await api.addComment(sampleStories[0].id, "A quiet encounter.");
  assert.equal((await api.comments(sampleStories[0].id)).length, 0);
  api.demoLogin();
  let q = await api.queue();
  await api.moderateComment(q.comments[0].id, "approved");
  assert.equal((await api.comments(sampleStories[0].id)).length, 1);
  await api.reportComment(q.comments[0].id, "Please review");
  await api.moderateComment(q.comments[0].id, "removed");
  assert.equal((await api.comments(sampleStories[0].id)).length, 0);
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
  api.demoLogin();
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
