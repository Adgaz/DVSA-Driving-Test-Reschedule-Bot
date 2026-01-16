from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List

@dataclass
class TestPreferences:
    licence: str
    booking: str
    current_test_date: datetime
    formatted_current_test_date: date
    current_test_centre: str
    disabled_dates: List[date]
    preferred_centres: List[str]
    before_date: date
    after_date: date
    excluded_weekdays: List[int]
    auto_book_test: bool
    
    def __post_init__(self):
        self._validate_licence()
        self._validate_dates()
        self._validate_centres()
    
    def _validate_licence(self):
        if not self.licence or len(self.licence) != 16:
            raise ValueError("Invalid licence number format (must be 16 characters)")
    
    def _validate_dates(self):
        if self.after_date >= self.before_date:
            raise ValueError("before_date must be after after_date")
    
    def _validate_centres(self):
        if not self.preferred_centres:
            raise ValueError("At least one preferred centre must be specified")

@dataclass
class TwilioConfig:
    account_sid: str
    auth_token: str
    messaging_service_sid: str
    phone_number: str
    enabled: bool = True
    
    def __post_init__(self):
        if self.enabled and self.phone_number and not self.phone_number.startswith('+'):
            raise ValueError("Phone number must include country code with +")

@dataclass
class BrowserConfig:
    driver_path: str
    run_on_vm: bool
    solve_manually: bool
    enable_buster: bool
    buster_path: str
    headless: bool
    max_retries: int
    retry_delay_seconds: int

@dataclass
class NotificationConfig:
    enable_sms: bool
    notify_on_test_found: bool
    notify_on_booking_success: bool
    notify_on_error: bool

@dataclass
class OperatingHours:
    start_time: time
    end_time: time
    
    def is_operating(self, current_time: time) -> bool:
        return self.start_time <= current_time <= self.end_time
