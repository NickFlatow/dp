import logging
import json
from datetime import datetime

# logging.basicConfig(filename='/tmp/dp_logs/dp.log', format='%(asctime)s - %(message)s', level=logging.DEBUG)
logging.basicConfig(filename='/tmp/dp.log', format='%(message)s', level=logging.DEBUG)

#Test messages
# logger.debug("Harmless debug Message")
# logger.info("Just an information")
# logger.warning("Its a Warning")
# logger.error("Did you try to divide by zero")
# logger.critical("Internet is down")


class logger():
    def __init__(self):
        #Creating an object
        self.logger=logging.getLogger()
        #Setting the threshold of logger to DEBUG
        self.logger.setLevel(logging.INFO)

 
    def log_json(self,json_array,cbsds=None):
        # parsed_json = json.loads(json_array)
        self.logger.info(f"timestamp: {datetime.now()} UTC timestamp: {datetime.utcnow()}")
        self.logger.info(f"number of cbsds: {cbsds}")
        self.logger.info(json.dumps(json_array,indent=4, sort_keys=True))

dpLogger = logger()