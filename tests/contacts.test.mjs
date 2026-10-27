import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { config } from "../shared/config.js";
import {
  contactOptions,
  contactHref,
  contactLabel,
  confirmLabel,
  additionalReviewedContacts,
} from "../shared/contacts.js";
test("wildlife assistance and human emergencies are configured separately with sources and review metadata", () => {
  const [wildlife, emergency] = config.assistanceContacts;
  assert.equal(wildlife.kind, "wildlife");
  assert.equal(contactHref(wildlife), "tel:1300264625");
  assert.equal(contactLabel(wildlife), "Call 1300 ANIMAL");
  assert.equal(emergency.kind, "emergency");
  assert.equal(contactHref(emergency), "tel:000");
  assert.equal(contactLabel(emergency), "Call Triple Zero (000)");
  assert.equal(confirmLabel(emergency), "Call 000");
  assert.match(
    emergency.warning,
    /Do not call 000 only because an animal appears injured/,
  );
  for (const contact of config.assistanceContacts) {
    assert.ok(
      contact.sourceUrls.every((url) => new URL(url).protocol === "https:"),
    );
    assert.match(contact.reviewedAt, /^\d{4}-\d{2}-\d{2}$/);
    assert.ok(contact.reviewBasis);
  }
});
test("cards separate the two purposes, have large phone-labelled links, and use configuration rather than embedded numbers", async () => {
  const html = contactOptions();
  assert.match(html, /contact-wildlife/);
  assert.match(html, /contact-emergency/);
  assert.match(html, /aria-haspopup="dialog"/);
  assert.match(html, /contact-phone-icon/);
  assert.match(html, /Injured or trapped wildlife/);
  assert.match(html, /Is a person in immediate danger/);
  const customized = structuredClone(config.assistanceContacts);
  customized[0].number = "123456789";
  customized[0].mnemonic = "Test wildlife line";
  assert.match(contactOptions(customized), /tel:123456789/);
  assert.match(contactOptions(customized), /Call Test wildlife line/);
  const component = await readFile(
    new URL("../shared/contacts.js", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(component, /1300264625|tel:000|1300 ANIMAL/);
});
test("duplicate standard numbers cannot reappear in the ordinary reviewed-contact list", () => {
  const base = {
    verified: true,
    sourceUrl: "https://example.test",
    reviewedAt: "2026-10-27",
  };
  assert.equal(
    additionalReviewedContacts([
      { ...base, phone: "000" },
      { ...base, phone: "1300 264 625" },
      { ...base, phone: "0123456789" },
      { ...base, phone: "other", verified: false },
    ]).length,
    1,
  );
});
