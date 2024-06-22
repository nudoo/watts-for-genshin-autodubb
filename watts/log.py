from NsparkleLog import LogManager


def new_logger(name, debug=True):
    logger = LogManager.GetLogger(name)
    return logger
