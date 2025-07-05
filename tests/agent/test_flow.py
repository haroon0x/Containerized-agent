from src.agent.flow import create_qa_flow
from pocketflow import Flow

def test_create_qa_flow():
    flow = create_qa_flow()
    assert isinstance(flow, Flow)
    assert hasattr(flow, 'start') 