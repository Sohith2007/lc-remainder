import React, { useState, useEffect } from 'react';
import { Header, Footer, Badge, Button } from '../components';
import { apiClient } from '../api';
import type { DailyProblem } from '../types/api';
import './ProblemPage.css';

interface ProblemPageProps {
  onNavigateToLanding: () => void;
}

export const ProblemPage: React.FC<ProblemPageProps> = ({ onNavigateToLanding }) => {
  const [problem, setProblem] = useState<DailyProblem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProblem();
  }, []);

  useEffect(() => {
    // Update timer every minute
    const interval = setInterval(() => {
      loadProblem();
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadProblem = async () => {
    try {
      const response = await apiClient.getProblem();
      setProblem(response.daily_problem);
    } catch (err) {
      console.error('Failed to load problem:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSolveClick = () => {
    if (problem?.url) {
      window.open(problem.url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="problem-page">
        <Header onTodaysProblemClick={() => {}} onSubscribeClick={onNavigateToLanding} onLogoClick={onNavigateToLanding} />
        <div className="loading">Loading problem...</div>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="problem-page">
        <Header onTodaysProblemClick={() => {}} onSubscribeClick={onNavigateToLanding} onLogoClick={onNavigateToLanding} />
        <div className="error">Failed to load problem</div>
      </div>
    );
  }

  return (
    <div className="problem-page">
      <Header onTodaysProblemClick={() => {}} onSubscribeClick={onNavigateToLanding} onLogoClick={onNavigateToLanding} />

      <main className="problem-content">
        <div className="problem-main">
          <div className="problem-header">
            <Badge label="Daily Challenge" variant="primary" />
            <div className="problem-date">
              {new Date(problem.fetched_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </div>
          </div>

          <h1 className="problem-title">{problem.title}</h1>

          <div className="problem-tags">
            <Badge label={problem.difficulty} variant="difficulty" />
            {(problem.topic_tags || []).slice(0, 6).map((tag) => (
              <Badge key={tag} label={tag} variant="tag" />
            ))}
          </div>

          <section className="problem-statement">
            <h2>Problem Statement</h2>
            <div className="problem-description">{problem.description}</div>
          </section>
        </div>

        <aside className="problem-sidebar">
          <Button fullWidth onClick={handleSolveClick} className="solve-button">
            Solve on LeetCode →
          </Button>

          <div className="sidebar-section acceptance-rate">
            <h3>Acceptance Rate</h3>
            <div className="rate-stat">
              <div className="rate-value">{problem.acceptance_rate ? `${problem.acceptance_rate.toFixed(1)}%` : 'N/A'}</div>
              <div className="rate-bar">
                <div className="rate-fill" style={{ width: `${problem.acceptance_rate || 0}%` }}></div>
              </div>
            </div>
          </div>
        </aside>
      </main>

      <Footer />
    </div>
  );
};
