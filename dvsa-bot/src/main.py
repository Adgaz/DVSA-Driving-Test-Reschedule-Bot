import sys
from pathlib import Path
from datetime import datetime
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
        self.preferences, self.twilio_config, self.browser_config, self.notification_config, self.operating_hours = config_loader.load()
        
        self.browser_manager = BrowserManager(self.browser_config)
        self.state_machine = StateMachine()
        
        if self.twilio_config.enabled and self.notification_config.enable_sms:
            self.notifier = TwilioNotifier(self.twilio_config, self.notification_config)
        else:
            self.notifier = None
            logger.info("SMS notifications disabled")
        
        self.driver = None
        
    def run(self):
        if not self.operating_hours.is_operating(datetime.now().time()):
            logger.info(f"Outside operating hours ({self.operating_hours.start_time} - {self.operating_hours.end_time})")
            return
        
        for attempt in range(self.browser_config.max_retries):
            logger.info("-" * 100)
            logger.info(f"Attempt {attempt + 1}/{self.browser_config.max_retries}")
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
                
                if self.notifier and self.notification_config.notify_on_error:
                    self.notifier.notify_error(str(e))
            
            finally:
                if attempt < self.browser_config.max_retries - 1:
                    logger.info(f"Waiting {self.browser_config.retry_delay_seconds}s before next attempt...")
                    time.sleep(self.browser_config.retry_delay_seconds)
        
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
            self.preferences.formatted_current_test_date,
            self.preferences.excluded_weekdays
        )
        
        if slot:
            self.state_machine.transition_to(BotState.TEST_FOUND, f"Found slot: {slot}")
            
            if self.notifier and self.notification_config.notify_on_test_found:
                self.notifier.notify_test_found(slot)
            
            if self.preferences.auto_book_test:
                self.state_machine.transition_to(BotState.BOOKING, "Auto-booking enabled")
                
                if booking_handler.book_slot(slot, auto_confirm=True):
                    self.state_machine.transition_to(BotState.BOOKING_CONFIRMED, "Booking successful")
                    
                    if self.notifier and self.notification_config.notify_on_booking_success:
                        self.notifier.notify_booking_success(slot)
                else:
                    raise Exception("Booking failed")
            else:
                logger.info("Auto-booking disabled, manual action required")
        else:
            logger.info("No suitable slots found")
    
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
