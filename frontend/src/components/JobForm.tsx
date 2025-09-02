
import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const API_URL = 'http://localhost:8000';

const JobForm = ({ onJobScheduled }) => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    const promise = axios.post(`${API_URL}/schedule`, { prompt });

    toast.promise(promise, {
      loading: 'Scheduling job...',
      success: () => {
        setPrompt('');
        onJobScheduled();
        return <b>Job scheduled successfully!</b>;
      },
      error: <b>Could not schedule job.</b>,
    });

    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <textarea
          id="prompt"
          className="form-control"
          rows={5}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter a task for the AI agent..."
          style={{
            backgroundColor: 'var(--input)',
            color: 'var(--foreground)',
            borderColor: 'var(--border)',
            resize: 'none'
          }}
        />
      </div>
      <button
        type="submit"
        className="btn w-100 fw-medium"
        disabled={isLoading}
        style={{
          background: 'var(--accent-gradient)',
          color: 'var(--primary-foreground)',
          border: 'none'
        }}
      >
        {isLoading ? 'Scheduling...' : 'Schedule Job'}
      </button>
    </form>
  );
};

export default JobForm;
