import logging
import os
from datetime import datetime

def get_logger(name="process_manager"):
   
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
   
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    
    if not logger.handlers:
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
         
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
              
        log_file = f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
             
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
