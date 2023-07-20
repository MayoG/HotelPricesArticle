import logging
import sys
from datetime import datetime

def setup_logger():
    root_logger = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(logFormatter)
    
    fileHandler = logging.FileHandler(f"data/{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    fileHandler.setFormatter(logFormatter)

    root_logger.addHandler(streamHandler)
    root_logger.addHandler(fileHandler)

    root_logger.setLevel(logging.INFO)

    return logging.getLogger()
