import logging


def set_config(logger):
    # logger = logging.getLogger(__name__)
    handler = logging.FileHandler('core.log')
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

