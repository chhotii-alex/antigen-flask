from flask import has_request_context, request
import logging
from flask.logging import default_handler

class RequestFormatter(logging.Formatter):
    def format(self, record):
        print("formatting a record")
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

def set_up_logging():
    formatter = RequestFormatter(
        '--here is the custom log format--'
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
        '--end one log entry--'
    )
    default_handler.setFormatter(formatter)

    print("Set log format...")

