import logging
import sys


# TODO logger class not working as expected

class Logger:
    def __init__(self):
        self.format = '%(asctime) s %(levelname) -8s [%(filename) s:%(lineno) d] %(message) s'
        self.datefmt = '%d-%m-%Y:%H:%M:%S'
        self.level = logging.INFO

    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "CRITICAL": logging.CRITICAL

    }

    def get_file_logger(self, level, filename='logs.log'):
        level = level.upper()
        logging.basicConfig(format=self.format,
                            datefmt=self.datefmt,
                            level=self.levels[level],
                            filename=filename)

        return logging.getLogger('bol_file')

    def get_commandline_logger(self, level):
        level = level.upper()
        logging.basicConfig(format=self.format,
                            datefmt=self.datefmt,
                            level=self.levels[level],
                            stream=sys.stdout)

        return logging.getLogger('bol_commandline')
