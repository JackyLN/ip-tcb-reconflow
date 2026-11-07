# UI palette update · 2026-11-06

User request: restyle the existing ReconFlow UI with Techcombank branding colors.
This is a palette interpretation for the synthetic interview prototype. ReconFlow keeps its own
wordmark, navigation, existing behavior and synthetic-demo identity.

References read:
- User-provided brand manual reference: https://www.slideshare.net/slideshow/tcb-brand-identify/15855119
  Corporate-colour section lists red, black, white and supporting yellow/gold. It is an older
  public manual and does not establish a current digital accessibility specification.
- User-provided secondary reference: https://rootagency.vn/kien-thuc-marketing/bo-nhan-dien-thuong-hieu-techcombank/
  Lists #ED1C24 with white and black. Exact brand red was also explicitly supplied by the user.
- Current official public brand context: https://techcombank.com/en/about-us

| Token/use | Hex | Interpretation |
| --- | --- | --- |
| Brand accents, chart, wordmark R, active indicator | #ED1C24 | User-supplied Techcombank red |
| Primary button | #CC1720 | UI contrast adaptation, not an official alternate brand specification |
| Button hover, links, focus | #B5121B | UI contrast adaptation |
| Main text / navigation | #202020 / #171717 | Black/charcoal foundation |
| Surface / workspace | #FFFFFF / #F5F5F5 | White and neutral sky-grey |
| Gold accent | #B18A49 | Chosen complementary UI gold; official hex NOT VERIFIED |
| Measured badge text/background | #76541D / #FBF4E7 | Readable gold treatment |

Brand red is a graphical accent and chart fill; its contrast against white is insufficient for
normal-size white text. Primary buttons therefore use a darker red. Status alerts retain their
semantic green/amber/danger treatments and explicit text, distinct from brand navigation accents.
Gold is restrained to measured-data/environment labeling. CSS owns palette values; Chart.js reads
the brand token instead of carrying a separate hardcoded accent. No data or financial logic changes.

MEASURED contrast ratios (WCAG relative luminance formula): primary white text 5.66:1,
primary hover/links 6.85:1 on white, muted text 5.59:1 on workspace grey, sidebar text 11.62:1,
active-navigation white text 14.90:1, measured gold badge 6.28:1. Brand-red chart fill is 4.38:1
against white (graphical contrast); normal button text uses the darker action red. Keyboard focus
uses dark red on light surfaces and bright brand red on charcoal navigation. These are selected
color-pair checks, not a complete WCAG conformance certification.

Verification results are recorded in docs/verification.md after the rebuilt application is checked.
This is not an independent accessibility audit or a claim of official brand compliance.
