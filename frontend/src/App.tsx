
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import JobForm from './components/JobForm';
import JobList from './components/JobList';
import JobDetails from './components/JobDetails';
import SystemStats from './components/SystemStats';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    document.body.className = 'dark';
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API_URL}/jobs`);
      const sortedJobs = response.data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
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
      },
      { style: { background: 'var(--card)', color: 'var(--foreground)', border: '1px solid var(--border)' } }
    );
  };

  const handleDownload = (jobId) => {
    window.open(`${API_URL}/download/${jobId}`, '_blank');
  };

  return (
    <>
      <Toaster position="bottom-right" />
      <Header />
      <main className="container mt-5">
        <div className="mx-auto" style={{ maxWidth: '720px' }}>
          <SystemStats jobs={jobs} />
          <JobForm onJobScheduled={fetchJobs} />
          <JobList
            jobs={jobs}
            onShowDetails={handleShowDetails}
            onCancel={handleCancel}
            onDownload={handleDownload}
          />
        </div>
      </main>
      {selectedJob && <JobDetails job={selectedJob} onClose={handleCloseDetails} />}
    </>
  );
}

export default App;
