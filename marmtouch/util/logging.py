import logging
import sys

from marmtouch._version import version


def getLogger(
    fileName="",
    fileMode="a",
    fileLevel="DEBUG",
    printLevel="WARN",
    capture_warnings=True,
    capture_errors=True,
):
    """Utility that returns a logger object

    Parameters
    ----------
    loggerName: str
        Name for the logger, usually just provide __name__
    fileName: str or bool, optional
        Name for the log file, if False no log file is generated
    fileMode: str, optional, default: 'a'
        Mode for opening log file (e.g. 'w' for write, 'a' for append).
    fileLevel: {'DEBUG','INFO','WARN'}, optional, default: 'DEBUG'
        Log level for FileHandler
    printLevel: {'DEBUG','INFO','WARN'}, optional, default: 'WARN'
        Log level for StreamHandler
    capture_warnings: bool, optional, default: True
        Captures warnings to be processed by logger
    capture_errors: bool, optional, default: True
        Captures errors to be processed by logger

    Returns
    -------
    logger: logging.Logger
        A logger object with FileHandler and StreamHandler as configured. Note the logger is a singleton.
    """
    logger_levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARN": logging.WARN}
    name = f"marmtouch v{version}"
    logger = logging.getLogger(name)
    logging.captureWarnings(capture_warnings)

    if logger.hasHandlers():
        logger.handlers[:] = []

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if fileName:
        if not fileLevel in logger_levels:
            raise ValueError(
                f"Provided invalid fileLevel '{fileLevel}'. Valid options: {logger_levels.keys()}"
            )
        fileHandler = logging.FileHandler(fileName, mode=fileMode)
        fileHandler.setLevel(logger_levels[fileLevel])
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    if not printLevel in logger_levels:
        raise ValueError(
            f"Provided invalid printLevel '{printLevel}'. Valid options: {logger_levels.keys()}"
        )
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(printLevel)
    logger.addHandler(streamHandler)

    if capture_errors:
        sys.stderr = LoggerWriter(logger.error)
        logger.info(f"stderr redirected to: {logger}")
    return logger


class LoggerWriter:
    """A mock file-like stream for redirecting to logger

    Parameters
    ----------
    writer: callable
        stream is processed and passed to this callable

    References
    ----------
    [1] https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
    """

    def __init__(self, writer):
        self._writer = writer
        self._msg = ""

    def write(self, message):
        self._msg = self._msg + message
        while "\n" in self._msg:
            pos = self._msg.find("\n")
            self._writer(self._msg[:pos])
            self._msg = self._msg[pos + 1 :]

    def flush(self):
        if self._msg != "":
            self._writer(self._msg)
            self._msg = ""
