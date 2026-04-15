import { useState } from 'react';
import { LandingPage, ProblemPage } from './pages';
import './App.css';

type PageType = 'landing' | 'problem';

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('landing');

  const handleNavigateToProblem = () => {
    setCurrentPage('problem');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateToLanding = () => {
    setCurrentPage('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app">
      {currentPage === 'landing' ? (
        <LandingPage
          onNavigateToProblem={handleNavigateToProblem}
          onNavigateToLanding={handleNavigateToLanding}
        />
      ) : (
        <ProblemPage onNavigateToLanding={handleNavigateToLanding} />
      )}
    </div>
  );
}

export default App;
