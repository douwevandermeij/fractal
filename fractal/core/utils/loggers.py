import logging


def init_logging(loglevel):
    # create logger
    logger = logging.getLogger("app")
    logger.setLevel(loglevel)

    # create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)

    # create formatter
    formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
