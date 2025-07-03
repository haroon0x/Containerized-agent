from pocketflow import Flow
from nodes import GetQuestionNode, AnswerNode

def create_qa_flow():
    """Create and return a question-answering flow."""
   
    get_question_node = GetQuestionNode()
    answer_node = AnswerNode()

    get_question_node >> answer_node
    return Flow(start=get_question_node)

qa_flow = create_qa_flow()