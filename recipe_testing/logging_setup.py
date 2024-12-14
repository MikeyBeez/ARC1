"""Logging configuration for recipe testing"""

import logging
from pathlib import Path

class RunIdFilter(logging.Filter):
    """Filter that adds run_id to log records"""
    def __init__(self):
        super().__init__()
        self.run_id = None
        
    def filter(self, record):
        record.run_id = self.run_id if self.run_id else 'no_run'
        return True

def setup_logging(base_dir: Path) -> tuple[logging.Logger, RunIdFilter]:
    """Configure logging with run ID support"""
    log_format = (
        '%(asctime)s.%(msecs)03d [%(levelname)s] '
        '%(message)s (run_id=%(run_id)s)'
    )
    date_format = '%Y-%m-%d %H:%M:%S'
    
    run_id_filter = RunIdFilter()
    
    # Configure file handler
    handler = logging.FileHandler(
        base_dir / 'recipe_testing.log',
        encoding='utf-8'
    )
    handler.setFormatter(
        logging.Formatter(log_format, date_format)
    )
    
    # Configure logger
    logger = logging.getLogger('recipe_tester')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addFilter(run_id_filter)
    
    return logger, run_id_filter