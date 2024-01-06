# paper-feeds

![PyPI - Version](https://img.shields.io/pypi/v/paper-feeds)
[![Coverage Status](https://coveralls.io/repos/github/sneakers-the-rat/paper-feeds/badge.svg)](https://coveralls.io/github/sneakers-the-rat/paper-feeds)

A FastAPI web server for creating RSS feeds for scholarly journals with the magic of adversarial interoperability

Many journals still have RSS feeds. Some don't though, as they try
and squeeze everyone onto their platforms to monetize our 
engagement data.

This is a simple web app for creating feeds (currently RSS, soon ActivityPub and Atom) for academic papers by
collecting metadata from multiple data sources. It intended to be a publicly- and self-hostable
toolkit for subscribing to and curating scholarly literature!

Dependencies are kept minimal, as
is deployment - No webpack, no complex build, no postgres,
just pip install and press play :).

# usage

(to be completed when main docs are, for now here's something brief)

After [creating and activating a virtual environment...](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)

```bash
pip install paper-feeds
python -m paper_feeds
# then open http://localhost:8000 in your browser
```

Note: we are still working out the packaging here, so you may
need to clone the repository and run the server from the repo
root until we can figure that out :)

And see [CONTRIBUTING.md](./CONTRIBUTING.md) for more information on setting up
a development environment

# progress

Everything is just getting started! things will break and change! To be moved to docs when made. Help wanted on all, open an issue <3

API:
- [x] Query Crossref for journal
- [x] Write journal metadata to db
- [x] Paginate papers by journal
- [x] Store papers in db
- [x] Populate papers when feed created
- [ ] Periodic database updates
- [ ] Cache Feed output
- [ ] Scheduled update of feed metadata
- [ ] Backfill Abstracts and other additional data
- [ ] Feed statistics

Frontend
- [x] Search for journal
- [x] Display list of journals
- [x] Pages for each journal
- [x] Create new feed button
- [ ] Copy feed link
- [ ] Export feeds
- [ ] Show existing feeds, stats, threads

Feed Types
- [x] Journals
- [ ] Authors (via ORCID)
- [ ] Keywords

Feed Formats
- [ ] RSS
  - [x] RSS feed from papers by issn
  - [ ] Linked Data-enriched RSS feeds
  - [ ] HTML formatting for item details
- [ ] Activitypub
  - [ ] Actors for feeds
  - [ ] LD-enriched ActivityStreams actions
  - [ ] Bot-Actor for instance
  - [ ] DOI mention detection & crossref events data
  - [ ] Hashtag -> keyword detection
  - [ ] Create threads under feed actor with mention

Data Sources
- [x] Crossref
  - [x] Journals
  - [x] Papers
  - [ ] Events
- [ ] OpenAlex
- [ ] ORCID
- [ ] PubPeer
- [ ] RetractionWatch
- [ ] Hypothes.is

Meta
- [ ] Docs
  - [ ] We need em! Sphinx & RTD!
  - [ ] Move this list to there
  - [ ] Scope
  - [ ] Design
  - [ ] Usage
  - [ ] Configuration
- [ ] Tests
  - [x] Basic CI

# Credits
- El Duvelle, whose need for RSS feeds inspired this project
- @lambdaloop (list PRs)
- @roaldarbol (list PRs)

# References

- https://github.com/marty331/fasthtmx/
- https://samherbert.net/svg-loaders/
- https://htmx.org/examples/active-search/

# See also

- https://github.com/internetarchive/fatcat-scholar
