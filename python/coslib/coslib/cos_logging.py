import logging

logger = logging.getLogger('cos')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(name)s][%(filename)s:%(lineno)s]: %(message)s')
# [%(threadName)s]

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