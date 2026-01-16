from configparser import ConfigParser
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import os
from dotenv import load_dotenv
from .settings import TestPreferences, TwilioConfig, BrowserConfig, NotificationConfig, OperatingHours
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    def __init__(self, config_path: Optional[str] = None):
        load_dotenv()
        
        self.config_path = Path(config_path or os.getenv('CONFIG_PATH', 'config.ini'))
        self.defaults_path = Path('config.defaults.ini')
        self.parser = ConfigParser()
        
    def load(self):
        if not self.defaults_path.exists():
            raise FileNotFoundError(f"Default config not found: {self.defaults_path}")
        
        self.parser.read(self.defaults_path)
        
        if self.config_path.exists():
            self.parser.read(self.config_path)
            logger.info(f"Loaded user config: {self.config_path}")
        else:
            logger.warning(f"User config not found: {self.config_path}, using defaults only")
        
        try:
            preferences = self._load_preferences()
            twilio = self._load_twilio()
            browser = self._load_browser()
            notifications = self._load_notifications()
            operating_hours = self._load_operating_hours()
            
            logger.info("Configuration loaded successfully")
            return preferences, twilio, browser, notifications, operating_hours
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_preferences(self):
        section = self.parser['preferences']
        
        licence = os.getenv('DVSA_LICENCE_NUMBER')
        booking = os.getenv('DVSA_BOOKING_REFERENCE')
        
        if not licence or not booking:
            raise ValueError(
                "DVSA_LICENCE_NUMBER and DVSA_BOOKING_REFERENCE must be set in .env file"
            )
        
        current_test_date_str = section.get('current_test_date', fallback=None)
        current_test_centre = section.get('current_test_centre', fallback=None)
        
        if not current_test_date_str:
            raise ValueError("current_test_date must be set in config.ini")
        
        current_test_date = datetime.strptime(
            current_test_date_str,
            "%A %d %B %Y %I:%M%p"
        )
        
        search_days_ahead = section.getint('search_days_ahead', fallback=90)
        search_days_after = section.getint('search_days_after', fallback=7)
        
        before_date = (datetime.now() + timedelta(days=search_days_ahead)).date()
        after_date = (datetime.now() + timedelta(days=search_days_after)).date()
        
        disabled_dates_str = section.get('disabled_dates', fallback='')
        disabled_dates = []
        if disabled_dates_str.strip():
            disabled_dates = [
                datetime.strptime(d.strip(), "%Y-%m-%d").date()
                for d in disabled_dates_str.split(',')
                if d.strip()
            ]
        
        preferred_centres_str = section.get('preferred_centres', fallback='')
        if not preferred_centres_str.strip():
            raise ValueError("preferred_centres must be set in config.ini")
        
        preferred_centres = [c.strip() for c in preferred_centres_str.split(',') if c.strip()]
        
        excluded_weekdays_str = section.get('excluded_weekdays', fallback='5,6')
        excluded_weekdays = [
            int(day.strip())
            for day in excluded_weekdays_str.split(',')
            if day.strip()
        ]
        
        return TestPreferences(
            licence=licence,
            booking=booking,
            current_test_date=current_test_date,
            formatted_current_test_date=current_test_date.date(),
            current_test_centre=current_test_centre,
            disabled_dates=disabled_dates,
            preferred_centres=preferred_centres,
            before_date=before_date,
            after_date=after_date,
            excluded_weekdays=excluded_weekdays,
            auto_book_test=section.getboolean('auto_book_test', fallback=False)
        )
    
    def _load_twilio(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        messaging_service_sid = os.getenv('TWILIO_MESSAGING_SERVICE_SID')
        phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, messaging_service_sid, phone_number]):
            logger.warning("Twilio credentials not fully configured, notifications disabled")
            return TwilioConfig(
                account_sid='',
                auth_token='',
                messaging_service_sid='',
                phone_number='',
                enabled=False
            )
        
        return TwilioConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            messaging_service_sid=messaging_service_sid,
            phone_number=phone_number,
            enabled=True
        )
    
    def _load_browser(self):
        section = self.parser['browser']
        return BrowserConfig(
            driver_path=section.get('driver_path', fallback='/bin/chromedriver'),
            run_on_vm=section.getboolean('run_on_vm', fallback=False),
            solve_manually=section.getboolean('solve_manually', fallback=False),
            enable_buster=section.getboolean('enable_buster', fallback=True),
            buster_path=section.get('buster_path', fallback='./buster-chrome.zip'),
            headless=section.getboolean('headless', fallback=False),
            max_retries=section.getint('max_retries', fallback=4),
            retry_delay_seconds=section.getint('retry_delay_seconds', fallback=60)
        )
    
    def _load_notifications(self):
        section = self.parser['notifications']
        return NotificationConfig(
            enable_sms=section.getboolean('enable_sms', fallback=True),
            notify_on_test_found=section.getboolean('notify_on_test_found', fallback=True),
            notify_on_booking_success=section.getboolean('notify_on_booking_success', fallback=True),
            notify_on_error=section.getboolean('notify_on_error', fallback=False)
        )
    
    def _load_operating_hours(self):
        section = self.parser['operating_hours']
        start_time_str = section.get('start_time', fallback='06:05')
        end_time_str = section.get('end_time', fallback='23:35')
        
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        
        return OperatingHours(start_time=start_time, end_time=end_time)
