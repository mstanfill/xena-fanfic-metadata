# Fan Fiction Metadata Scraper

A polite scraper that collects story **metadata** (titles, authors, part
links, summaries, tags and ratings, but not story text) from three
fan-run Xena: Warrior Princess fan fiction archives. Each site's records are
converted to one shared schema so they can be compared across sites.

| Site | Entry point | Source of metadata | Scale |
| --- | --- | --- | --- |
| xenafan.com | [`/fiction/titles.html`](https://xenafan.com/fiction/titles.html) | one title index, plus optional part-1 story pages | ~1,450 stories |
| Academy of Bards | [`/authors/`](https://www.academyofbards.org/authors/) | author index, then one page per author | ~920 authors |
| The Athenaeum (xenafiction.net) | [search results](http://xenafiction.net/styles/athenaeum_deepblue/index2.cfm?art=0) | paginated search results, 50 per page | ~6,966 works |

These are small, old, volunteer-run servers that are no longer updated.
The scraper is built to put as little load on them as possible; please keep
it that way (see [Responsible use](#responsible-use)).

## Status

| Stage | xenafan | Athenaeum | Academy |
| --- | --- | --- | --- |
| Live check (robots.txt + a few pages) | done | done | done |
| Parser | done | done | done |
| Full crawl | index: 1 request; story-page pass via `fanfic-enrich-xenafan --all` | code exists (`discover_athenaeum(max_pages=None)`), no command or export yet | not built: only the 5 sample authors are fetched |
| Cross-site merge (`merge.py`) | not built | not built | not built |

`title_normalized` is only lowercased on xenafan and empty for the other
sites; real normalization is planned for the merge stage.

## Install

Requires Python 3.10 or newer.

```sh
git clone https://github.com/mstanfill/xena-fanfic-metadata.git
cd xena-fanfic-metadata
pip install -e ".[dev]"             # add ,notebooks for JupyterLab
```

## Contact email (required for downloads)

Every request carries a User-Agent of the form
`fanfic-metadata-research (you@example.org)`, so site operators can reach
whoever is crawling. **Use your own address.** Either set it once:

```sh
export FANFIC_CONTACT_EMAIL=you@example.org
```

or leave it unset and you will be asked for it the first time a download is
actually needed. In the notebooks, fill in the `CONTACT_EMAIL` setting.
Anything that only reads saved pages never asks. If no email is available,
the scraper stops before sending any request.

## Usage

Run commands from the repository root. Saved pages, the crawl queue and
output files go to `./data/`, or to the folder named by `FANFIC_DATA_DIR`.
`data/` is git-ignored.

The recommended order for each site is: **verify, then review the sample,
then (if the sample looks right) the full pass.**

| Command | Notebook | Network |
| --- | --- | --- |
| `fanfic-verify-xenafan` | `verify_xenafan.ipynb` | robots.txt + titles.html (2 requests) |
| `fanfic-verify-athenaeum` | `verify_athenaeum.ipynb` | robots.txt + search pages 1–2 (3 requests) |
| `fanfic-verify-academy` | `verify_academy.ipynb` | robots.txt + index + 5 author pages (7 requests) |
| `fanfic-sample-xenafan` | `run_xenafan_sample.ipynb` | none if verify was run; otherwise downloads what's missing |
| `fanfic-sample-athenaeum` | `run_athenaeum_sample.ipynb` | none if verify was run; otherwise downloads what's missing |
| `fanfic-sample-academy` | `run_academy_sample.ipynb` | none if verify was run; otherwise downloads what's missing |
| `fanfic-enrich-xenafan` | `enrich_xenafan_stories.ipynb` | ~6 story pages; `--all` (or `RUN_ALL = True`) for ~1,450, about 2.5 h |

Every command can also be run as `python -m fanfic_scraper.scripts.<name>`,
for example `python -m fanfic_scraper.scripts.verify_xenafan`. A page that has
already been saved is never downloaded again. robots.txt is the one exception:
it is requested once at the start of every run that downloads anything.

### Notebooks

Each command has a notebook in `notebooks/` that does the same thing step by
step, with extra cells for searching and reviewing the records. Open them
with `jupyter lab` from the repository. They find the repository root
themselves, so they use the same `data/` folder whether you start Jupyter
in the root or in `notebooks/`, and they work without `pip install -e .`.
Notebooks are committed without outputs; please clear outputs before
committing, since they can contain scraped data.

## Safeguards

All network access goes through `fanfic_scraper/fetch/`, which enforces:

- **One request at a time per site**, with a random 5–10 s pause between
  requests.
- **robots.txt**: checked before crawling. `Disallow` rules are honored, a
  longer `Crawl-delay` widens the pause, and if robots.txt can't be read
  (server error or no connection) the site is not crawled at all.
- **Identification**: the User-Agent carries your contact email (see above).
- **Backoff**: on 429, 5xx, timeouts or connection errors the fetcher waits
  2, 4, 8, 16, 32 s between retries, and marks a page failed after 5
  attempts. The xenafan story-page pass stops after 3 failures in a row.
- **Disk cache**: every response is saved exactly as received (one file per
  normalized URL, plus a JSON sidecar with status, headers and fetch time),
  and parsers read only from the cache.
- **Resumable**: a SQLite queue (`data/scrape.db`) records each page as
  pending, fetched, failed or skipped by robots.txt.
- **URL normalization**: scheme, host, `www.` and `%20` are made consistent
  so the same page is never fetched under two addresses.
- **Index pages, not stories**: listings and author pages are used wherever
  they carry the metadata. Story bodies are never crawled; the optional
  xenafan pass reads only part 1 of each story, for its header block.

Known limits: the pause timer lives in memory, so don't run two commands
against the same site at once. Pages marked failed stay failed until you
remove them from the `queue` table. Only `Disallow` and `Crawl-delay` are
read from robots.txt (`Allow` exceptions are ignored, which is stricter).

## Responsible use

- **Run the sample and look at it before any full crawl.** Fix parser
  problems against the saved pages, which costs the sites nothing.
- **Crawl once.** The sites are frozen; keep your cache rather than
  re-crawling. For later updates, re-fetch only Academy authors whose "Last
  Updated" date changed. The [Wayback Machine](https://web.archive.org/) may
  also have usable snapshots.
- **Personal data.** Story headers and author pages can include authors'
  email addresses and other personal details. Do not publish raw pages or
  unfiltered output. Strip or minimize personal fields before sharing
  derived datasets, and follow your institution's research-ethics guidance.
- **Copyright.** Summaries and teasers belong to their authors. Quote them
  in line with fair use or fair dealing, and don't redistribute the cache.

## Record schema

Every site produces `fanfic_scraper.parse.schema.Record` objects, one per
story per site (records from different sites are never collapsed).

| Field | xenafan | Academy | Athenaeum |
| --- | --- | --- | --- |
| `source_site`, `source_id`, `title`, `authors`, `parts`, `status`, `fetched_from` | ✓ | ✓ | ✓ |
| `source_id` is | story URL | part-1 URL | site ID (`I_KEY`) |
| `author_page_url` | enrichment pass | ✓ | ✓ |
| `work_type` (poem, song, screenplay…) | ✓ | ✓ (`[poem]`-style tags) | |
| `summary` | | ✓ | ✓ (teaser) |
| `series`, `series_members` | | ✓ | members only |
| `universe`, `era`, `orientation`, `genre`, `length_pages`, `date` | | | ✓ |
| `cast`, `related_episodes`, `awards`, `ratings` | | | ✓ |
| `ebook_available` / `ebook_links` | | flag only | ✓ |
| `external_url` (off-site stories) | ✓ | | ✓ |
| `disclaimer_text` | enrichment pass | | |
| `notes` (sequel notes, contest tags, Academy co-authors, mismatches…) | ✓ | ✓ | ✓ |

Text is decoded using the declared charset, falling back to cp1252 and
latin-1, and mojibake is repaired with [`ftfy`](https://github.com/rspeer/python-ftfy).

## Repository layout

```
fanfic_scraper/
  fetch/      the only code that touches the network: politeness, robots.txt,
              backoff, disk cache, SQLite queue, URL normalization
  discover/   one module per site: works out which pages to fetch
  parse/      one parser per site: saved HTML -> Record
  scripts/    the commands listed above
notebooks/    one notebook per command
tests/        unit tests; they use invented sample pages and fake HTTP
              and never contact the live sites
```

## Tests

```sh
pytest
```

The tests run on GitHub Actions for Python 3.10–3.13 on every push and pull
request. The sample HTML in the tests is invented: it copies the real sites'
markup but contains no real titles, authors or addresses.

## License

[MIT](LICENSE).
