
import React from 'react';
import { FiBox, FiLoader, FiCheckCircle, FiXCircle } from 'react-icons/fi';

const SystemStats = ({ jobs }) => {
  const totalJobs = jobs.length;
  const runningJobs = jobs.filter(j => j.status === 'running').length;
  const completedJobs = jobs.filter(j => j.status === 'completed').length;

  const Stat = ({ value, label, icon }) => (
    <div className="d-flex align-items-center">
      {icon}
      <span className="ms-2">{value} {label}</span>
    </div>
  );

  return (
    <div className="d-flex justify-content-center mb-5 small" style={{ color: 'var(--foreground-muted)', letterSpacing: '0.05em' }}>
      <Stat value={totalJobs} label="Total" icon={<FiBox size={14} />} />
      <span className="mx-3">•</span>
      <Stat value={runningJobs} label="Running" icon={<FiLoader size={14} />} />
      <span className="mx-3">•</span>
      <Stat value={completedJobs} label="Completed" icon={<FiCheckCircle size={14} />} />
    </div>
  );
};

export default SystemStats;
