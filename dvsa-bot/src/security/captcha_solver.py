from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import time
import random
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CaptchaSolver:
    def __init__(self, driver: WebDriver, manual_mode: bool = False):
        self.driver = driver
        self.manual_mode = manual_mode
        
    def solve(self):
        if self.manual_mode:
            return self._solve_manually()
        else:
            return self._solve_with_buster()
    
    def _solve_with_buster(self):
        logger.info("Attempting automated captcha solution with Buster")
        
        try:
            self.driver.switch_to.default_content()
            main_iframe = self.driver.find_element(By.ID, "main-iframe")
            self.driver.switch_to.frame(main_iframe)
            
            anchor_iframe = self.driver.find_element(
                By.CSS_SELECTOR,
                "iframe[name*='a-'][src*='https://www.google.com/recaptcha/api2/anchor?']"
            )
            self.driver.switch_to.frame(anchor_iframe)
            
            time.sleep(0.2)
            checkbox = self.driver.find_element(By.XPATH, "//span[@id='recaptcha-anchor']")
            checkbox.click()
            
            self.driver.switch_to.default_content()
            time.sleep(0.2)
            
            main_iframe = self.driver.find_element(By.ID, "main-iframe")
            self.driver.switch_to.frame(main_iframe)
            
            if "Why am I seeing this page" in self.driver.page_source:
                logger.info("Challenge detected, triggering Buster")
                time.sleep(2)
                
                challenge_iframe = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "iframe[title*='recaptcha challenge'][src*='https://www.google.com/recaptcha/api2/bframe?']"
                )
                self.driver.switch_to.frame(challenge_iframe)
                
                time.sleep(2)
                help_button = self.driver.find_elements(By.CLASS_NAME, "help-button-holder")[0]
                help_button.click()
                
                time.sleep(random.uniform(5, 9))
                
                attempts = 0
                while "Multiple correct solutions required" in self.driver.page_source and attempts < 4:
                    attempts += 1
                    help_button.click()
                    time.sleep(random.uniform(5, 9))
                
                self.driver.switch_to.default_content()
                logger.info("Captcha solution completed")
            
            if "Why am I seeing this page" not in self.driver.page_source:
                logger.info("Captcha solved successfully")
                return True
            else:
                logger.warning("Captcha solution failed")
                return False
                
        except Exception as e:
            logger.error(f"Captcha solver error: {e}")
            return False
    
    def _solve_manually(self):
        logger.info("Manual captcha solving mode - waiting 60 seconds")
        time.sleep(60)
        return True
