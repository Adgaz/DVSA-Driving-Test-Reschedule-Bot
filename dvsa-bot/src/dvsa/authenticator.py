from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import time
import random
from ..utils.logger import get_logger
from ..security.firewall_handler import FirewallHandler
from ..security.captcha_solver import CaptchaSolver

logger = get_logger(__name__)

class AuthenticationError(Exception):
    pass

class Authenticator:
    def __init__(self, driver: WebDriver, firewall_handler: FirewallHandler, captcha_solver: CaptchaSolver):
        self.driver = driver
        self.firewall_handler = firewall_handler
        self.captcha_solver = captcha_solver
        
    def login(self, licence: str, booking: str):
        logger.info("Starting login process")
        
        try:
            self._enter_credentials(licence, booking)
            self._submit_login()
            
            if self._is_login_successful():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - invalid credentials")
                raise AuthenticationError("Invalid licence or booking reference")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    def _enter_credentials(self, licence: str, booking: str):
        self._type_slowly("driving-licence-number", licence)
        self._type_slowly("application-reference-number", booking)
        time.sleep(random.uniform(1, 2))
    
    def _type_slowly(self, element_id: str, text: str):
        element = self.driver.find_element(By.ID, element_id)
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.01, 0.05))
    
    def _submit_login(self):
        submit_button = self.driver.find_element(By.ID, "booking-login")
        submit_button.click()
        time.sleep(random.uniform(3, 4))
    
    def _is_login_successful(self):
        return "loginError=true" not in self.driver.current_url
