from pocketflow import Flow
from src.agent.nodes import TaskAnalysisNode, ShellCommandNode, PythonCodeNode, ResultCompilationNode

def create_qa_flow() -> Flow:
    """Create and return a task execution flow for containerized agent."""
    task_analysis = TaskAnalysisNode()
    shell_command = ShellCommandNode()
    python_code = PythonCodeNode()
    result_compilation = ResultCompilationNode()
    
    # Create the flow: analyze task -> execute shell commands -> execute Python code -> compile results
    task_analysis >> shell_command >> python_code >> result_compilation
    return Flow(start=task_analysis)

qa_flow = create_qa_flow()