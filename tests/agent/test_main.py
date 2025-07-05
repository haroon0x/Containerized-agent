from unittest.mock import patch
import agent.main

def test_main_flow():
    with patch('builtins.input', return_value='What is AI?'), \
         patch('agent.utils.call_llm.call_llm', return_value='Artificial Intelligence.'):
        agent.main.main() 