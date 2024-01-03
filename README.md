# journal-rss

A FastAPI web server for creating RSS feeds for scholarly journals with the magic of adversarial interoperability

Many journals still have RSS feeds. Some don't though, as they try
and squeeze everyone onto their platforms to monetize our 
engagement data.

This is a simple web app for creating RSS feeds for journals by
collecting metadata from crossref. Dependencies are kept minimal, as
is deployment - No webpack, no complex build, no postgres,
just pip install and press play :).

# progress

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
