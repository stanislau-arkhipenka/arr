import logging
from typing import List

if 'tmp_log_data' not in globals():
    tmp_log_data: List[str] = []


class ListLogHandler(logging.StreamHandler):

    def emit(self, record):
            global tmp_log_data
            msg = self.format(record)
            tmp_log_data.append(msg)