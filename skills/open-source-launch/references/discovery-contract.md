# GitHub discovery, SEO, and GEO contract

Snapshot: 2026-08-11.

## First principles

Discovery is a chain:

```text
user intent -> eligible/indexable source -> understandable evidence
-> retrieved result -> trusted click/install -> first success -> retention
```

SEO helps search systems understand and surface useful content. “GEO” is used
here as shorthand for making verified project facts easy for answer engines to
retrieve, attribute, and cite. Neither has a magic GitHub switch.

## Intent map

Create a small map before rewriting:

| User job | Natural query variants | Best evidence surface | First action |
| --- | --- | --- | --- |
| What problem does it solve? | category + task + platform | README first paragraph | inspect proof |
| Can I run it? | install + OS/runtime | Quick start/release | copy install |
| Is it safe/private? | data + permissions + telemetry | trust/security docs | inspect boundary |
| Does it fit my stack? | integration + protocol + version | compatibility/docs | run example |
| How do I fix failure X? | exact error + product name | troubleshooting/issue | recover |

Use the language naturally. Google explicitly discourages keyword stuffing and
does not use the meta-keywords tag.

## GitHub surfaces

### Repository metadata

- **Name:** stable, memorable, and not deceptively generic.
- **Description:** one concise sentence with category, primary job, and relevant
  platform—not a slogan wall.
- **Homepage:** canonical docs/product URL when one exists.
- **Topics:** focused purpose, subject, ecosystem, platform, and language terms.
  GitHub topic names are public, lowercase/hyphenated, at most 50 characters,
  and limited to 20; use fewer high-signal topics.
- **Social preview:** truthful product image, preferably 1280×640 and under
  1 MB, readable on light/dark sharing surfaces.

### README and docs

- Canonical product name and plain definition in the title/first paragraph.
- Descriptive headings, concrete examples, expected outputs, compatibility,
  limitations, and exact error text where useful.
- Descriptive alt text near relevant explanatory text.
- Stable links to releases, packages, docs, security, support, and examples.
- FAQ only for real adoption questions; do not manufacture search bait.
- Source-backed comparisons and benchmarks with method, date, conditions, and
  reproducible evidence.

### Docs website, when justified

Use a site when the repository needs durable guides, reference pages, or
landing pages beyond a README. Then verify canonical URLs, crawlability,
sitemap, robots, titles/descriptions, structured data where applicable, and
Search Console. Do not add these artifacts to a repository that has no website
and call the work complete.

`llms.txt` is optional and not a success signal. Add it only to a real docs site
when there is a maintained canonical document map and a verified consumer or
product need. Eligibility is not retrieval, citation, recommendation, or
conversion.

## Evidence levels

Track each finding as:

- `observed` — directly read from GitHub, Search Console, analytics, or a live
  answer-engine result;
- `inferred` — plausible from content/structure but not observed downstream;
- `missing_evidence` — requires indexing, query, citation, or conversion data.

Do not claim SEO/GEO success because metadata exists, CI passed, a sitemap was
submitted, or an AI system cited the project once.

## Measurement

Use metrics that correspond to the chain:

- repository impressions/referrers when available;
- release/package downloads and clone windows;
- quick-start completion failures and support issues;
- documentation queries/clicks for a docs site;
- qualified citations/mentions with captured prompt, model, date, and source;
- repeat users, retained contributors, and downstream projects.

GitHub Traffic is an owner-only rolling window, not lifetime analytics. Public
visitor badges may include bots and repeat loads.

## Primary sources

- GitHub README guidance:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- GitHub topics:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- GitHub social preview:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview
- GitHub community health:
  https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions
- Google SEO Starter Guide:
  https://developers.google.com/search/docs/fundamentals/seo-starter-guide
