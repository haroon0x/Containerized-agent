import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pytest
from src.agent.agent_runtime import AgentRuntime
from src.agent_container.agent_runner import main


class TestAgentRuntime:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.task = "Write a simple hello world function in Python"
        self.job_id = "test_job_123"
        self.output_dir = os.path.join(self.temp_dir, "output")

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('src.agent.agent_runtime.create_qa_flow')
    def test_agent_runtime_initialization(self, mock_create_flow):
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow
        
        runtime = AgentRuntime(self.task, self.job_id, self.output_dir)
        
        assert runtime.task == self.task
        assert runtime.job_id == self.job_id
        assert runtime.output_dir == os.path.join(self.output_dir, self.job_id)
        assert os.path.exists(runtime.output_dir)
        assert runtime.result_file == os.path.join(runtime.output_dir, "result.json")

    @patch('src.agent.agent_runtime.create_qa_flow')
    def test_agent_runtime_successful_run(self, mock_create_flow):
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow
        
        runtime = AgentRuntime(self.task, self.job_id, self.output_dir)
        
        shared_data = {
            "task_analysis": {"analysis": "test analysis"},
            "shell_results": [{"command": "echo hello", "output": "hello"}],
            "python_results": [{"code": "print('hello')", "output": "hello"}]
        }
        mock_flow.run.return_value = None
        
        with patch.object(mock_flow, 'run') as mock_run:
            mock_run.side_effect = lambda shared: shared.update(shared_data)
            
            result = runtime.run()
            
            assert result["task"] == self.task
            assert result["job_id"] == self.job_id
            assert result["status"] == "completed"
            assert result["analysis"] == shared_data["task_analysis"]
            assert result["shell_results"] == shared_data["shell_results"]
            assert result["python_results"] == shared_data["python_results"]
            
            assert os.path.exists(runtime.result_file)
            with open(runtime.result_file, 'r') as f:
                saved_result = json.load(f)
            assert saved_result == result

    @patch('src.agent.agent_runtime.create_qa_flow')
    def test_agent_runtime_failed_run(self, mock_create_flow):
        mock_flow = MagicMock()
        mock_create_flow.return_value = mock_flow
        mock_flow.run.side_effect = Exception("Test error")
        
        runtime = AgentRuntime(self.task, self.job_id, self.output_dir)
        
        result = runtime.run()
        
        assert result["job_id"] == self.job_id
        assert result["task"] == self.task
        assert result["status"] == "failed"
        assert "Test error" in result["error"]
        
        assert os.path.exists(runtime.result_file)
        with open(runtime.result_file, 'r') as f:
            saved_result = json.load(f)
        assert saved_result == result

    def test_agent_runtime_default_output_dir(self):
        with patch('src.agent.agent_runtime.create_qa_flow') as mock_create_flow:
            mock_flow = MagicMock()
            mock_create_flow.return_value = mock_flow
            
            runtime = AgentRuntime(self.task, self.job_id)
            
            expected_output_dir = f"/workspace/output/{self.job_id}"
            assert runtime.output_dir == expected_output_dir


class TestAgentRunner:
    @patch('src.agent_container.agent_runner.AgentRuntime')
    @patch('src.agent_container.agent_runner.logging')
    @patch.dict(os.environ, {
        'JOB_PROMPT': 'Test task prompt',
        'JOB_ID': 'test_job_456',
        'AGENT_OUTPUT_DIR': '/test/output'
    })
    def test_main_with_environment_variables(self, mock_logging, mock_agent_runtime_class):
        mock_runtime = MagicMock()
        mock_agent_runtime_class.return_value = mock_runtime
        
        main()
        
        mock_agent_runtime_class.assert_called_once_with(
            'Test task prompt',
            'test_job_456',
            output_dir='/test/output'
        )
        mock_runtime.run.assert_called_once()

    @patch('src.agent_container.agent_runner.AgentRuntime')
    @patch('src.agent_container.agent_runner.logging')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_with_default_values(self, mock_logging, mock_agent_runtime_class):
        mock_runtime = MagicMock()
        mock_agent_runtime_class.return_value = mock_runtime
        
        main()
        
        mock_agent_runtime_class.assert_called_once_with(
            ' write a hello function ina python file',
            'unknown',
            output_dir='output'
        )
        mock_runtime.run.assert_called_once()


def test_integration_agent_runner():
    """Integration test that can be run to verify the agent runner works end-to-end"""
    temp_dir = tempfile.mkdtemp()
    try:
        job_id = "integration_test_123"
        task = "Create a simple Python function that returns 'Hello, World!'"
        output_dir = os.path.join(temp_dir, "output")
        
        with patch('src.agent.agent_runtime.create_qa_flow') as mock_create_flow:
            mock_flow = MagicMock()
            mock_create_flow.return_value = mock_flow
            
            runtime = AgentRuntime(task, job_id, output_dir)
            
            shared_data = {
                "task_analysis": {"plan": "Create a simple hello world function"},
                "shell_results": [],
                "python_results": [{"code": "def hello(): return 'Hello, World!'", "output": "Function created"}]
            }
            
            with patch.object(mock_flow, 'run') as mock_run:
                mock_run.side_effect = lambda shared: shared.update(shared_data)
                
                result = runtime.run()
                
                assert result["status"] == "completed"
                assert result["job_id"] == job_id
                assert result["task"] == task
                assert len(result["python_results"]) > 0
                
                result_file = os.path.join(output_dir, job_id, "result.json")
                assert os.path.exists(result_file)
                
                with open(result_file, 'r') as f:
                    saved_result = json.load(f)
                assert saved_result == result
                
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True) 