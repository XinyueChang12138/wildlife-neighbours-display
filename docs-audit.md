# Audit before integration

## Public display

Dependency-free HTML/CSS/JavaScript; no original backend, package manifest or test harness. On design-preview, routes were index, animals, species, help and community, with old quiz/sounds/stories compatibility redirects. Reusable components: cream/forest/rust theme, story photography, optional Web Speech, species detail pattern and privacy labels. Original media: possum photographs and three prototype WAV files; no new third-party sound recordings are introduced.

## Existing Fencepost

Source: https://github.com/LewisSwan24/fencepost, cloned and inspected after the user supplied access. Edits are on wildlife-neighbours-preview. Existing Next.js 15 / React 19 frontend is in web/; Python API and libSQL/Turso backend are at repository root. The generated root schema.sql and prompts are explicitly protected by its documentation and were not edited. Original system includes private/permissioned storyboards, nickname gate, QR/share codes, camera masking, forums and an assistant; it is not an anonymous approved-public-story service.

Existing routes include /, /b/[id] with capture/frame/mask/species/write, review, forum, close and share subroutes; /s/[token], /c/[code], /you, /sign-in, /credits and /study. They are retained. The old dashboard component moves to /legacy, and its tests import that preserved component. The default root and /park now show the public park workflow without NameGate. The legacy gate still protects the old UX where appropriate.

Shared park modules are synchronised into web/public/wildlife and mounted by a small Next client component; the original framework/build/deployment and components remain. Supabase is additive and isolated from Turso. No existing entries are automatically copied into public stories. The production Fencepost site was not redeployed or overwritten.

Cloud requests to deployed Fencepost, official wildlife websites and GitHub's API were blocked. Native Git proxy access worked for both source repositories. The initial Google Fonts build fetch failed; locally bundled matching fonts resolved it without changing families or disabling TLS verification.
