import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.state_machine import StateMachine, BotState, StateTransitionError

class TestStateMachine:
    def test_initial_state(self):
        sm = StateMachine()
        assert sm.is_in_state(BotState.INITIALIZED)
    
    def test_valid_transition(self):
        sm = StateMachine()
        assert sm.transition_to(BotState.CONNECTING, "test") == True
        assert sm.is_in_state(BotState.CONNECTING)
    
    def test_invalid_transition(self):
        sm = StateMachine()
        with pytest.raises(StateTransitionError):
            sm.transition_to(BotState.BOOKING_CONFIRMED, "invalid")
    
    def test_state_history(self):
        sm = StateMachine()
        sm.transition_to(BotState.CONNECTING)
        sm.transition_to(BotState.AUTHENTICATING)
        
        assert len(sm.state_history) == 3
        assert sm.state_history[-1] == BotState.AUTHENTICATING
