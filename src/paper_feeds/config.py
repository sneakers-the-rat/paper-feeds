from typing import Optional, Literal
from pathlib import Path
from importlib.metadata import version
if version('pydantic').startswith('2'):
    from pydantic_settings import BaseSettings, SettingsConfigDict
else:
    from pydantic import BaseSettings

class Config(BaseSettings):
    if version('pydantic').startswith('2'):
        model_config = SettingsConfigDict(
            env_file='.env',
            env_file_encoding='utf-8',
            env_prefix="paperfeeds_")
    else:
        class Config:
            env_prefix = 'paperfeeds_'
            env_file_encoding='utf-8'
            env_file='.env'


    db: Optional[Path] = Path('./db.sqlite')
    """
    Optional, if set to ``None`` , use the in-memory sqlite DB
    """
    log_dir: Path = Path('./logs')
    host: str = "localhost"
    port: int = 8000
    env: Literal['dev', 'prod'] = 'dev'
    crossref_email: Optional[str] = None
    """
    Crossref wants you to give an email address when you use
    their API! https://github.com/CrossRef/rest-api-doc#good-manners--more-reliable-service
    """
    public_url: str = "http://localhost"
    refresh_schedule: str = "0 3 * * *"
    """
    Crontab expression to schedule when to refresh feeds. Default is every day at 3am
    """
    refresh_threads: int = 12


    @property
    def sqlite_path(self) -> str:
        if self.db is None:
            return 'sqlite://'
        else:
            return f'sqlite:///{str(self.db.resolve())}'

    @property
    def reload(self) -> bool:
        """whether to reload the wsgi server ie. when in dev mode"""
        if self.env == 'dev':
            return True
        else:
            return False

    def __post_init__(self):
        self.db.parent.mkdir(exist_ok=True, parents=True)
        self.log_dir.mkdir(exist_ok=True, parents=True)
