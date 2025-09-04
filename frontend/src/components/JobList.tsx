import React from 'react';
import { motion, type Variants, type Transition } from 'framer-motion';
import { FiInfo, FiTrash2, FiDownload, FiCircle, FiAlertCircle, FiLoader } from 'react-icons/fi';
import { formatDistanceToNow } from 'date-fns';
import { Link } from 'react-router-dom';

// Define the type for a single job
export interface Job {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  prompt: string;
  created_at: string;
}

// Define the type for the component's props
interface JobListProps {
  jobs: Job[];
  onCancel: (jobId: string) => void;
  onDownload: (jobId: string) => void;
  filter: string;
  onFilterChange: (filter: string) => void;
}

const statusConfig = {
  pending: { color: 'var(--foreground-muted)', icon: <FiCircle size={8} /> },
  running: { color: '#f59e0b', icon: <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}><FiLoader size={12} /></motion.div> },
  completed: { color: '#10b981', icon: <FiCircle size={8} style={{ fill: '#10b981' }} /> },
  failed: { color: '#ef4444', icon: <FiCircle size={8} style={{ fill: '#ef4444' }} /> },
};

const JobList: React.FC<JobListProps> = ({ jobs, onCancel, onDownload, filter, onFilterChange }) => {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.05, delayChildren: 0.1 } as Transition
    }
  };

  const itemVariants: Variants = {
    hidden: { y: 10, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { type: 'spring', stiffness: 100 } as Transition }
  };

  if (jobs.length === 0) {
    return (
      <div className="text-center py-5 mt-5 border-top" style={{ borderColor: 'var(--border)' }}>
        <FiAlertCircle size={24} className="mx-auto mb-3" style={{ color: 'var(--foreground-muted)' }} />
        <h3 className="h6" style={{ color: 'var(--foreground-muted)' }}>Your scheduled jobs will appear here.</h3>
      </div>
    );
  }

  return (
    <motion.section
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="d-flex justify-content-center mb-4">
        <div className="btn-group" role="group">
          <button type="button" className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => onFilterChange('all')}>All</button>
          <button type="button" className={`btn btn-sm ${filter === 'pending' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => onFilterChange('pending')}>Pending</button>
          <button type="button" className={`btn btn-sm ${filter === 'running' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => onFilterChange('running')}>Running</button>
          <button type="button" className={`btn btn-sm ${filter === 'completed' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => onFilterChange('completed')}>Completed</button>
          <button type="button" className={`btn btn-sm ${filter === 'failed' ? 'btn-primary' : 'btn-outline-secondary'}`} onClick={() => onFilterChange('failed')}>Failed</button>
        </div>
      </div>
      <div className="list-group list-group-flush">
        {jobs.map(job => {
          const isCancelable = job.status === 'pending' || job.status === 'running';
          const isDownloadable = job.status === 'completed';

          return (
            <motion.div
              key={job.job_id}
              className="list-group-item d-flex justify-content-between align-items-center px-1 py-3"
              style={{ backgroundColor: 'transparent', borderBottom: '1px solid var(--border)' }}
              variants={itemVariants}
            >
              <div className="d-flex align-items-center">
                <div style={{ color: statusConfig[job.status]?.color || 'gray' }}>
                  {statusConfig[job.status]?.icon || <FiCircle size={8} />}
                </div>
                <div className="ms-3">
                  <p className="mb-0 fw-medium">{job.prompt || job.job_id}</p>
                  <small style={{ color: 'var(--foreground-muted)' }}>
                    {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                  </small>
                </div>
              </div>
              <div className="d-flex align-items-center">
                <Link to={`/job/${job.job_id}`} className="btn-ghost" title="View Details"><FiInfo size={16} /></Link>
                <button 
                  className="btn-ghost" 
                  title={isCancelable ? "Cancel Job" : "Cannot cancel a completed or failed job"} 
                  onClick={() => onCancel(job.job_id)} 
                  disabled={!isCancelable}
                >
                  <FiTrash2 size={16} />
                </button>
                <button 
                  className="btn-ghost" 
                  title={isDownloadable ? "Download Output" : "Output is not available for this job status"} 
                  onClick={() => onDownload(job.job_id)} 
                  disabled={!isDownloadable}
                >
                  <FiDownload size={16} />
                </button>
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.section>
  );
};

export default JobList;