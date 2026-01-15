from configparser import ConfigParser
from pathlib import Path
import ast
from datetime import datetime
from .settings import TestPreferences, TwilioConfig, BrowserConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str = "config.ini"):
        self.config_path = Path(config_path)
        self.parser = ConfigParser()
        
    def load(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        self.parser.read(self.config_path)
        
        try:
            preferences = self._load_preferences()
            twilio = self._load_twilio()
            browser = self._load_browser()
            
            logger.info("Configuration loaded successfully")
            return preferences, twilio, browser
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_preferences(self):
        section = self.parser['preferences']
        
        return TestPreferences(
            licence=section.get('licence'),
            booking=section.get('booking'),
            current_test_date=datetime.strptime(
                section.get('current_test_date'), 
                "%A %d %B %Y %I:%M%p"
            ),
            formatted_current_test_date=datetime.strptime(
                section.get('formatted_current_test_date'),
                "%Y-%m-%d"
            ).date(),
            current_test_centre=section.get('current_test_centre'),
            disabled_dates=[
                datetime.strptime(d, "%Y-%m-%d").date() 
                for d in ast.literal_eval(section.get('disabled_dates'))
            ],
            preferred_centres=ast.literal_eval(section.get('centre')),
            before_date=datetime.strptime(section.get('before_date'), "%Y-%m-%d").date(),
            after_date=datetime.strptime(section.get('after_date'), "%Y-%m-%d").date(),
            auto_book_test=section.getboolean('auto_book_test')
        )
    
    def _load_twilio(self):
        section = self.parser['twilio']
        return TwilioConfig(
            account_sid=section.get('account_sid'),
            auth_token=section.get('auth_token'),
            messaging_service_sid=section.get('messaging_service_sid'),
            phone_number=section.get('phone_number')
        )
    
    def _load_browser(self):
        section = self.parser['chromedriver']
        return BrowserConfig(
            driver_path=section.get('driver_path', '/bin/chromedriver'),
            run_on_vm=section.getboolean('run_on_vm', False),
            solve_manually=section.getboolean('solve_manually', False),
            enable_buster=section.getboolean('enable_buster', True),
            buster_path=section.get('buster_path', './buster-chrome.zip'),
            headless=section.getboolean('headless', False)
        )
