import uvicorn

from paper_feeds.config import Config

class Server(uvicorn.Server):
    """
    Uvicorn server that also shuts down rocketry

    References:
        - https://rocketry.readthedocs.io/en/stable/cookbook/fastapi.html
    """
    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


def start():
    config = Config()
    uvicorn.run(
        "paper_feeds.app:app",
        host=config.host,
        port=config.port,
        reload=config.reload
    )

