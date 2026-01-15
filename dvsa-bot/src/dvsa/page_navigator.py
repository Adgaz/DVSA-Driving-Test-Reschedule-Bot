from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import time
import random
from ..security.queue_manager import QueueManager
from ..security.firewall_handler import FirewallHandler
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PageNavigator:
    LOGIN_URL = "https://driverpracticaltest.dvsa.gov.uk/login"
    QUEUE_URL = "https://queue.driverpracticaltest.dvsa.gov.uk/?c=dvsatars&e=ibsredirectprod0915&t=https%3A%2F%2Fdriverpracticaltest.dvsa.gov.uk%2Flogin&cid=en-GB"
    
    def __init__(self, driver: WebDriver, queue_manager: QueueManager, firewall_handler: FirewallHandler):
        self.driver = driver
        self.queue_manager = queue_manager
        self.firewall_handler = firewall_handler
        
    def navigate_to_login(self):
        logger.info("Navigating to DVSA login")
        self.driver.get(self.QUEUE_URL)
        time.sleep(2)
        self.firewall_handler.handle_if_present()
    
    def navigate_to_centre(self, centre_name: str):
        logger.info(f"Navigating to test centre: {centre_name}")
        
        try:
            change_button = self.driver.find_element(By.ID, "test-centre-change")
            change_button.click()
            time.sleep(3)
            
            search_input = self.driver.find_element(By.ID, "test-centres-input")
            search_input.clear()
            self._type_slowly(search_input, centre_name)
            
            submit_button = self.driver.find_element(By.ID, "test-centres-submit")
            submit_button.click()
            time.sleep(5)
            
            self.firewall_handler.handle_if_present()
            
            results = self.driver.find_element(By.CLASS_NAME, "test-centre-results")
            first_result = results.find_element(By.XPATH, ".//a")
            first_result.click()
            time.sleep(3)
            
            self.firewall_handler.handle_if_present()
            
            logger.info(f"Successfully navigated to {centre_name}")
            
        except Exception as e:
            logger.error(f"Failed to navigate to centre: {e}")
            raise
    
    def navigate_to_earliest_test(self):
        logger.info("Navigating to earliest test selection")
        
        try:
            change_button = self.driver.find_element(By.ID, "date-time-change")
            change_button.click()
            time.sleep(2)
            
            earliest_radio = self.driver.find_element(By.ID, "test-choice-earliest")
            earliest_radio.click()
            time.sleep(2)
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            submit_button = self.driver.find_element(By.ID, "driving-licence-submit")
            submit_button.click()
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to navigate to earliest test: {e}")
            raise
    
    def _type_slowly(self, element, text: str):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.01, 0.05))
