import logging

ROOT_LOGGER = 'uvicorn.error'

def init_logger(name:str = '') -> logging.Logger:
    """
    Placeholder logging module for now :)

    .. todo::

        fill in with That Good Logging later :)

    """
    name = '.'.join([ROOT_LOGGER, name])
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

