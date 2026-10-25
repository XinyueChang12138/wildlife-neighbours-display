import {
  species,
  sampleStories,
  observationSamples,
  opportunity,
  historicOpportunity,
  sampleOutcome,
} from "../shared/data.js";
import { createHash } from "node:crypto";
const q = (v) =>
  v === null || v === undefined
    ? "null"
    : typeof v === "boolean"
      ? String(v)
      : "'" + String(v).replaceAll("'", "''") + "'";
const uuid = (s) => {
  const h = createHash("sha256").update(s).digest("hex");
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-4${h.slice(13, 16)}-a${h.slice(17, 20)}-${h.slice(20, 32)}`;
};
console.log(
  "-- Fictional demonstration data only. Run after 001_schema.sql in a test Supabase project.\nbegin;",
);
console.log(
  `insert into public.opportunities(id,data) values(${q(opportunity.id)},${q(JSON.stringify(opportunity))}::jsonb) on conflict(id) do nothing;`,
);
console.log(
  `insert into public.opportunities(id,data) values(${q(historicOpportunity.id)},${q(JSON.stringify(historicOpportunity))}::jsonb) on conflict(id) do nothing;`,
);
for (const s of sampleStories)
  console.log(
    `insert into public.public_stories(id,species,public_area,approximate_time,behaviour,story_text,media_url,verified_fact,fact_source,reviewed_by,sample) values(${[uuid(s.id), s.species, s.publicArea, s.approximateTime, s.behaviour, s.storyText, null, s.verifiedFact, s.factSource, s.reviewedBy, true].map(q).join(",")}) on conflict(id) do nothing;`,
  );
for (const o of observationSamples)
  console.log(
    `insert into public.observations(id,nickname,possible_species,approximate_time,public_area,private_rescue_location,behaviour,description,injury_concern,status) values(${[uuid(o.id), o.nickname, o.possibleSpecies, o.approximateTime, o.publicArea, o.privateRescueLocation, o.behaviour, o.description, o.injuryConcern, o.status].map(q).join(",")}) on conflict(id) do nothing;`,
  );
const o = sampleOutcome;
console.log(
  `insert into public.outcomes(id,opportunity_id,title,public_area,completed_at,actions_completed,community_message,published,sample) values(${[uuid(o.id), o.opportunityId, o.title, o.publicArea, o.completedAt, o.actionsCompleted, o.communityMessage, true, true].map(q).join(",")}) on conflict(id) do nothing;`,
);
console.log("commit;");
