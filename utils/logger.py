#!/usr/bin/env python3
"""
Logger - SDN controller ve test olaylarını loglar
"""

import logging
import os
from datetime import datetime
from colorlog import ColoredFormatter


class SDNLogger:
    def __init__(self, name='SDN', log_dir='../logs', console_level=logging.INFO, file_level=logging.DEBUG):
        """
        Args:
            name: str - Logger adı
            log_dir: str - Log dosyalarının kaydedileceği dizin
            console_level: int - Konsol log seviyesi
            file_level: int - Dosya log seviyesi
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Log dizinini oluştur
        os.makedirs(log_dir, exist_ok=True)
        
        # Dosya handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Konsol handler (renkli)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        
        # Renkli formatter
        console_formatter = ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            datefmt='%H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler'ları ekle
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logger initialized: {name}")
        self.logger.info(f"Log file: {log_file}")
    
    def get_logger(self):
        """Logger instance'ını döndür"""
        return self.logger


# Test için
if __name__ == '__main__':
    logger = SDNLogger('TestLogger').get_logger()
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
