from selenium.webdriver.remote.webdriver import WebDriver
import time
import random
from ..security.captcha_solver import CaptchaSolver
from ..utils.logger import get_logger

logger = get_logger(__name__)

class FirewallHandler:
    FIREWALL_INDICATOR = "Request unsuccessful. Incapsula incident ID"
    
    def __init__(self, driver: WebDriver, captcha_solver: CaptchaSolver):
        self.driver = driver
        self.captcha_solver = captcha_solver
        
    def is_firewall_active(self):
        return self.FIREWALL_INDICATOR in self.driver.page_source
    
    def handle_if_present(self):
        if not self.is_firewall_active():
            logger.debug("No firewall detected")
            return True
        
        logger.warning("Firewall detected, attempting bypass")
        return self._bypass_firewall()
    
    def _bypass_firewall(self):
        time.sleep(random.uniform(4, 10))
        
        self.driver.refresh()
        time.sleep(2)
        
        if self.is_firewall_active():
            logger.info("Firewall still active, attempting captcha solution")
            
            if self.captcha_solver.solve():
                time.sleep(4)
                
                if not self.is_firewall_active():
                    logger.info("Firewall bypassed successfully")
                    return True
                else:
                    logger.warning("Firewall still active after captcha, applying long delay")
                    time.sleep(random.uniform(180, 200))
                    return False
            else:
                logger.error("Captcha solution failed")
                return False
        else:
            logger.info("Firewall bypassed after refresh")
            return True
