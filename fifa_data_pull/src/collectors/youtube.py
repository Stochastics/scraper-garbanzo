import logging
import os

LOGGER = logging.getLogger(__name__)


def collect(config: dict, keywords: list[str]):
    if not config.get('enabled', False):
        return [], []
    if not os.getenv('YOUTUBE_API_KEY'):
        LOGGER.info('YouTube enabled but YOUTUBE_API_KEY missing. Skipping.')
        return [], []
    LOGGER.info('YouTube collector scaffold present; implementation can be expanded.')
    return [], []
