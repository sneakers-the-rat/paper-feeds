import uvicorn

from paper_feeds.config import Config


def start() -> None:
    config = Config()
    uvicorn.run(
        "paper_feeds.app:app", host=config.host, port=config.port, reload=config.reload
    )
