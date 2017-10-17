import logging
import tornado.log

logger = logging.getLogger()
tornado.log.enable_pretty_logging(logger=logger)


def getLogger():
    return logger
