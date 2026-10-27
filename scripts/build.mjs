import { readFile, access, readdir, rm, mkdir, cp } from "node:fs/promises";
import { species } from "../shared/data.js";
import { spawnSync } from "node:child_process";
for (const file of [
  "app.js",
  "shared/api.js",
  "shared/mobile.js",
  "shared/controls.js",
  "shared/contacts.js",
  "shared/wildlife-help.js",
  "shared/wildlife-help-policy.js",
  "shared/ui.js",
  "shared/config.js",
  "shared/data.js",
  "shared/activities.js",
  "shared/quiz-data.js",
  "shared/quiz-state.js",
  "shared/presentation.js",
  "shared/auth.js",
  "shared/storage.js",
  "shared/demo-accounts.js",
  "shared/comment-safety.js",
]) {
  const r = spawnSync(process.execPath, ["--check", file], {
    encoding: "utf8",
  });
  if (r.status !== 0) throw Error(r.stderr);
}
for (const file of [
  "index.html",
  "animals.html",
  "species.html",
  "help.html",
  "community.html",
  "fencepost/index.html",
  "styles.css",
  "shared/mobile.css",
  "shared/contacts.css",
  "shared/quiz.css",
  "shared/wildlife-help.css",
  "vendor/qrcode.js",
  ...species.map((s) => s.image).filter((x) => x.startsWith("assets/")),
  "activity.html",
  "story.html",
  "updates.html",
  "update.html",
  "assets/neighbours-illustrations.webp",
])
  await access(file);
for (const file of [
  "index.html",
  "animals.html",
  "species.html",
  "help.html",
  "community.html",
]) {
  const s = await readFile(file, "utf8");
  if (!s.includes('data-control="choose"') || !s.includes('type="module"'))
    throw Error(file + " missing public controls or script");
}
// Publish only website files, excluding repository metadata, tests and secrets.
await rm("public", { recursive: true, force: true });
await mkdir("public");
for (const entry of await readdir(".", { withFileTypes: true })) {
  if (entry.isFile() && /\.(html|css|js)$/.test(entry.name)) {
    await cp(entry.name, `public/${entry.name}`);
  }
}
for (const directory of ["assets", "shared", "vendor", "fencepost"]) {
  await cp(directory, `public/${directory}`, { recursive: true });
}
console.log("Static build validation passed. Website generated in public/.");
