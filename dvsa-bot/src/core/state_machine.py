from enum import Enum, auto
from typing import Optional, Callable
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BotState(Enum):
    INITIALIZED = auto()
    CONNECTING = auto()
    IN_QUEUE = auto()
    SOLVING_CAPTCHA = auto()
    AUTHENTICATING = auto()
    AUTHENTICATED = auto()
    NAVIGATING_TO_CENTRE = auto()
    MONITORING = auto()
    TEST_FOUND = auto()
    BOOKING = auto()
    BOOKING_CONFIRMED = auto()
    ERROR = auto()
    STOPPED = auto()

class StateTransitionError(Exception):
    pass

class StateMachine:
    VALID_TRANSITIONS = {
        BotState.INITIALIZED: [BotState.CONNECTING, BotState.STOPPED],
        BotState.CONNECTING: [BotState.IN_QUEUE, BotState.SOLVING_CAPTCHA, BotState.AUTHENTICATING, BotState.ERROR],
        BotState.IN_QUEUE: [BotState.SOLVING_CAPTCHA, BotState.AUTHENTICATING, BotState.ERROR],
        BotState.SOLVING_CAPTCHA: [BotState.AUTHENTICATING, BotState.ERROR, BotState.IN_QUEUE],
        BotState.AUTHENTICATING: [BotState.AUTHENTICATED, BotState.ERROR, BotState.SOLVING_CAPTCHA],
        BotState.AUTHENTICATED: [BotState.NAVIGATING_TO_CENTRE, BotState.ERROR],
        BotState.NAVIGATING_TO_CENTRE: [BotState.MONITORING, BotState.ERROR, BotState.SOLVING_CAPTCHA],
        BotState.MONITORING: [BotState.TEST_FOUND, BotState.ERROR, BotState.MONITORING],
        BotState.TEST_FOUND: [BotState.BOOKING, BotState.MONITORING, BotState.ERROR],
        BotState.BOOKING: [BotState.BOOKING_CONFIRMED, BotState.ERROR, BotState.SOLVING_CAPTCHA],
        BotState.BOOKING_CONFIRMED: [BotState.STOPPED],
        BotState.ERROR: [BotState.CONNECTING, BotState.STOPPED],
        BotState.STOPPED: []
    }
    
    def __init__(self, initial_state: BotState = BotState.INITIALIZED):
        self.current_state = initial_state
        self.state_history = [initial_state]
        self.state_callbacks = {}
        
    def transition_to(self, new_state: BotState, reason: str = ""):
        if new_state not in self.VALID_TRANSITIONS[self.current_state]:
            error_msg = f"Invalid transition: {self.current_state} -> {new_state}"
            logger.error(error_msg)
            raise StateTransitionError(error_msg)
        
        old_state = self.current_state
        self.current_state = new_state
        self.state_history.append(new_state)
        
        logger.info(f"State transition: {old_state} -> {new_state}. Reason: {reason}")
        
        if new_state in self.state_callbacks:
            self.state_callbacks[new_state]()
        
        return True
    
    def register_callback(self, state: BotState, callback: Callable):
        self.state_callbacks[state] = callback
    
    def is_in_state(self, state: BotState):
        return self.current_state == state
    
    def can_transition_to(self, state: BotState):
        return state in self.VALID_TRANSITIONS[self.current_state]
