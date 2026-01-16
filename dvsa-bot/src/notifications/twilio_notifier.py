from twilio.rest import Client
from .notifier import Notifier
from ..dvsa.calendar_scanner import TestSlot
from ..config.settings import TwilioConfig, NotificationConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TwilioNotifier(Notifier):
    def __init__(self, twilio_config: TwilioConfig, notification_config: NotificationConfig):
        self.twilio_config = twilio_config
        self.notification_config = notification_config
        
        if twilio_config.enabled:
            self.client = Client(twilio_config.account_sid, twilio_config.auth_token)
        else:
            self.client = None
        
    def notify_test_available(self, date: str, time: str):
        if not self._should_notify():
            return
        
        message = f"Tests are available on {date} at {time}."
        self._send_sms(message)
    
    def notify_test_found(self, slot: TestSlot):
        if not self._should_notify() or not self.notification_config.notify_on_test_found:
            return
        
        short_notice_text = " (Short Notice)" if slot.short_notice else ""
        message = (
            f"Test found!\n"
            f"Date: {slot.date}\n"
            f"Time: {slot.time}{short_notice_text}"
        )
        self._send_sms(message)
    
    def notify_booking_success(self, slot: TestSlot):
        if not self._should_notify() or not self.notification_config.notify_on_booking_success:
            return
        
        message = (
            f"Booking confirmed!\n"
            f"Date: {slot.date}\n"
            f"Time: {slot.time}\n"
            f"Don't forget to prepare!"
        )
        self._send_sms(message)
    
    def notify_booking_failure(self, slot: TestSlot, reason: str):
        if not self._should_notify():
            return
        
        message = (
            f"Booking failed\n"
            f"Slot: {slot.date} at {slot.time}\n"
            f"Reason: {reason}"
        )
        self._send_sms(message)
    
    def notify_error(self, error_message: str):
        if not self._should_notify() or not self.notification_config.notify_on_error:
            return
        
        message = f"Bot error: {error_message}"
        self._send_sms(message)
    
    def _should_notify(self):
        return self.twilio_config.enabled and self.notification_config.enable_sms and self.client is not None
    
    def _send_sms(self, message: str):
        if not self.client:
            logger.warning("SMS client not initialized, skipping notification")
            return
        
        try:
            self.client.messages.create(
                messaging_service_sid=self.twilio_config.messaging_service_sid,
                body=message,
                to=self.twilio_config.phone_number
            )
            logger.info(f"SMS sent: {message[:50]}...")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
