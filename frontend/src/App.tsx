import { useState } from 'react';
import { Navbar } from './components/Navbar';

// ── Account Safety mode
import { Hero } from './components/Hero';
import { ProcessSteps } from './components/ProcessSteps';
import { ProgressScreen } from './components/ProgressScreen';
import { ResultsDashboard } from './components/ResultsDashboard';
import { mockAccountData, resolveAccountData } from './mockData';
import type { AccountSafetyData, ExampleKey } from './mockData';

// ── Fact Checker mode
import { FactHero } from './components/FactHero';
import { FactProgressScreen } from './components/FactProgressScreen';
import { FactResultsDashboard } from './components/FactResultsDashboard';
import { mockFactData, resolveFactCheckByUrl } from './factCheckData';
import type { FactClaimData, FactExampleKey } from './factCheckData';

import './App.css';

type AppMode = 'account' | 'factcheck';
type ViewState = 'landing' | 'analyzing' | 'results';

function App() {
  const [mode, setMode]   = useState<AppMode>('account');
  const [view, setView]   = useState<ViewState>('landing');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // ── Account safety state
  const [username, setUsername]         = useState('');
  const [accountData, setAccountData]   = useState<AccountSafetyData | null>(null);

  // ── Fact-check state
  const [reelUrl, setReelUrl]           = useState('');
  const [factData, setFactData]         = useState<FactClaimData | null>(null);

  // ── Theme ──────────────────────────────────────────────
  const handleToggleTheme = () => {
    setTheme(prev => {
      const next = prev === 'light' ? 'dark' : 'light';
      if (next === 'dark') document.body.classList.add('dark');
      else document.body.classList.remove('dark');
      return next;
    });
  };

  // ── Mode switch ────────────────────────────────────────
  const handleSwitchMode = (newMode: AppMode) => {
    setMode(newMode);
    setView('landing');
    setUsername('');
    setReelUrl('');
    setAccountData(null);
    setFactData(null);
  };

  const handleGoHome = () => {
    setView('landing');
    setUsername('');
    setReelUrl('');
    setAccountData(null);
    setFactData(null);
  };

  // ── Account safety handlers ────────────────────────────
  const handleSelectAccountExample = (key: ExampleKey) => {
    const data = mockAccountData[key];
    setUsername(data.username);
    setAccountData(data);
    setView('analyzing');
  };

  const handleAnalyzeAccount = () => {
    if (!username.trim()) return;
    setAccountData(resolveAccountData(username));
    setView('analyzing');
  };

  // ── Fact-check handlers ────────────────────────────────
  const handleSelectFactExample = (key: FactExampleKey) => {
    const data = mockFactData[key];
    setReelUrl(data.reelUrl);
    setFactData(data);
    setView('analyzing');
  };

  const handleAnalyzeReel = () => {
    if (!reelUrl.trim()) return;
    setFactData(resolveFactCheckByUrl(reelUrl));
    setView('analyzing');
  };

  const handleAnalysisComplete = () => setView('results');

  // ── Render ─────────────────────────────────────────────
  return (
    <div className="app-container">
      {/* Ambient background orb */}
      <div style={{
        position: 'fixed', bottom: -220, left: -120,
        width: 520, height: 520, borderRadius: '50%',
        background: 'radial-gradient(circle, var(--primary-glow) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 0,
        animation: 'floatOrb 16s ease-in-out infinite reverse', opacity: 0.42,
      }} />

      <Navbar
        activeMode={mode}
        onSwitchMode={handleSwitchMode}
        onNavigateHome={handleGoHome}
        theme={theme}
        onToggleTheme={handleToggleTheme}
      />

      <main className="main-content" style={{ position: 'relative', zIndex: 1 }}>

        {/* ══════════════ ACCOUNT SAFETY MODE ══════════════ */}
        {mode === 'account' && (
          <>
            {view === 'landing' && (
              <>
                <Hero
                  username={username}
                  setUsername={setUsername}
                  onAnalyze={handleAnalyzeAccount}
                  onSelectExample={handleSelectAccountExample}
                />
                <ProcessSteps />
              </>
            )}
            {view === 'analyzing' && <ProgressScreen onComplete={handleAnalysisComplete} />}
            {view === 'results' && accountData && (
              <ResultsDashboard data={accountData} onBack={handleGoHome} />
            )}
          </>
        )}

        {/* ══════════════ FACT CHECKER MODE ══════════════ */}
        {mode === 'factcheck' && (
          <>
            {view === 'landing' && (
              <>
                <FactHero
                  reelUrl={reelUrl}
                  setReelUrl={setReelUrl}
                  onAnalyze={handleAnalyzeReel}
                  onSelectExample={handleSelectFactExample}
                />
                <FactProcessStepsSection />
              </>
            )}
            {view === 'analyzing' && <FactProgressScreen onComplete={handleAnalysisComplete} />}
            {view === 'results' && factData && (
              <FactResultsDashboard data={factData} onBack={handleGoHome} />
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-links">
          <span className="footer-link" onClick={handleGoHome}>Home</span>
          <span className="footer-link" onClick={() => handleSwitchMode('account')}>Account Safety</span>
          <span className="footer-link" onClick={() => handleSwitchMode('factcheck')}>Fact Checker</span>
          <span className="footer-link" onClick={() => window.open('mailto:support@safecheck.app')}>Contact</span>
        </div>
        <p style={{ fontSize: '0.82rem' }}>
          © 2026 SafeCheck · Account safety &amp; fact-checking for everyone ·
          <span style={{ color: 'var(--primary)', fontWeight: 700 }}> Free to use</span>
        </p>
      </footer>
    </div>
  );
}

// Inline "How it works" for Fact Checker mode
function FactProcessStepsSection() {
  const steps = [
    { emoji: '📋', title: 'Paste the Claim', desc: 'Copy and paste any viral claim, headline, or reel caption into the text box.' },
    { emoji: '🔎', title: 'We Check the Facts', desc: 'Our system cross-references the claim with trusted sources, news, and known facts.' },
    { emoji: '⚖️', title: 'Get a Clear Verdict', desc: 'Receive a plain-English verdict: TRUE, FALSE, or PARTIALLY TRUE — with explanation.' },
    { emoji: '🛡️', title: 'Stay Informed', desc: 'See which facts were confirmed, which were disputed, and what to watch out for.' },
  ];
  return (
    <section id="how-it-works" className="process-card" style={{ marginBottom: '4rem' }}>
      <div className="process-header">
        <h3>How Fact-Checking Works</h3>
        <p>Four steps to verify any claim you see online</p>
      </div>
      <div className="process-steps">
        {steps.map(s => (
          <div key={s.title} className="process-step">
            <div className="step-num">{s.emoji}</div>
            <div className="step-title">{s.title}</div>
            <p className="step-desc">{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default App;
