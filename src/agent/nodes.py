import logging
from typing import Any, Dict
from pocketflow import Node
from agent.utils.call_llm import call_llm

class GetQuestionNode(Node):
    def exec(self, _: Any) -> str:
        """Get question directly from user input."""
        user_question = input("Enter your question: ")
        logging.info(f"User question: {user_question}")
        return user_question
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: str) -> str:
        """Store the user's question in shared."""
        shared["question"] = exec_res
        return "default"

class AnswerNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        """Read question from shared."""
        return shared["question"]
    
    def exec(self, question: str) -> str:
        """Call LLM to get the answer."""
        answer = call_llm(question)
        logging.info(f"LLM answer: {answer}")
        return answer
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: str) -> None:
        """Store the answer in shared."""
        shared["answer"] = exec_res