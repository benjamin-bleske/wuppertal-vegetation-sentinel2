# Sentinel Wiki – Schema

An LLM-maintained knowledge base on Sentinel satellite imagery (Copernicus: Sentinel-1/2/3/5P, etc.) and the work built on it. Language: match the user (German or English); keep page titles consistent once chosen.

## Layers
- `raw/` – immutable sources (articles, papers, product docs, notes, images in `raw/assets/`). Never modify; only read.
- `wiki/` – LLM-owned markdown. The user reads, the LLM writes.
  - `wiki/sources/` – one summary page per raw source (`<slug>.md`)
  - `wiki/entities/` – missions, satellites, instruments, products, tools, datasets, organisations, projects, sites
  - `wiki/concepts/` – processing levels, indices (NDVI…), methods, techniques, glossary
  - `wiki/analyses/` – filed answers, comparisons, syntheses worth keeping
  - `wiki/overview.md` – evolving top-level synthesis
  - `wiki/index.md` – catalog of every page: link + one-line summary, grouped by category
  - `wiki/log.md` – append-only chronology
- `CLAUDE.md` – this file; co-evolve it with the user.

## Page conventions
- Obsidian-style `[[wikilinks]]` (filename without `.md`); lowercase-kebab-case filenames.
- YAML frontmatter: `title`, `type` (source|entity|concept|analysis), `tags`, `updated` (YYYY-MM-DD), `sources` (list of source slugs backing the page).
- Cite sources inline as `[[sources/<slug>]]`. Flag contradictions explicitly under a `## Widersprüche / Contradictions` heading with both claims and their sources.
- Mark uncertain or unsourced claims as such; never invent facts.

## Workflows
**Ingest** (one source at a time unless told otherwise): read the source → discuss key takeaways with the user → write `wiki/sources/<slug>.md` → create/update affected entity and concept pages (typically 5–15 pages) → update `overview.md` if the synthesis shifts → update `index.md` → append to `log.md`.

**Query**: read `index.md` first, then drill into relevant pages; answer with citations. Offer to file valuable answers under `wiki/analyses/` (then update index + log).

**Lint** (on request): contradictions, stale claims, orphan pages, concepts mentioned without a page, missing cross-references, data gaps (suggest web searches/new sources). Report findings, fix what is safe, log the pass.

## Log format
`## [YYYY-MM-DD] ingest|query|lint|setup | Title` followed by 1–3 lines listing pages touched. Check recent entries with `grep "^## \[" wiki/log.md | tail -5`.
