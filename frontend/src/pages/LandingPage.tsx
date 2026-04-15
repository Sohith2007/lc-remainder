import React, { useState, useEffect } from 'react';
import { Header, Footer, Badge, Button, Input, ToastContainer, type ToastVariant } from '../components';
import { apiClient } from '../api';
import type { DailyProblem, RecipientResponse } from '../types/api';
import './LandingPage.css';

interface LandingPageProps {
  onNavigateToProblem: () => void;
  onNavigateToLanding: () => void;
}

interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigateToProblem, onNavigateToLanding }) => {
  const [problem, setProblem] = useState<DailyProblem | null>(null);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    loadProblem();
  }, []);

  const loadProblem = async () => {
    try {
      const response = await apiClient.getHome();
      setProblem(response.daily_problem);
    } catch (err) {
      console.error('Failed to load problem:', err);
    }
  };

  const addToast = (message: string, variant: ToastVariant = 'info') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, variant }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiClient.addRecipient(email) as RecipientResponse;
      addToast(response.message, 'success');
      setEmail('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to subscribe';
      setError(errorMessage);
      addToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="landing-page">
      <Header onTodaysProblemClick={onNavigateToProblem} onSubscribeClick={() => {}} onLogoClick={onNavigateToLanding} />

      <main className="landing-content">
        <div className="hero-section">
          <div className="hero-left">
            <Badge label="Daily Problem" variant="primary" />
            <h1 className="hero-title">Never Miss a Day on LeetCode</h1>
            <p className="hero-description">
              Master your technical interviews with a curated daily challenge delivered directly
              to your workspace. Consistency is the edge you need.
            </p>
          </div>

          <div className="hero-right">
            <div className="signup-card">
              <div className="signup-icon">✉️</div>
              <h2 className="signup-title">Join To Grind</h2>
              <p className="signup-subtitle">One problem. Every morning. Zero Friction.</p>

              <form onSubmit={handleSubscribe} className="signup-form">
                <Input
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={error}
                  disabled={loading}
                  required
                />
                <Button type="submit" loading={loading} fullWidth>
                  Subscribe →
                </Button>
              </form>

              <ul className="signup-benefits">
                <li>Frequency: Daily (Mon-Sun)</li>
                <li>Commitment: No spam, unsubscribe in one click</li>
              </ul>
            </div>
          </div>
        </div>

        {problem && (
          <div className="featured-problem">
            <h3>Today's Daily Challenge</h3>
            <div className="problem-preview">
              <div className="problem-meta">
                <Badge label={problem.difficulty} variant="difficulty" />
                <h4>{problem.title}</h4>
              </div>
              <p className="problem-excerpt">{problem.description.substring(0, 200)}...</p>
              <Button variant="secondary" onClick={onNavigateToProblem}>
                View Problem Details
              </Button>
            </div>
          </div>
        )}
      </main>

      <Footer />
      <ToastContainer messages={toasts} onRemove={removeToast} />
    </div>
  );
};
