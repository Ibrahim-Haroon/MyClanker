import logging
from flask import Flask
from flask_cors import CORS
from src.util.logging_config import setup_logging
from src.rest.api.clanker_api import clanker_routes
from src.util.env import Env


class MyClanker:
    def __init__(self, host=None, port=None):
        env = Env()
        self.__app = Flask(__name__)
        self.__host = host or env['HOST'] or '0.0.0.0'
        self.__port = int(port or env['PORT'] or 8000)
        self.__configure_app()

    def __configure_app(self):
        """Configure Flask application with middleware and routes"""
        CORS(self.__app)
        clanker_routes(self.__app)

    def run(self):
        self.__app.run(
            host=self.__host,
            port=self.__port,
            debug=False
        )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")
    server = MyClanker()
    server.run()


if __name__ == "__main__":
    main()
