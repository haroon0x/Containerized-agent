from pocketflow import Flow
from src.agent.nodes import TaskAnalysisNode, ShellCommandNode, PythonCodeNode, FileOperationNode, ResultCompilationNode

def create_qa_flow() -> Flow:
    task_analysis = TaskAnalysisNode()
    shell_command = ShellCommandNode()
    file_operation = FileOperationNode()
    python_code = PythonCodeNode()
    result_compilation = ResultCompilationNode()
    
    task_analysis >> shell_command >> file_operation >> python_code >> result_compilation
    return Flow(start=task_analysis)

qa_flow = create_qa_flow()