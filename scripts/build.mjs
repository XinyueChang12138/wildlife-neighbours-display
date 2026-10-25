import { readFile, access } from "node:fs/promises";
import { species } from "../shared/data.js";
import { spawnSync } from "node:child_process";
for (const file of [
  "app.js",
  "shared/api.js",
  "shared/mobile.js",
  "shared/controls.js",
  "shared/ui.js",
  "shared/config.js",
  "shared/data.js",
  "shared/activities.js",
  "shared/presentation.js",
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
console.log(
  "Static build validation passed. Deploy this repository as-is; no generated build directory is required.",
);
