# Contributing

This is a new and semi-informal project, so contributing guidelines very much in flux!
Making this to keep notes as they develop <3

## Code style

Docstring style: [Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

## Setting up development environment

TODO. For now, just...

Set up the repo:

```bash
git clone https://github.com/sneakers-the-rat/paper-feeds
cd paper-feeds

# make a new branch to work on!
git branch -b my-new-branch dev
git switch my-new-branch
```

If you're using poetry...

```bash
poetry install --extras "tests"
poetry run start
```

Otherwise...

```bash
python -m venv ./venv
source ./venv/bin/activate
pip install -e '.[tests]'
python -m paper_feeds
```

## Making Pull Requests

- First raise an issue to discuss potential PRs (unless they are blaringly obvious/there is only one possible implementation/fix. use ur discretion <3)
- Pull against the `dev` branch
- Write tests for newly added code.
- If you have changed any of the database models, write a database migration with [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- Ensure tests pass! If you've installed the package with the `tests` extras (eg. `pip install paper-feeds[tests]`),
  then all you need to do is run `pytest` from the repository root

## Writing Migrations

See the [alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) and
[auto generating migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

In short... If your change is something that alembic can automatically detect:

> - Table additions, removals. 
> - Column additions, removals.
> - Change of nullable status on columns.
> - Basic changes in indexes and explicitly-named unique constraints
> - Basic changes in foreign key constraints
> - Changes of column type (see [comparing types](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#compare-types))

Then... 

```bash
alembic revision --autogenerate -m "Description of change!"
```

If you have changed something not in the above list, see the alembic docs for how to
write migrations for things that alembic *can't* detect, like:

- changes of table name
- changes of column name
- anonymous/unnamed constraints
- certain changes in type!
