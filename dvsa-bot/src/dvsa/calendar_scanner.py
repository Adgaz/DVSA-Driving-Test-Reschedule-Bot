from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime, date
from typing import Optional, List
import time
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TestSlot:
    def __init__(self, date: date, time: str, element: WebElement, short_notice: bool = False):
        self.date = date
        self.time = time
        self.element = element
        self.short_notice = short_notice
    
    def __str__(self):
        return f"TestSlot(date={self.date}, time={self.time}, short_notice={self.short_notice})"

class CalendarScanner:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
    def find_earliest_slot(self, before_date: date, after_date: date, disabled_dates: List[date], current_test_date: date, excluded_weekdays: List[int] = None):
        if excluded_weekdays is None:
            excluded_weekdays = [5, 6]
        
        logger.info(f"Scanning calendar: after={after_date}, before={before_date}, excluded_weekdays={excluded_weekdays}")
        
        try:
            calendar_body = self.driver.find_element(By.CLASS_NAME, "BookingCalendar-datesBody")
            available_days = calendar_body.find_elements(By.XPATH, ".//td")
            
            for day_element in available_days:
                if "--unavailable" in day_element.get_attribute("class"):
                    continue
                
                day_link = day_element.find_element(By.XPATH, ".//a")
                slot_date_str = day_link.get_attribute("data-date")
                slot_date = datetime.strptime(slot_date_str, "%Y-%m-%d").date()
                
                if self._is_valid_slot(slot_date, before_date, after_date, disabled_dates, current_test_date, excluded_weekdays):
                    return self._extract_slot_details(day_link, slot_date)
            
            logger.info("No suitable slots found")
            return None
            
        except Exception as e:
            logger.error(f"Error scanning calendar: {e}")
            raise
    
    def _is_valid_slot(self, slot_date: date, before_date: date, after_date: date, disabled_dates: List[date], current_test_date: date, excluded_weekdays: List[int]):
        if slot_date in disabled_dates:
            logger.debug(f"Skipping {slot_date}: in disabled_dates")
            return False
        if slot_date >= current_test_date:
            logger.debug(f"Skipping {slot_date}: not before current test date")
            return False
        if slot_date >= before_date:
            logger.debug(f"Skipping {slot_date}: not before search limit")
            return False
        if slot_date <= after_date:
            logger.debug(f"Skipping {slot_date}: not after search start")
            return False
        if slot_date.weekday() in excluded_weekdays:
            logger.debug(f"Skipping {slot_date}: weekday {slot_date.weekday()} excluded")
            return False
        return True
    
    def _extract_slot_details(self, day_link: WebElement, slot_date: date):
        try:
            day_link.click()
            time.sleep(0.5)
            
            date_str = slot_date.strftime("%Y-%m-%d")
            time_container = self.driver.find_element(By.ID, f"date-{date_str}")
            
            label = time_container.find_element(By.XPATH, ".//label")
            slot_id = label.get_attribute('for')
            
            time_timestamp = int(slot_id.replace("slot-", "")) / 1000
            slot_time = datetime.fromtimestamp(time_timestamp).strftime("%H:%M")
            
            slot_element = time_container.find_element(By.ID, slot_id)
            short_notice = slot_element.get_attribute('data-short-notice') == 'true'
            
            logger.info(f"Found slot: {slot_date} at {slot_time}, short_notice={short_notice}")
            
            return TestSlot(slot_date, slot_time, label, short_notice)
            
        except Exception as e:
            logger.error(f"Error extracting slot details: {e}")
            return None
