# Justice Szotkowski — Owner Context

## Who I Am
- Self-employed growth automation and paid media operator based in Eau Claire, WI
- College student at UW Eau Claire, part-time at Phoenix Taproom
- Run two businesses: Forward Commerce (performance marketing) and Forward Automation AI (AI receptionist/workflow automation)
- ~6 years experience in paid social, CRM automation, direct response copywriting
- Girlfriend based in Florence, Italy
- **Timezone:** Central Time (America/Chicago)

## Active Projects

### Serena Facebook Ads Campaign
- Magnesium glycinate sleep supplement targeting perimenopausal women
- Using Anthony Camacho desire-testing framework (ED1, ED3, ED8)
- D3-Hook1-Image1 is early standout performer ($0.59 CPC, 37.5% link-to-click ratio)
- Landing page needs policy compliance fixes before scaling (anxiety claims, unsubstantiated social proof, causation language)
- Win state: $0.15-0.75 CPLC with good conversion rate before scaling budget

### HCC GoHighLevel CRM Build
- Building CRM for High Cliff Consulting (Wisconsin septic/land consulting) run by Emery Palmer
- Managed through Jack Fentress at Jolly Mammoth Co
- Core challenge: delivering completed report PDFs to clients after invoice payment
- GHL workaround: dynamic public form upload link in Emery's notification email
- Open items: Field Work Complete notification, Report Ready/Released emails, invoice info update, Google Review link, SMS consent, POWTS Design and Survey workflows, Stripe live mode
- Open question for Emery: Is the SBD-8330 Soil Evaluation Report client-facing or internal only?

### Local Web Design Outreach
- Video-based outreach: build polished HTML mock sites, record Loom walkthroughs, send as personalized pitches
- Sites built: Daily Grind Cafe (Stillwater MN) — **not interested**, The Silver Dollar (Menomonie) — pending approach, The Yard (Menomonie), EC Billiards (Eau Claire) — **not interested**, Abbey Pub (Menomonie)
- Abbey Pub deployed to GitHub Pages (justicewastaken/abbey-pub) with hash routing, plus Manus preview: https://abbeypub-eu4kcd7b.manus.space/
- Forward Media landing page at justicewastaken.github.io/forward-media
- Best targets for fast closes: tattoo artists, barbers, mobile service businesses (solo operators, no gatekeepers)
- **Plan:** Get referral from Abbey Pub owner on Thursday for The Silver Dollar; continue refining targeting

### Website Sales Automation Pipeline
- Daily automated outreach to local businesses (salons initially, expanding to tattoo/barbers/mobile)
- Full pipeline: Google Maps scrape → Playwright enrichment (email/booking platform) → email generation → batch send
- Scripts: `full_daily_pipeline.sh`, `daily_website_batch.py`, `enrich_salons_v2.js`
- **Critical Issue:** Deliverability — emails bouncing with "limit reached" or "address not found." Likely sending to invalid/risky addresses.
- **Next:** Add email validation during enrichment; test smaller batches; investigate warm-up/rate limiting.

### NTS Protection Services AI Receptionist
- Built VAPI + Make.com AI receptionist ("Sarah") for father Troy's security company
- Routes: employment → mnjobs@ntsprotection.com, training → anthony@, security leads → mel@, general → troy@, emergency → Chris
- Uses GPT-4o for voice function calling
- $1,000 setup + $500/month engagement

### Tidy Turf (Dog Waste Removal)
- **Scrapped** — side project; poor metrics, not viable

## Key Frameworks
- Anthony Camacho desire-testing and gradualization for Facebook ads
- Eugene Schwartz awareness stages (unaware → most aware)
- Desire-based creative testing: 5 desires framework (Effortless Competence, Maintenance-Free Freedom, Authenticated Adulting, Strategic Investment, Emotional Anchoring)

## Tools & Stack
- GoHighLevel, Make.com, VAPI, n8n, Notion (primary workspace), Google Drive
- GitHub (justicewastaken), Shopify, Facebook Ads Manager
- Gmail accounts: justiceforanything@gmail.com, justice@forwardaffiliate.com

## Integrations & Credentials
### Google Workspace (Gmail/Calendar)
- Auth method: OAuth service account (client_secret.json at `.config/gog/`)
- Primary account: justiceforanything@gmail.com
- Issue: keyring locked; set `GOG_KEYRING_PASSWORD` env var for non-interactive access
- Reference: `docs/gog_setup.md`
- Morning brief script reads calendars and sends Telegram summary at 7 AM CT
