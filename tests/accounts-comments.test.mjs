import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
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
const auth = await import("../shared/auth.js");
const { checkComment } = await import("../shared/comment-safety.js");
const resident = () => api.login("resident@fencepost.demo", "resident123");
const moderator = () => api.login("moderator@fencepost.demo", "moderator123");
beforeEach(async () => {
  await moderator();
  api.resetDemo();
  api.logout();
});
test("both demo accounts authenticate, wrong passwords fail and only safe session metadata is stored", async () => {
  await assert.rejects(
    api.login("resident@fencepost.demo", "wrong"),
    /incorrect/,
  );
  await resident();
  assert.equal(auth.currentUser().displayName, "Taylor");
  const safe = JSON.parse(localStorage.getItem("wn-demo-session"));
  assert.deepEqual(Object.keys(safe).sort(), [
    "displayName",
    "email",
    "id",
    "role",
  ]);
  assert.ok(!JSON.stringify([...localStorage.m]).includes("resident123"));
  api.logout();
  assert.equal(auth.currentUser(), null);
  await moderator();
  assert.equal(auth.currentUser().role, "moderator");
});
test("resident cannot read queues, private rescue fields or other accounts’ registrations", async () => {
  await resident();
  await assert.rejects(api.queue(), /Moderator access/);
  const own = await api.myObservations();
  assert.equal(own.length, 2);
  assert.ok(own.some((o) => o.status === "pending"));
  assert.ok(own.some((o) => o.status === "approved"));
  assert.ok(!JSON.stringify(own).includes("privateRescueLocation"));
  assert.ok(!JSON.stringify(own).includes("DEMO PRIVATE LOCATION"));
  assert.equal(api.registrationList().length, 1);
  assert.equal((await api.savedStories()).length, 1);
  assert.equal(
    (await api.stories()).some(
      (s) => s.sourceObservationId === "taylor-pending-demo",
    ),
    false,
  );
});
test("reply and report do not add posts or place comments in a pre-approval queue", async () => {
  await resident();
  const c = await api.addComment(
    "story-brushtail",
    "I watched from a distance.",
    "comment-neighbour-demo",
  );
  assert.equal(c.parentCommentId, "comment-neighbour-demo");
  await api.reportComment(
    "comment-neighbour-demo",
    "Other concern",
    "Please check the discussion.",
  );
  await assert.rejects(api.reportComment(c.id, "Other concern"), /another/);
  await moderator();
  const q = await api.queue();
  assert.ok(
    q.reports.some(
      (r) => r.commentId === "comment-neighbour-demo" && r.status === "open",
    ),
  );
  assert.ok(q.comments.every((c) => ["visible", "removed"].includes(c.status)));
  assert.ok(!q.observations.some((o) => o.id === c.id));
});
test("only moderators remove/restore with an audit; a report alone leaves content visible", async () => {
  await resident();
  await api.reportComment("comment-neighbour-demo", "Other concern");
  assert.ok(
    (await api.comments("story-brushtail")).some(
      (c) => c.id === "comment-neighbour-demo",
    ),
  );
  await assert.rejects(
    api.moderateComment("comment-neighbour-demo", "remove", "Checked"),
    /Moderator access/,
  );
  await moderator();
  await assert.rejects(
    api.moderateComment("comment-neighbour-demo", "remove"),
    /reason/,
  );
  await api.moderateComment(
    "comment-neighbour-demo",
    "remove",
    "Review found inappropriate advice.",
  );
  assert.ok(
    !(await api.comments("story-brushtail")).some(
      (c) => c.id === "comment-neighbour-demo",
    ),
  );
  await api.moderateComment(
    "comment-neighbour-demo",
    "restore",
    "Restored after review.",
  );
  assert.ok(
    (await api.comments("story-brushtail")).some(
      (c) => c.id === "comment-neighbour-demo",
    ),
  );
  assert.equal((await api.queue()).commentHistory.length, 2);
});
test("comment validation blocks personal details, unsafe instructions and threats", () => {
  for (const value of [
    "",
    "Find it at 12 Acacia Street",
    "Email me at person@example.test",
    "Call 0412 345 678",
    "My plate is ABC123",
    "You should feed the possum",
    "I will kill you",
  ])
    assert.ok(checkComment(value).errors.length, value);
  assert.equal(
    checkComment("Watch quietly from a distance. Do not feed wildlife.").errors
      .length,
    0,
  );
  assert.ok(checkComment("That wording seems ridiculous.").warnings.length);
});
test("demo reset requires a moderator, restores records and keeps the authenticated moderator", async () => {
  await resident();
  await assert.rejects(
    Promise.resolve().then(() => api.resetDemo()),
    /Moderator access/,
  );
  await moderator();
  await api.moderateComment(
    "comment-neighbour-demo",
    "remove",
    "Sample review reason",
  );
  api.resetDemo();
  assert.equal(api.account().role, "moderator");
  assert.ok(
    (await api.comments("story-brushtail")).some(
      (c) => c.id === "comment-neighbour-demo",
    ),
  );
  api.logout();
  await resident();
  assert.equal(api.registrationList().length, 1);
});
test("dismissing a report records the reviewer and leaves the comment visible", async () => {
  await resident();
  await api.reportComment("comment-neighbour-demo", "Other concern");
  await moderator();
  const report = (await api.queue()).reports.find(
    (r) => r.commentId === "comment-neighbour-demo",
  );
  await api.dismissReport(report.id);
  const reviewed = (await api.queue()).reports.find((r) => r.id === report.id);
  assert.equal(reviewed.status, "dismissed");
  assert.equal(reviewed.reviewedBy, "wildlife-moderator");
  assert.ok(reviewed.reviewedAt);
  assert.ok(
    (await api.comments("story-brushtail")).some(
      (c) => c.id === "comment-neighbour-demo",
    ),
  );
});

test("local upgrade removes retired draft metadata without changing community records or the session", async () => {
  await resident();
  const saved = api.initialState();
  saved.drafts = {
    old: { original: "private draft", description: "retired suggestion" },
  };
  saved.observations[0].aiAssisted = true;
  saved.observations[1].ai_assisted = false;
  const expected = structuredClone(saved);
  delete expected.drafts;
  delete expected.observations[0].aiAssisted;
  delete expected.observations[1].ai_assisted;
  const session = localStorage.getItem("wn-demo-session");
  localStorage.setItem("wn-demo-v2", JSON.stringify(saved));
  await api.stories();
  assert.deepEqual(JSON.parse(localStorage.getItem("wn-demo-v2")), expected);
  assert.equal(localStorage.getItem("wn-demo-session"), session);
  await api.stories();
  assert.deepEqual(JSON.parse(localStorage.getItem("wn-demo-v2")), expected);
});
