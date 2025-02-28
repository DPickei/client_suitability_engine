import logging
import sys

def setup_logging():
    """Centralized logging configuration"""
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename="logging.log"
    )

