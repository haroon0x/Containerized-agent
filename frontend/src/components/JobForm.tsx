
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
        return <b>Job scheduled.</b>;
      },
      error: <b>Could not schedule job.</b>,
    }, { style: { background: 'var(--card)', color: 'var(--foreground)', border: '1px solid var(--border)' } });

    setIsLoading(false);
  };

  return (
    <section className="mb-5">
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <textarea
            id="prompt"
            className="form-control"
            rows={3}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a task..."
          />
        </div>
        <div className="text-end">
          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Scheduling...' : 'Schedule'}
          </button>
        </div>
      </form>
    </section>
  );
};

export default JobForm;
