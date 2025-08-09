import logging
import threading
from flask import Flask
from flask_cors import CORS
from src.util.logging_config import setup_logging


class MyClanker:
    def __init__(self, host='0.0.0.0', port=8000):
        self.__app = Flask(__name__)
        self.__host = host
        self.__port = port
        self.__configure_app()

    def __configure_app(self):
        """Configure Flask application with middleware and routes"""
        CORS(self.__app)

    def run(self):
        threading.Thread(
            target=lambda: self.__app.run(
                host=self.__host,
                port=self.__port,
                debug=False
            ),
            daemon=True
        ).start()


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")
    server = MyClanker()
    server.run()


if __name__ == "__main__":
    main()
