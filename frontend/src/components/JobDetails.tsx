import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

const API_URL = 'http://localhost:8000';

const JobDetails = ({ job, onClose }) => {
  const [logs, setLogs] = useState('');
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);

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

  if (!job) return null;

  return (
    <motion.div
      className="modal show d-block"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{ backgroundColor: 'rgba(0,0,0,0.7)' }}
      onClick={onClose}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered" onClick={e => e.stopPropagation()}>
        <motion.div
          className="modal-content"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 20, opacity: 0 }}
        >
          <div className="modal-header border-0">
            <h5 className="modal-title h6">Job Details</h5>
            <button type="button" className="btn-close-white" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-4">
              <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Job ID</strong>
              <span className="font-monospace">{job.job_id}</span>
            </div>
            <div className="mb-4">
              <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Status</strong>
              <span>{job.status}</span>
            </div>
            <div className="mb-4">
              <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Prompt</strong>
              <p className="mb-0">{job.prompt}</p>
            </div>
            <div className="mb-4">
              <strong className="d-block small mb-1" style={{ color: 'var(--foreground-muted)' }}>Created</strong>
              <span>{formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}</span>
            </div>
            
            <h6 className="small" style={{ color: 'var(--foreground-muted)' }}>Logs</h6>
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
        </motion.div>
      </div>
    </motion.div>
  );
};

export default JobDetails;