
import React from 'react';

const SystemStats = ({ jobs }) => {
  const totalJobs = jobs.length;
  const runningJobs = jobs.filter(j => j.status === 'running').length;
  const completedJobs = jobs.filter(j => j.status === 'completed').length;
  const failedJobs = jobs.filter(j => j.status === 'failed').length;

  const StatCard = ({ label, value }) => (
    <div className="text-center">
      <p className="h3 fw-bold mb-0">{value}</p>
      <p className="text-muted mb-0">{label}</p>
    </div>
  );

  return (
    <div className="bento-box stats-box d-flex align-items-center justify-content-around">
      <StatCard label="Total" value={totalJobs} />
      <StatCard label="Running" value={runningJobs} />
      <StatCard label="Completed" value={completedJobs} />
      <StatCard label="Failed" value={failedJobs} />
    </div>
  );
};

export default SystemStats;
