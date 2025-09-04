
import { FiBox, FiLoader, FiCheckCircle } from 'react-icons/fi';
import type { Job } from './JobList';

interface SystemStatsProps {
  jobs: Job[];
}

const SystemStats: React.FC<SystemStatsProps> = ({ jobs }) => {
  const totalJobs = jobs.length;
  const runningJobs = jobs.filter((j: Job) => j.status === 'running').length;
  const completedJobs = jobs.filter((j: Job) => j.status === 'completed').length;

  interface StatProps {
    value: number;
    label: string;
    icon: React.ReactElement;
  }

  const Stat: React.FC<StatProps> = ({ value, label, icon }) => (
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
