import logging
import json
from datetime import datetime

# logging.basicConfig(filename='/tmp/dp.log', format='%(message)s', level=logging.INFO)
logging.basicConfig(format='%(message)s', level=logging.INFO)

# logger.debug("Harmless debug Message")
# logger.info("Just an information")
# logger.warning("Its a Warning")
# logger.error("Did you try to divide by zero")
# logger.critical("Internet is down")


class logger(object):
    def __init__(self):
        #Creating an object
        self.logger=logging.getLogger('log')
 
    def log_json(self,json_array,cbsds=None):
        self.logger.info(f"timestamp: {datetime.now()} UTC timestamp: {datetime.utcnow()}")
        self.logger.info(f"number of cbsds: {cbsds}")
        self.logger.info(json.dumps(json_array,indent=4, sort_keys=True))

    def __getattr__(self, attr):
        return getattr(self.logger, attr)

dpLogger = logger()
