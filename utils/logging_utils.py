import logging
import sys
from datetime import datetime

def setup_logger():
    root_logger = logging.getLogger()
    logFormatter = logging.Formatter("%(name)-27s: %(levelname)-8s- %(message)s")
    
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(logFormatter)
    
    fileHandler = logging.FileHandler(f"data/{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    fileHandler.setFormatter(logFormatter)

    root_logger.addHandler(streamHandler)
    root_logger.addHandler(fileHandler)

    root_logger.setLevel(logging.INFO)

    return root_logger

def get_logger():
    return logging.getLogger()