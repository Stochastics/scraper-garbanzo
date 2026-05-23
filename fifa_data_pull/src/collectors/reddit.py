import logging
import os

LOGGER = logging.getLogger(__name__)


def collect(config: dict, keywords: list[str]):
    if not config.get('enabled', False):
        return [], []
    required = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
    if any(not os.getenv(k) for k in required):
        LOGGER.info('Reddit enabled but credentials missing. Skipping.')
        return [], []
    LOGGER.info('Reddit collector scaffold present; implementation can be expanded.')
    return [], []
