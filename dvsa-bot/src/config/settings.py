from dataclasses import dataclass
from datetime import date, datetime
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
    auto_book_test: bool
    
    def __post_init__(self):
        self._validate_licence()
        self._validate_dates()
    
    def _validate_licence(self):
        if not self.licence or len(self.licence) != 16:
            raise ValueError("Invalid licence number format")
    
    def _validate_dates(self):
        if self.after_date >= self.before_date:
            raise ValueError("before_date must be after after_date")

@dataclass
class TwilioConfig:
    account_sid: str
    auth_token: str
    messaging_service_sid: str
    phone_number: str
    
    def __post_init__(self):
        if not self.phone_number.startswith('+'):
            raise ValueError("Phone number must include country code with +")

@dataclass
class BrowserConfig:
    driver_path: str
    run_on_vm: bool
    solve_manually: bool
    enable_buster: bool
    buster_path: str
    headless: bool = False
