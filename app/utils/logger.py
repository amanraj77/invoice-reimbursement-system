import logging
import sys
from app.config import Config

def setup_logger():
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('invoice_system.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()