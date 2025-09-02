
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

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
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <motion.div
          className="modal-content"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -50, opacity: 0 }}
          style={{ 
            backgroundColor: 'color-mix(in srgb, var(--card) 90%, transparent)',
            backdropFilter: 'blur(20px)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)'
          }}
        >
          <div className="modal-header border-0">
            <h5 className="modal-title">Job Details</h5>
            <button type="button" className="btn-close-white" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <strong className="d-block text-muted mb-1">Job ID</strong>
              <span>{job.job_id}</span>
            </div>
            <div className="mb-3">
              <strong className="d-block text-muted mb-1">Status</strong>
              <span>{job.status}</span>
            </div>
            <div className="mb-3">
              <strong className="d-block text-muted mb-1">Prompt</strong>
              <p>{job.prompt}</p>
            </div>
            <div className="mb-3">
              <strong className="d-block text-muted mb-1">Created At</strong>
              <span>{new Date(job.created_at).toLocaleString()}</span>
            </div>
            
            <h6 className="mt-4">Logs</h6>
            <pre className="p-3 rounded" style={{ 
              backgroundColor: 'var(--background)', 
              minHeight: '200px', 
              maxHeight: '400px', 
              overflowY: 'auto',
              border: '1px solid var(--border)'
            }}>
              {isLoadingLogs ? 'Loading logs...' : <code>{logs}</code>}
            </pre>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default JobDetails;
