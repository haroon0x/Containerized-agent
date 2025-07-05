from agent.nodes import GetQuestionNode, AnswerNode
from unittest.mock import patch

def test_get_question_node_exec():
    node = GetQuestionNode()
    with patch('builtins.input', return_value='Test?'):
        result = node.exec(None)
        assert result == 'Test?'

def test_answer_node_exec():
    node = AnswerNode()
    with patch('agent.utils.call_llm.call_llm', return_value='42'):
        result = node.exec('What is the answer?')
        assert result == '42' 