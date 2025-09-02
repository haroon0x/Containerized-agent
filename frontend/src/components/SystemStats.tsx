import React from 'react';

const SystemStats = ({ jobs }) => {
  const totalJobs = jobs.length;
  const runningJobs = jobs.filter(j => j.status === 'running').length;
  const completedJobs = jobs.filter(j => j.status === 'completed').length;

  return (
    <div className="text-center mb-5 small text-uppercase" style={{ color: 'var(--foreground-muted)', letterSpacing: '0.1em' }}>
      {totalJobs} Total <span className="mx-2">•</span> {runningJobs} Running <span className="mx-2">•</span> {completedJobs} Completed
    </div>
  );
};

export default SystemStats;