import argparse
import logging
import yaml
import sys
from logging import FileHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from src.cli.movesense_cli import MovesenseCLI


def setup_file_logger():
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')

    # Add a StreamHandler to log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def parse_args():
    parser = argparse.ArgumentParser(description="Movesense CLI")
    parser.add_argument("--session", default=None, help="Path to the yaml that defines the data-collection "
                                                        "session. If none, connections will be prompted during "
                                                        "execution as a new session settings config.")
    return parser.parse_args()


def main():

    interface = None

    try:
        logger.info("Starting MoveSense CLI.")

        args = parse_args()
        config = None

        # Set up a file logger with console
        setup_file_logger()

        # If session config.yaml given, load
        if args.session:
            with open(args.session, 'r') as f:
                config = yaml.safe_load(f)

            logger.info("Found session config: {}".format(args.session))


        # Setup the CLI interface
        interface = MovesenseCLI(config)

        # interface.run_remote() # For remote testing
        interface.run() # For local testing

    except Exception as e:
        logger.error(e)

        if interface:
            interface.device_manager.disconnect_devices()

        sys.exit(-1)


if __name__ == "__main__":
    main()
