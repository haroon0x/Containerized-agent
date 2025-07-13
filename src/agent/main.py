import os
import logging
from src.agent.agent_runtime import AgentRuntime

def main():
    logging.basicConfig(level=logging.INFO)
    task = os.getenv("JOB_PROMPT", "echo 'Hello from agent'" )
    job_id = os.getenv("JOB_ID", "unknown")
    logging.info(f"Agent main started for job {job_id}")
    AgentRuntime(task, job_id).run()

if __name__ == "__main__":
    test_tasks = [
        {
            "name": "Basic Shell Command Test",
            "task": "echo 'Hello World' and show the current directory with pwd command",
            "job_id": "test_shell_001"
        },
        {
            "name": "File Creation Test",
            "task": "create a Python file called hello.py with a function that prints 'Hello from Python' and then execute it",
            "job_id": "test_file_001"
        },
        {
            "name": "Python Code Execution Test",
            "task": "write Python code to calculate the sum of numbers from 1 to 10 and print the result, also show the Python version",
            "job_id": "test_python_001"
        },
        {
            "name": "Complex File Operation Test",
            "task": "create a directory called 'test_data' and inside it create a file called 'data.txt' with sample data 'Hello World\nThis is test data\nLine 3', then create a Python script that reads this file and prints its contents line by line",
            "job_id": "test_complex_001"
        },
        {
            "name": "System Information Test",
            "task": "show system information including Python version with 'python --version', current working directory with 'pwd', and list files in the current directory with 'ls -la'",
            "job_id": "test_system_001"
        },
        {
            "name": "Data Processing Test",
            "task": "create a Python script that generates a list of 5 random numbers between 1 and 100, saves them to a file called 'numbers.txt' (one number per line), then reads the file and calculates the average of the numbers",
            "job_id": "test_data_001"
        },
        {
            "name": "Web Scraping Simulation Test",
            "task": "create a Python script that simulates web scraping by creating a mock HTML file with some data, then extract and display the information",
            "job_id": "test_web_001"
        },
        {
            "name": "Multi-step Workflow Test",
            "task": "create a workflow that: 1) creates a config file with settings, 2) generates sample data, 3) processes the data, 4) creates a summary report",
            "job_id": "test_workflow_001"
        }
    ]
    
    print("=== Agent Container Test Suite ===")
    print("Testing agent functionality with various tasks...")
    print()
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test in enumerate(test_tasks, 1):
        print(f"Running test {i}/{len(test_tasks)}: {test['name']}")
        print(f"Task: {test['task']}")
        print("-" * 60)
        
        try:
            result = AgentRuntime(test['task'], test['job_id']).run()
            
            if result.get('status') == 'completed':
                print(f"✅ Test PASSED: {test['name']}")
                passed_tests += 1
                
                created_files = result.get('created_files', [])
                shell_results = result.get('shell_results', [])
                python_results = result.get('python_results', [])
                file_results = result.get('file_results', [])
                
                if created_files:
                    print(f"   📁 Created files: {len(created_files)}")
                    for file_info in created_files:
                        print(f"      - {file_info['filename']} ({file_info['size']} bytes)")
                
                if shell_results:
                    print(f"   🖥️  Shell results: {len(shell_results)}")
                    for shell_result in shell_results:
                        if shell_result.get('success'):
                            print(f"      ✅ {shell_result.get('command', 'Unknown command')}")
                        else:
                            err = shell_result.get('error', 'Unknown error')
                            cmd = shell_result.get('command', 'Unknown command')
                            if 'not recognized as an internal or external command' in err:
                                print(f"      ⚠️  {cmd}: Not available on this platform")
                            else:
                                print(f"      ❌ {cmd}: {err}")
                
                if python_results:
                    print(f"   🐍 Python results: {len(python_results)}")
                    for py_result in python_results:
                        if py_result.get('success'):
                            print(f"      ✅ Python execution successful")
                            if py_result.get('output'):
                                print(f"         Output: {py_result['output'].strip()}")
                        else:
                            print(f"      ❌ Python execution failed: {py_result.get('error', 'Unknown error')}")
                
                if file_results:
                    print(f"   📄 File results: {len(file_results)}")
                
                print(f"   📂 Output directory: {result.get('output_dir', 'N/A')}")
                print(f"   📄 Result file: {result.get('workspace_dir', 'N/A')}/result.json")
                
            else:
                print(f"❌ Test FAILED: {test['name']}")
                failed_tests += 1
                print(f"   Error: {result.get('error', 'Unknown error')}")
            
            print()
            
        except Exception as e:
            print(f"❌ Test FAILED with exception: {test['name']}")
            failed_tests += 1
            print(f"   Exception: {str(e)}")
            print()
    
    print("=== Test Suite Summary ===")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Total: {len(test_tasks)}")
    print(f"📈 Success Rate: {(passed_tests/len(test_tasks)*100):.1f}%")
    print()
    print("Check the output directories for detailed results and created files.")
    print("Each test creates its own output directory with workspace and result files.") 