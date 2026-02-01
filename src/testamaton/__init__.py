from logging import Logger, NullHandler, getLogger

tlogger: Logger = getLogger(__name__).addHandler(NullHandler())
