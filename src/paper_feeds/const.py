import importlib.resources

SCIHUB_URL = "https://sci-hub.se/"

TEMPLATE_DIR = importlib.resources.files("paper_feeds") / "templates"
STATIC_DIR = importlib.resources.files("paper_feeds") / "static"
