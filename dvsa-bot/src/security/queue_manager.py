from selenium.webdriver.remote.webdriver import WebDriver
import time
from ..utils.logger import get_logger

logger = get_logger(__name__)

class QueueManager:
    QUEUE_URL = "queue.driverpracticaltest.dvsa.gov.uk"
    MAX_WAIT_ITERATIONS = 100
    CHECK_INTERVAL = 2
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
    def wait_in_queue(self):
        if self.QUEUE_URL not in self.driver.current_url:
            logger.info("Not in queue")
            return True
        
        logger.info("Entered queue, waiting...")
        iterations = 0
        
        while iterations < self.MAX_WAIT_ITERATIONS:
            if self.QUEUE_URL not in self.driver.current_url:
                logger.info(f"Queue cleared after {iterations * self.CHECK_INTERVAL} seconds")
                return True
            
            iterations += 1
            time.sleep(self.CHECK_INTERVAL)
        
        logger.warning("Queue timeout reached")
        return False
