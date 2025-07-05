import pytest
from unittest.mock import patch, MagicMock
from orchestrator.api.job_manager import JobManager

@patch('orchestrator.api.job_manager.docker')
def test_launch_job_success(mock_docker):
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.id = 'container123'
    mock_client.containers.run.return_value = mock_container
    mock_docker.from_env.return_value = mock_client
    jm = JobManager()
    job_id = jm.launch_job('echo test')
    assert job_id in jm.jobs
    assert jm.jobs[job_id]['status'] == 'running'

@patch('orchestrator.api.job_manager.docker')
def test_launch_job_error(mock_docker):
    mock_client = MagicMock()
    mock_client.containers.run.side_effect = Exception('fail')
    mock_docker.from_env.return_value = mock_client
    jm = JobManager()
    job_id = jm.launch_job('fail')
    assert job_id in jm.jobs
    assert jm.jobs[job_id]['status'] == 'error'

@patch('orchestrator.api.job_manager.docker')
def test_get_status_not_found(mock_docker):
    jm = JobManager()
    status = jm.get_status('not-a-job')
    assert status == 'not_found'

@patch('orchestrator.api.job_manager.docker')
def test_cancel_job_invalid(mock_docker):
    jm = JobManager()
    result = jm.cancel_job('not-a-job')
    assert result is False 