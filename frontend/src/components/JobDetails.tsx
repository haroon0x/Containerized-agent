import { useState, useEffect } from 'react';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';
import type { Job } from './JobList';
import { useParams, useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:8000';

const JobDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [logs, setLogs] = useState('');
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  const [isLoadingJob, setIsLoadingJob] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobDetails = async () => {
      if (!id) return;
      setIsLoadingJob(true);
      try {
        const response = await axios.get(`${API_URL}/job/${id}`);
        setJob(response.data);
      } catch (err) {
        console.error("Error fetching job details:", err);
        setError('Failed to load job details.');
      } finally {
        setIsLoadingJob(false);
      }
    };
    fetchJobDetails();
  }, [id]);

  useEffect(() => {
    if (job) {
      setIsLoadingLogs(true);
      axios.get(`${API_URL}/logs/${job.job_id}`)
        .then(response => setLogs(response.data.logs || 'No logs available.'))
        .catch(error => {
          console.error("Error fetching logs:", error);
          setLogs('Failed to load logs.');
        })
        .finally(() => setIsLoadingLogs(false));
    }
  }, [job]);

  if (isLoadingJob) {
    return <div className="text-center mt-5">Loading job details...</div>;
  }

  if (error) {
    return <div className="alert alert-danger mt-5">{error}</div>;
  }

  if (!job) {
    return <div className="text-center mt-5">Job not found.</div>;
  }

  const handleDownloadLogs = () => {
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${job.job_id}_logs.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mt-5">
      <div className="card p-4 shadow-sm">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="card-title h6 mb-0">Job Details</h5>
          <button type="button" className="btn-close" aria-label="Close" onClick={() => navigate(-1)}></button>
        </div>
        <div className="mb-3">
          <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Job ID</strong>
          <span className="font-monospace">{job.job_id}</span>
        </div>
        <div className="mb-3">
          <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Status</strong>
          <span>{job.status}</span>
        </div>
        <div className="mb-3">
          <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Prompt</strong>
          <p className="mb-0">{job.prompt}</p>
        </div>
        <div className="mb-3">
          <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Created</strong>
          <span>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
        </div>

        <div className="d-flex justify-content-between align-items-center mb-2">
          <h6 className="small mb-0" style={{ color: 'var(--foreground-muted)' }}>Logs</h6>
          <button className="btn btn-sm btn-outline-secondary" onClick={handleDownloadLogs} disabled={!logs || isLoadingLogs}>
            Download Logs
          </button>
        </div>
        <pre className="p-3 rounded small" style={{
          backgroundColor: 'var(--background)',
          minHeight: '200px',
          maxHeight: '400px',
          overflowY: 'auto',
          border: '1px solid var(--border)'
        }}>
          {isLoadingLogs ? 'Loading logs...' : <code className='font-monospace'>{logs}</code>}
        </pre>
      </div>
    </div>
  );
};

export default JobDetails;