import logging


class IgnoreBrokenPipeFilter(logging.Filter):
    def filter(self, record):
        return "Broken pipe from" not in record.getMessage()
