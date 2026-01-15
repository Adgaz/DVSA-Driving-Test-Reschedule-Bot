from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import time
import random
from typing import Optional
from .calendar_scanner import TestSlot
from ..security.captcha_solver import CaptchaSolver
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BookingError(Exception):
    pass

class BookingHandler:
    def __init__(self, driver: WebDriver, captcha_solver: CaptchaSolver):
        self.driver = driver
        self.captcha_solver = captcha_solver
        
    def book_slot(self, slot: TestSlot, auto_confirm: bool = False):
        logger.info(f"Attempting to book: {slot}")
        
        try:
            self._select_slot(slot)
            self._submit_slot_choice()
            self._handle_warnings(slot.short_notice)
            
            if auto_confirm:
                return self._confirm_booking_auto()
            else:
                return self._confirm_booking_manual()
                
        except Exception as e:
            logger.error(f"Booking failed: {e}")
            raise BookingError(f"Failed to book slot: {e}")
    
    def _select_slot(self, slot: TestSlot):
        slot.element.click()
        time.sleep(0.2)
    
    def _submit_slot_choice(self):
        submit_button = self.driver.find_element(By.ID, "slot-chosen-submit")
        submit_button.click()
        time.sleep(0.5)
    
    def _handle_warnings(self, is_short_notice: bool):
        if is_short_notice:
            warning_button = self.driver.find_element(By.XPATH, "(//button[@id='slot-warning-continue'])[2]")
        else:
            warning_button = self.driver.find_element(By.ID, "slot-warning-continue")
        
        warning_button.click()
        time.sleep(random.uniform(1, 2))
    
    def _confirm_booking_auto(self):
        attempts = 0
        max_attempts = 4
        
        while attempts < max_attempts:
            logger.info(f"Booking confirmation attempt {attempts + 1}/{max_attempts}")
            
            try:
                candidate_button = self.driver.find_element(By.ID, "i-am-candidate")
                candidate_button.click()
                
                if self._check_slot_taken():
                    logger.warning("Slot was taken by another user")
                    return False
                
                if self._needs_captcha():
                    logger.info("Captcha required for booking")
                    if not self.captcha_solver.solve():
                        attempts += 1
                        continue
                
                if self._is_booking_confirmed():
                    logger.info("Booking confirmed successfully")
                    return True
                    
            except Exception as e:
                logger.warning(f"Booking attempt {attempts + 1} failed: {e}")
            
            attempts += 1
            time.sleep(2)
        
        logger.error("All booking attempts exhausted")
        return False
    
    def _confirm_booking_manual(self):
        logger.info("Manual booking confirmation required")
        logger.info("Please complete the booking manually...")
        time.sleep(60)
        return True
    
    def _check_slot_taken(self):
        return "The time chosen is no longer available" in self.driver.page_source
    
    def _needs_captcha(self):
        try:
            self.driver.find_element(By.ID, "main-iframe")
            return True
        except:
            return False
    
    def _is_booking_confirmed(self):
        return "Your test has been booked" in self.driver.page_source or "contents" in self.driver.page_source
