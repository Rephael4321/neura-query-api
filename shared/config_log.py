import logging
from datetime import datetime
from zoneinfo import ZoneInfo

class JerusalemTimeFormatter(logging.Formatter):
    def converter(self, timestamp):
        jerusalem_datetime = datetime.fromtimestamp(timestamp, ZoneInfo("Asia/Jerusalem"))
        return jerusalem_datetime

    def formatTime(self, record, datefmt=None):
        jerusalem_datetime = self.converter(record.created)
        if datefmt:
            return jerusalem_datetime.strftime(datefmt)
        else:
            return jerusalem_datetime.isoformat()

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
formatter = JerusalemTimeFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
logger.addHandler(console_handler)
