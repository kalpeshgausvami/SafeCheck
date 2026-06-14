import React, { useEffect, useState } from 'react';

interface FactProgressProps {
  onComplete: () => void;
}

const STEPS = [
  { label: 'Opening the reel link…',              icon: '🔗' },
  { label: 'Fetching reel content…',              icon: '📥' },
  { label: 'Extracting spoken claims from video…', icon: '🎙️' },
  { label: 'Reading on-screen text…',             icon: '👁️' },
  { label: 'Cross-referencing with trusted sources…', icon: '📚' },
  { label: 'Forming a verdict…',                  icon: '⚖️' },
  { label: 'Preparing your report…',              icon: '📋' },
];

export const FactProgressScreen: React.FC<FactProgressProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= STEPS.length - 1) { clearInterval(interval); setTimeout(onComplete, 500); return prev + 1; }
        return prev + 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [onComplete]);

  const progress = Math.min((currentStep / STEPS.length) * 100, 100);

  return (
    <div className="progress-container">
      {/* Instagram reel spinner */}
      <div style={{
        width: 84, height: 84, borderRadius: '50%', margin: '0 auto 1.75rem',
        background: 'linear-gradient(135deg, #f58529, #dd2a7b, #8134af)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 40px rgba(221,42,123,0.5), inset 0 2px 0 rgba(255,255,255,0.2)',
        animation: 'glowPulse 2s ease-in-out infinite', position: 'relative', flexShrink: 0,
      }}>
        <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: 'linear-gradient(180deg,rgba(255,255,255,0.18) 0%,transparent 60%)' }} />
        <span style={{ fontSize: '2.2rem', lineHeight: 1, display: 'block' }}>🎬</span>
      </div>

      <div className="progress-header-text">Analyzing Reel Content</div>
      <p className="progress-subheader">
        We're watching and reading the reel, then cross-checking all claims with trusted sources.
      </p>

      {/* Progress bar */}
      <div style={{ height: 6, borderRadius: 999, background: 'var(--bg-input)', marginBottom: '2.25rem', overflow: 'hidden', boxShadow: 'var(--shadow-inset)' }}>
        <div style={{
          height: '100%', borderRadius: 999,
          background: 'linear-gradient(90deg, #f58529, #dd2a7b, #8134af)',
          width: `${progress}%`, transition: 'width 0.7s cubic-bezier(0.4,0,0.2,1)',
          boxShadow: '0 0 12px rgba(221,42,123,0.5)',
        }} />
      </div>

      {/* Steps */}
      <div className="progress-steps-list">
        {STEPS.map((step, idx) => {
          const state = idx < currentStep ? 'completed' : idx === currentStep ? 'active' : 'pending';
          return (
            <div key={step.label} className={`progress-item ${state}`}>
              <div className="progress-icon">
                {state === 'completed' ? (
                  <span style={{ fontSize: '1.1rem' }}>✅</span>
                ) : state === 'active' ? (
                  <div className="progress-spinner" style={{ borderTopColor: '#dd2a7b', borderColor: 'rgba(221,42,123,0.2)' }} />
                ) : (
                  <span style={{ fontSize: '1rem', opacity: 0.32 }}>{step.icon}</span>
                )}
              </div>
              <span style={{ flex: 1 }}>{step.label}</span>
              {state === 'completed' && (
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--safe)', letterSpacing: '0.02em' }}>Done</span>
              )}
            </div>
          );
        })}
      </div>

      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
        🔒 Your reel link is not stored. Analysis is private and not logged.
      </div>
    </div>
  );
};
