import uvicorn

from journal_rss.config import Config

def start():
    config = Config()
    uvicorn.run(
        "journal_rss.app:app",
        host=config.host,
        port=config.port,
        reload=config.reload
    )

