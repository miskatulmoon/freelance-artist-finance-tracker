import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        json_indent=None,
    )
    handler.setFormatter(formatter)
    logger.handlers = [handler]

    # Ensure uvicorn uses the same config
    logging.getLogger("uvicorn").handlers = logger.handlers
    logging.getLogger("uvicorn.error").handlers = logger.handlers
    logging.getLogger("uvicorn.access").handlers = logger.handlers
