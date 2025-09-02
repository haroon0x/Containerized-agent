
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import JobForm from './components/JobForm';
import JobList from './components/JobList';
import JobDetails from './components/JobDetails';
import SystemStats from './components/SystemStats';
import './App.css';

type Theme = 'light' | 'dark';

const API_URL = 'http://localhost:8000';

function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [theme, setTheme] = useState<Theme>('dark');

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.className = newTheme;
  };

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_URL}/jobs`);
      const sortedJobs = response.data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setJobs(sortedJobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      toast.error('Could not fetch jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleShowDetails = (job) => setSelectedJob(job);
  const handleCloseDetails = () => setSelectedJob(null);

  const handleCancel = async (jobId) => {
    toast.promise(
      axios.post(`${API_URL}/cancel/${jobId}`),
      {
        loading: 'Cancelling job...',
        success: () => {
          fetchJobs();
          return <b>Job cancelled.</b>;
        },
        error: <b>Could not cancel job.</b>,
      }
    );
  };

  const handleDownload = (jobId) => {
    window.open(`${API_URL}/download/${jobId}`, '_blank');
  };

  return (
    <div className={theme}>
      <Toaster position="bottom-right" toastOptions={{ style: { background: 'var(--card)', color: 'var(--foreground)' } }} />
      <Header theme={theme} toggleTheme={toggleTheme} />
      <main className="container py-4">
        <div className="bento-grid">
          <div className="bento-box job-form-box">
            <h2 className="h5 mb-4">New Job</h2>
            <JobForm onJobScheduled={fetchJobs} />
          </div>
          <div className="bento-box stats-box">
             <SystemStats jobs={jobs} />
          </div>
          <div className="bento-box job-list-box">
            <h2 className="h5 mb-4">Job Status</h2>
            <JobList
              jobs={jobs}
              isLoading={loading}
              onShowDetails={handleShowDetails}
              onCancel={handleCancel}
              onDownload={handleDownload}
            />
          </div>
        </div>
      </main>
      {selectedJob && <JobDetails job={selectedJob} onClose={handleCloseDetails} />}
    </div>
  );
}

export default App;
