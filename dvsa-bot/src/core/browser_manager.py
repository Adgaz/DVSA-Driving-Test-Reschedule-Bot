import undetected_chromedriver as uc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
from typing import Optional
from ..config.settings import BrowserConfig
from ..utils.logger import get_logger
import time

logger = get_logger(__name__)

class BrowserManager:
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.driver: Optional[WebDriver] = None
        self.wait: Optional[WebDriverWait] = None
        
    def initialize(self):
        logger.info("Initializing Chrome driver")
        
        options = self._build_chrome_options()
        
        try:
            self.driver = uc.Chrome(
                executable_path=self.config.driver_path,
                options=options
            )
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("Chrome driver initialized successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def _build_chrome_options(self):
        options = uc.ChromeOptions()
        
        if not self.config.solve_manually:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        if self.config.run_on_vm:
            options.add_argument("--disable-gpu")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/92.0.4515.131 Safari/537.36"
            )
            options.add_argument("window-size=1400,900")
        
        if self.config.headless:
            options.add_argument("--headless")
        
        if self.config.enable_buster and Path(self.config.buster_path).exists():
            options.add_extension(self.config.buster_path)
            logger.info("Buster extension loaded")
        
        return options
    
    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
    
    def take_screenshot(self, filename: str):
        if self.driver:
            try:
                screenshot_path = Path("error_screenshots") / filename
                screenshot_path.parent.mkdir(exist_ok=True)
                self.driver.save_screenshot(str(screenshot_path))
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to save screenshot: {e}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
