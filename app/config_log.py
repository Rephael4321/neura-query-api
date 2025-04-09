import logging

logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)

formatter= logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
