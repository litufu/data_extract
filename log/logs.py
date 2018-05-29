# _author : litufu
# date : 2018/5/18

import os
import json
import logging.config

def setup_logging(
    default_path=r'H:\data_extract\log\logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    setup_logging()
    logger.info('Start reading database')