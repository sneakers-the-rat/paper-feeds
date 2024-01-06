class DBMigrationError(RuntimeError):
    """
    Our database needs migrations!
    """

class FetchError(RuntimeError):
    """
    Something wrong with fetching data!
    """