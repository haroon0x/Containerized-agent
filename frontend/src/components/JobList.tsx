
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiInfo, FiTrash2, FiDownload, FiCircle, FiAlertCircle } from 'react-icons/fi';
import SkeletonLoader from './SkeletonLoader';

const statusConfig = {
  pending: { icon: FiCircle, color: 'var(--muted-foreground)' },
  running: { icon: FiCircle, color: '#f59e0b' },
  completed: { icon: FiCircle, color: '#10b981' },
  failed: { icon: FiCircle, color: '#ef4444' },
};

const JobList = ({ jobs, isLoading, onShowDetails, onCancel, onDownload }) => {
  if (isLoading) {
    return <SkeletonLoader />;
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.07 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <AnimatePresence>
      {jobs.length === 0 ? (
        <motion.div
          className="text-center py-5"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <FiAlertCircle size={48} className="mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
          <h3 className="h5">No Jobs Found</h3>
          <p className="text-muted">Schedule a new job to get started.</p>
        </motion.div>
      ) : (
        <motion.div
          className="list-group"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {jobs.map(job => (
            <motion.div
              key={job.job_id}
              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center mb-2"
              variants={itemVariants}
              layout
              style={{
                backgroundColor: 'var(--muted)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)'
              }}
            >
              <div className="d-flex align-items-center">
                <statusConfig.icon
                  size={14}
                  color={statusConfig[job.status]?.color || 'gray'}
                  style={{ fill: statusConfig[job.status]?.color || 'gray' }}
                />
                <div className="ms-3">
                  <p className="mb-0 fw-medium">{job.prompt || job.job_id}</p>
                  <small className="text-muted">{new Date(job.created_at).toLocaleString()}</small>
                </div>
              </div>
              <div>
                <button className="btn-ghost" onClick={() => onShowDetails(job)}><FiInfo /></button>
                <button className="btn-ghost" onClick={() => onCancel(job.job_id)}><FiTrash2 /></button>
                <button className="btn-ghost" onClick={() => onDownload(job.job_id)}><FiDownload /></button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default JobList;
