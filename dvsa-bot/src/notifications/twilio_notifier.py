from twilio.rest import Client
from .notifier import Notifier
from ..dvsa.calendar_scanner import TestSlot
from ..config.settings import TwilioConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TwilioNotifier(Notifier):
    def __init__(self, config: TwilioConfig):
        self.config = config
        self.client = Client(config.account_sid, config.auth_token)
        
    def notify_test_available(self, date: str, time: str):
        message = f"Tests are available on {date} at {time}."
        self._send_sms(message)
    
    def notify_test_found(self, slot: TestSlot):
        short_notice_text = " (Short Notice)" if slot.short_notice else ""
        message = (
            f"Test found!\n"
            f"Date: {slot.date}\n"
            f"Time: {slot.time}{short_notice_text}"
        )
        self._send_sms(message)
    
    def notify_booking_success(self, slot: TestSlot):
        message = (
            f"Booking confirmed!\n"
            f"Date: {slot.date}\n"
            f"Time: {slot.time}\n"
            f"Don't forget to prepare!"
        )
        self._send_sms(message)
    
    def notify_booking_failure(self, slot: TestSlot, reason: str):
        message = (
            f"Booking failed\n"
            f"Slot: {slot.date} at {slot.time}\n"
            f"Reason: {reason}"
        )
        self._send_sms(message)
    
    def notify_error(self, error_message: str):
        message = f"Bot error: {error_message}"
        self._send_sms(message)
    
    def _send_sms(self, message: str):
        try:
            self.client.messages.create(
                messaging_service_sid=self.config.messaging_service_sid,
                body=message,
                to=self.config.phone_number
            )
            logger.info(f"SMS sent: {message[:50]}...")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
