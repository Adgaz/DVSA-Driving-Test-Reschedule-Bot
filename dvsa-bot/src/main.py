import sys
from pathlib import Path
from datetime import datetime, time as time_obj
import time
from .config.config_loader import ConfigLoader
from .core.browser_manager import BrowserManager
from .core.state_machine import StateMachine, BotState
from .dvsa.authenticator import Authenticator
from .dvsa.calendar_scanner import CalendarScanner
from .dvsa.booking_handler import BookingHandler
from .dvsa.page_navigator import PageNavigator
from .security.captcha_solver import CaptchaSolver
from .security.firewall_handler import FirewallHandler
from .security.queue_manager import QueueManager
from .notifications.twilio_notifier import TwilioNotifier
from .utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

class DVSABot:
    def __init__(self):
        setup_logging()
        logger.info("=" * 100)
        logger.info("DVSA Bot Starting")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 100)
        
        config_loader = ConfigLoader()
        self.preferences, self.twilio_config, self.browser_config = config_loader.load()
        
        self.browser_manager = BrowserManager(self.browser_config)
        self.state_machine = StateMachine()
        self.notifier = TwilioNotifier(self.twilio_config)
        
        self.driver = None
        self.max_attempts = 4
        
    def run(self):
        if not self._is_operating_hours():
            logger.info("Outside operating hours (6:05 AM - 11:35 PM)")
            return
        
        for attempt in range(self.max_attempts):
            logger.info("-" * 100)
            logger.info(f"Attempt {attempt + 1}/{self.max_attempts}")
            logger.info("-" * 100)
            
            try:
                self._run_single_attempt()
                
                if self.state_machine.is_in_state(BotState.BOOKING_CONFIRMED):
                    logger.info("Booking successful, exiting")
                    break
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}", exc_info=True)
                self.state_machine.transition_to(BotState.ERROR, str(e))
                self._take_error_screenshot(attempt)
            
            finally:
                if attempt < self.max_attempts - 1:
                    logger.info("Waiting before next attempt...")
                    time.sleep(60)
        
        self._cleanup()
    
    def _run_single_attempt(self):
        self.driver = self.browser_manager.initialize()
        self.state_machine.transition_to(BotState.CONNECTING, "Browser initialized")
        
        captcha_solver = CaptchaSolver(self.driver, self.browser_config.solve_manually)
        firewall_handler = FirewallHandler(self.driver, captcha_solver)
        queue_manager = QueueManager(self.driver)
        authenticator = Authenticator(self.driver, firewall_handler, captcha_solver)
        navigator = PageNavigator(self.driver, queue_manager, firewall_handler)
        scanner = CalendarScanner(self.driver)
        booking_handler = BookingHandler(self.driver, captcha_solver)
        
        navigator.navigate_to_login()
        
        if queue_manager.wait_in_queue():
            self.state_machine.transition_to(BotState.AUTHENTICATING, "Queue cleared")
        else:
            raise Exception("Queue timeout")
        
        if authenticator.login(self.preferences.licence, self.preferences.booking):
            self.state_machine.transition_to(BotState.AUTHENTICATED, "Login successful")
        else:
            raise Exception("Authentication failed")
        
        navigator.navigate_to_centre(self.preferences.preferred_centres[0])
        self.state_machine.transition_to(BotState.MONITORING, "At test centre calendar")
        
        slot = scanner.find_earliest_slot(
            self.preferences.before_date,
            self.preferences.after_date,
            self.preferences.disabled_dates,
            self.preferences.formatted_current_test_date
        )
        
        if slot:
            self.state_machine.transition_to(BotState.TEST_FOUND, f"Found slot: {slot}")
            self.notifier.notify_test_found(slot)
            
            if self.preferences.auto_book_test:
                self.state_machine.transition_to(BotState.BOOKING, "Auto-booking enabled")
                
                if booking_handler.book_slot(slot, auto_confirm=True):
                    self.state_machine.transition_to(BotState.BOOKING_CONFIRMED, "Booking successful")
                    self.notifier.notify_booking_success(slot)
                else:
                    raise Exception("Booking failed")
            else:
                logger.info("Auto-booking disabled, manual action required")
        else:
            logger.info("No suitable slots found")
    
    def _is_operating_hours(self):
        current_time = datetime.now().time()
        start_time = time_obj(6, 5)
        end_time = time_obj(23, 35)
        
        return start_time <= current_time <= end_time
    
    def _take_error_screenshot(self, attempt: int):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"error_attempt_{attempt}_{timestamp}.png"
        self.browser_manager.take_screenshot(filename)
    
    def _cleanup(self):
        logger.info("Cleaning up resources")
        self.browser_manager.quit()
        logger.info("=" * 100)
        logger.info("DVSA Bot Stopped")
        logger.info("=" * 100)

def main():
    try:
        bot = DVSABot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
