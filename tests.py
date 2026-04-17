import pytest
from main import CodingAIAgent

class TestCodingAIAgent:
    def setup_method(self):
        self.agent = CodingAIAgent()
    
    def test_agent_initialization(self):
        assert self.agent is not None
        assert self.agent.model == "claude-3-5-sonnet-20241022"
        assert self.agent.conversation_history == []
    
    def test_reset_conversation(self):
        self.agent.conversation_history = [{"role": "user", "content": "test"}]
        self.agent.reset_conversation()
        assert self.agent.conversation_history == []
    
    def test_methods_exist(self):
        assert hasattr(self.agent, 'analyze_code')
        assert hasattr(self.agent, 'debug_error')
        assert hasattr(self.agent, 'solve_algorithm')
        assert hasattr(self.agent, 'review_code')
        assert hasattr(self.agent, 'chat')
