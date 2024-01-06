# paper-feeds

![PyPI - Version](https://img.shields.io/pypi/v/paper-feeds)
[![Coverage Status](https://coveralls.io/repos/github/sneakers-the-rat/paper-feeds/badge.svg)](https://coveralls.io/github/sneakers-the-rat/paper-feeds)

A FastAPI web server for creating RSS feeds for scholarly journals with the magic of adversarial interoperability

Many journals still have RSS feeds. Some don't though, as they try
and squeeze everyone onto their platforms to monetize our 
engagement data.

This is a simple web app for creating RSS feeds for journals by
collecting metadata from crossref. Dependencies are kept minimal, as
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

Everything is just getting started! things will break and change!

API:
- [x] Query Crossref for journal
- [x] Write journal metadata to db
- [x] Paginate papers by journal
- [x] Store papers in db
- [x] Populate papers when feed created
- [ ] Create RSS feed from papers by issn
- [ ] Cache RSS feeds
- [ ] Scheduled update of feed metadata

Frontend
- [x] Search for journal
- [x] Display list of journals
- [ ] Pages for each journal
- [x] Create new feed button
- [ ] Copy feed link
- [ ] Export feeds

# Credits

- https://github.com/marty331/fasthtmx/
- https://samherbert.net/svg-loaders/
- https://htmx.org/examples/active-search/

# See also

- https://github.com/internetarchive/fatcat-scholar
