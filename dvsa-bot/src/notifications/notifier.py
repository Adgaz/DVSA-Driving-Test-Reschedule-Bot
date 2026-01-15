from abc import ABC, abstractmethod
from typing import Optional
from ..dvsa.calendar_scanner import TestSlot

class Notifier(ABC):
    @abstractmethod
    def notify_test_available(self, date: str, time: str):
        pass
    
    @abstractmethod
    def notify_test_found(self, slot: TestSlot):
        pass
    
    @abstractmethod
    def notify_booking_success(self, slot: TestSlot):
        pass
    
    @abstractmethod
    def notify_booking_failure(self, slot: TestSlot, reason: str):
        pass
    
    @abstractmethod
    def notify_error(self, error_message: str):
        pass
