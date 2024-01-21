import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)


_logger = logging.getLogger('totolo')
_logger.setLevel("INFO")

info = _logger.info
warning = _logger.warning
error = _logger.error
critical = _logger.critical
