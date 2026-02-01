from logging import Logger, getLogger, NullHandler

tlogger: Logger = getLogger(__name__).addHandler(NullHandler())
