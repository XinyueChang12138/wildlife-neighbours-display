# Revised prototype screenshots

Actual browser captures of the revised implementation. Illustration and community content is explicitly fictional. These are not evidence of a production deployment or hands-on hardware testing.

1. [Revised public-display home](01-public-display-home.png)
2. [Highlighted three-button navigation](02-highlighted-navigation.png)
3. [Selectable Return to previous screen](03-return-option.png)
4. [Local Wildlife Story without a rotation pause/resume control](04-local-story-no-pause.png)
5. [Meet the Animal quiz, answer and explanation](05-animal-quiz.png)
6. [Multiple-choice answer cards and three-button focus](06-multiple-choice.png)
7. [Revised Fencepost home hierarchy](07-fencepost-home.png)
8. [Sample volunteer opportunity](08-volunteer-opportunity.png)
9. [Prototype registration](09-prototype-registration.png)
10. [Sample Community Update](10-community-update.png)

Regenerate with `python3 scripts/capture-revision.py` while the static prototype runs at port 8050, or set `WN_TEST_BASE` to its development HTTP address. The keyboard tests additionally exercise 1024×768 iPad-sized and 390-pixel phone viewports. The actual keyboard, knob, iPad/cardboard reach and audio environment still need physical testing.

## Accounts, direct comments and writing help

11. [Demonstration login and quick-fill accounts](11-demo-login.png)
12. [Taylor’s resident activity/profile](12-resident-profile.png)
13. [Moderator posts awaiting approval](13-moderator-posts.png)
14. [Reported comments, separate from post review](14-reported-comments.png)
15. [Original and editable writing suggestion](15-writing-help.png)
16. [Immediately visible comments and resident controls](16-direct-comments.png)

These accounts and records are fictional exhibition data. The intentionally public credentials in the login screenshot are not production secrets. `scripts/capture-accounts.py` regenerates these six views.

## Multiple-choice quiz correction

Screenshots 5 and 6 now show the replacement quiz, rather than the removed games.

17. [Three-question completion and review controls](17-quiz-complete.png)
18. [Responsive quiz on Fencepost](18-quiz-mobile.png)

Regenerate only these quiz views with `scripts/capture-quiz.py`.
