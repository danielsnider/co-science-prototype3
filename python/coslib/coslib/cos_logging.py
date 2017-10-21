import logging

logger = logging.getLogger('cos')
logger.setLevel(logging.DEBUG)
# create file handler that logs debug and higher level messages
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter('[%(levelname)s][%(threadName)s][%(name)s/%(filename)s:%(lineno)s]: %(message)s')

def log_to_stdout():
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  ch.setFormatter(formatter)
  logger.addHandler(ch)

log_to_stdout()

def log_to_file():
  fh = logging.FileHandler('spam.log')
  fh.setLevel(logging.DEBUG)
  fh.setFormatter(formatter)
  logger.addHandler(fh)

logdebug = logger.debug
loginfo = logger.info
logwarn = logger.warn
logerr = logger.error
logcritical = logger.critical