# -*- coding: utf8 -*-

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

__all__ = (
           'get_logger',
          )

LOG_PATH = "/var/log/imap2gotify.log"

__LOG__ = None

def get_logger(path=LOG_PATH):
    global __LOG__
    
    if __LOG__ is not None:
        return __LOG__
        
    # Setup the log handlers to stdout and file.
    
    log = logging.getLogger('imap2gotify')
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)10s | %(message)s'
        )
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setLevel(logging.DEBUG)
    handler_stdout.setFormatter(formatter)
    
    log.addHandler(handler_stdout)
    
    if not LOG_PATH.strip():
        __LOG__ = log
        
        return log
        
    handler_file = RotatingFileHandler(
        LOG_PATH,
        mode='a',
        maxBytes=1048576,
        backupCount=9,
        encoding='UTF-8',
        delay=True
        )
    handler_file.setLevel(logging.DEBUG)
    handler_file.setFormatter(formatter)
    
    log.addHandler(handler_file)
    
    __LOG__ = log
    
    return log