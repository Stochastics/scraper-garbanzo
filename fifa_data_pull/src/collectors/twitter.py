import logging

LOGGER = logging.getLogger(__name__)


def collect(config: dict, keywords: list[str]):
    if config.get('enabled', False):
        LOGGER.info('X/Twitter collection requires API access. Historical data may require paid full-archive access. This collector is a placeholder.')
    return [], []
