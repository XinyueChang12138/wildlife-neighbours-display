// Run from the display repo: node scripts/sync-fencepost.mjs /workspace/fencepost
import { cp, mkdir } from "node:fs/promises";
import path from "node:path";
const destination = process.argv[2];
if (!destination) throw Error("Pass the existing Fencepost checkout path.");
const target = path.resolve(destination, "web/public/wildlife");
await mkdir(target, { recursive: true });
for (const item of [
  "shared",
  "assets",
  "vendor",
  "fencepost",
  "styles.css",
  "app.js",
  "index.html",
  "animals.html",
  "species.html",
  "help.html",
  "community.html",
  "activity.html",
  "story.html",
  "updates.html",
  "update.html",
])
  await cp(item, path.join(target, item), { recursive: true });
console.log("Shared park experience synced to " + target);
