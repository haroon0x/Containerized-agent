import { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import JobForm from './components/JobForm';
import JobList from './components/JobList';
import JobDetails from './components/JobDetails';
import SystemStats from './components/SystemStats';
import type { Job } from './components/JobList'; // Import Job interface
import './App.css';
import { Routes, Route } from 'react-router-dom';

const API_URL = 'http://localhost:8000';

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    document.body.className = 'dark';
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_URL}/jobs`);
      const sortedJobs = response.data.sort((a: Job, b: Job) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setJobs(sortedJobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      toast.error('Could not fetch jobs.');
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCancel = async (jobId: string) => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      toast.promise(
        axios.post(`${API_URL}/cancel/${jobId}`),
        {
          loading: 'Cancelling job...',
          success: () => {
            fetchJobs();
            return <b>Job cancelled.</b>;
          },
          error: <b>Could not cancel job.</b>,
        },
        { style: { background: 'var(--card)', color: 'var(--foreground)', border: '1px solid var(--border)' } }
      );
    }
  };

  const handleDownload = (jobId: string) => {
    window.open(`${API_URL}/download/${jobId}`, '_blank');
  };

  const filteredJobs = jobs.filter(job => {
    const statusFilter = filter === 'all' || job.status === filter;
    const searchFilter = job.prompt.toLowerCase().includes(searchQuery.toLowerCase());
    return statusFilter && searchFilter;
  });

  return (
    <>
      <Toaster position="bottom-right" />
      <Header />
      <main className="container mt-5">
        <Routes>
          <Route path="/" element={
            <div className="mx-auto" style={{ maxWidth: '720px' }}>
              <div className="mb-4">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by prompt..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <SystemStats jobs={jobs} />
              <JobForm onJobScheduled={fetchJobs} />
              <JobList
                jobs={filteredJobs}
                onCancel={handleCancel}
                onDownload={handleDownload}
                filter={filter}
                onFilterChange={setFilter}
              />
            </div>
          } />
          <Route path="/job/:id" element={<JobDetails />} />
          <Route path="/stats" element={<SystemStats jobs={jobs} />} />
        </Routes>
      </main>
    </>
  );
}

export default App;