# Wildlife Neighbours Community Display

Static public touchscreen prototype centred on neighbourhood wildlife observations.

## Run

From this folder run `python3 -m http.server 8000 --bind 0.0.0.0`, then open the site in your local browser. No dependencies or build are needed. VS Code Live Server also works.

## Pages

- `index.html`: rotating sample observation, sourced wildlife fact, optional spoken story, and two secondary paths.
- `help.html`: immediately readable safety guidance and an attributed Queensland rescue contact.
- `animals.html`: species selection.
- `species.html?animal=brushtail` or `species.html?animal=ringtail`: species information and one optional family discovery.
- `community.html`: Fencepost sharing and a single sample community action.
- Legacy stories, quiz and sounds URLs redirect to the new flow.

Stories rotate every 20 seconds and can be paused. Reduced-motion preferences pause automatic rotation. Secondary pages return home after two minutes of inactivity. Browser speech support varies; all information is available as text.

See `DESIGN.md` for the palette rationale, research basis and deployment requirements. Posts and volunteer details are sample content; there is no live post integration or verified registration destination.

## Validation

Run `node --check app.js`. Functional browser checks should cover story next/pause/rotation, species question feedback and fact reveal, idle return, legacy redirects, image loading, mobile overflow and JavaScript errors. Audio output and physical accessibility require testing on the installation hardware.
