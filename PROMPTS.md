# Work.Style — idea, business model and phase-wise build prompt

## 1. The idea (chosen position)

**Work.Style = "Find your work style, then build your workdays around it."**
A free, interactive work-style assessment (8 archetypes) as the traffic engine, surrounded by free work tools, practical guides and a B2B team-report funnel.

### Why this beats the alternatives

| Option for Work.Style | Traffic ceiling | Monetization depth | Moat | Verdict |
|---|---|---|---|---|
| Fashion "work style / office outfits" blog | High | Low-mid (fashion CPCs, affiliate only) | Weak — Pinterest owns this | Reject |
| Remote job board | Mid | High but needs two-sided marketplace | Weak vs WeWorkRemotely/RemoteOK | Phase 4 add-on only |
| Generic productivity blog | Mid | Mid | None | Reject |
| **Work-style assessment + tools + team reports** | **High (quizzes are shared and linked)** | **High: AdSense on HR/SaaS/ergonomic CPCs + B2B leads + sponsors** | **Owned archetypes, owned scoring, linkable tools** | **Chosen** |

Precedent from the 44 reviewed sites: 16Personalities, Truity and Crystal all prove a free assessment → archetype pages → team/B2B upsell path. Clockify, Levels.fyi and Ergotron prove calculators are durable SEO magnets.

### Revenue model (assumptions, not promises)
Model at 100k monthly pageviews (realistic 12–18 months in with consistent publishing):

| Stream | Assumption | Monthly |
|---|---|---|
| AdSense | RPM $8–20 (workplace/HR/SaaS niche, US/CA/UK-heavy traffic) | $800–2,000 |
| Team reports | 0.05% of visitors request; 25% close; $400 avg | $1,000–2,000 |
| Sponsorships | 1 newsletter/contest sponsor at $300–1,000 | $300–1,000 |
| Donations/pledges | Small; mainly goodwill | $50–200 |
| **Total** | | **$2,150–5,200** |

The B2B team-report line is the lever: one conversion is worth months of AdSense from the same visitor. Treat AdSense as the floor and the team funnel as the business.

### Biggest risk
Low-content / thin pages get AdSense rejections. Mitigation built in: 10 long-form original guides, 8 deep archetype pages, 6 working tools, full legal pages, no empty placeholders, clear navigation.

---

## 2. Phase-wise build prompt (reusable)

### Phase 1 — Foundation and compliance
> Build a static, responsive website for the domain **Work.Style** hosted on GitHub Pages (free plan, repo `webworksa1/work-style`). Plain HTML/CSS/JS, no build step required on the server. Include on every page:
> - Google AdSense code in `<head>`: `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>` and `ads.txt` with `google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0`.
> - A top strip: "Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership" linking to https://web.works/contact.
> - Privacy & cookie policy (with Google advertising-cookie wording and opt-out links), terms, disclaimer, about/methodology, contact, trademark & copyright disclosure stating no affiliation with any "Workstyle"-named company or product.
> - All forms send to one relay address that is never visible in markup or source text (encoded and assembled at runtime).
> - Cookie notice with "Accept all" and "Essential only" (non-personalized ads), sitemap.xml, robots.txt, canonical tags, Open Graph, JSON-LD, 404 page.

### Phase 2 — The traffic engine
> Build a 20-statement Likert Work Style Assessment scoring four dimensions (deep↔sprint, independent↔collaborative, planned↔flexible, home↔office). Map the first three to 8 archetypes (Cartographer, Tinkerer, Mentor, Collaborator, Sprinter, Scout, Coordinator, Catalyst) and the fourth to a remote/hybrid/office recommendation. Show results instantly with axis bars, strengths, watch-outs, ideal setup, methods and a shareable link. Create a full profile page per archetype. Add an interactive "quick read" dial on the homepage hero.

### Phase 3 — SEO tools and content
> Build six client-side tools: meeting cost calculator, commute savings calculator, focus timer (Pomodoro/50-10/90-20), desk & monitor height calculator, hybrid week planner, freelance hourly rate calculator. Write 10 original long-form guides: remote work, productivity methods, hybrid schedules, home-office ergonomics, managing mixed work styles, async communication, four-day week, work-life boundaries, meeting hygiene, digital nomad basics. Add a videos page with lite (click-to-load) YouTube embeds of verified talks.

### Phase 4 — Monetization and lead generation
> Build a dedicated **For teams** page with a 3-step lead form (goals → team size/model/timeline → contact) and FAQ; an email-gated full report on quiz results; a newsletter signup in the footer; a **Support** page with donation tiers, a pledge form and switchable PayPal/Stripe/Buy-Me-a-Coffee links in `assets/js/config.js`; a **Contests** page (Show Your Setup, Work Style Story, Best Hybrid Teams) with rules and entry form; a **Careers** page for writers, creators, coaches, ambassadors, developers and commission sales; an **Advertise** page with sponsorship packages and a media-kit request form.

### Phase 5 — Launch
> Push to `webworksa1/work-style` on `main` and `gh-pages`, publish via GitHub Pages, then: point the work.style DNS to GitHub Pages and add a `CNAME` file containing `work.style`, enable "Enforce HTTPS", submit sitemap to Google Search Console, and apply for AdSense on the custom domain.

### Phase 6 — Scale (after AdSense approval)
> Add: programmatic "best work style for [role]" pages; "X vs Y" method comparisons; a yearly "State of Work Styles" report from anonymized assessment counts; team compatibility (pair) report; remote job feed; affiliate roundups for chairs, desks and software with verdict boxes.

---

## 3. Operating notes
- **Edit content:** change `_build/` sources (guides are Markdown in `_build/guides/`, archetypes in `_build/styles_data.py`), then run `python3 _build/build.py` and commit the regenerated HTML.
- **Forms:** the first submission triggers a one-time FormSubmit activation email to the owner inbox — click it once, and all forms go live.
- **Payments:** paste links into `assets/js/config.js` → `payments` to switch Support from pledge mode to instant checkout.
