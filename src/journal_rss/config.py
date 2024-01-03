from typing import Optional, Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, DirectoryPath, computed_field, field_validator, model_validator, FieldValidationInfo

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix="jrss_")

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
