import React, { useEffect, useState } from 'react';

interface ProgressScreenProps {
  onComplete: () => void;
}

const STEPS = [
  { label: 'Looking up account…',           icon: '🔍' },
  { label: 'Checking profile details…',     icon: '👤' },
  { label: 'Analyzing activity patterns…',  icon: '📊' },
  { label: 'Reviewing follower information…', icon: '👥' },
  { label: 'Running safety checks…',        icon: '🛡️' },
  { label: 'Preparing your report…',        icon: '📋' },
];

export const ProgressScreen: React.FC<ProgressScreenProps> = ({ onComplete }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev >= STEPS.length - 1) {
          clearInterval(interval);
          setTimeout(() => onComplete(), 500);
          return prev + 1;
        }
        return prev + 1;
      });
    }, 1100);
    return () => clearInterval(interval);
  }, [onComplete]);

  const progress = Math.min((currentStepIndex / STEPS.length) * 100, 100);

  return (
    <div className="progress-container">
      {/* Shield spinner */}
      <div style={{
        width: 84, height: 84, borderRadius: '50%', margin: '0 auto 1.75rem',
        background: 'var(--gradient-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 40px var(--primary-glow-strong), inset 0 2px 0 rgba(255,255,255,0.25)',
        animation: 'glowPulse 2s ease-in-out infinite',
        position: 'relative',
        flexShrink: 0,
      }}>
        <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: 'linear-gradient(180deg,rgba(255,255,255,0.18) 0%,transparent 60%)' }} />
        <span style={{ fontSize: '2.2rem', lineHeight: 1, display: 'block' }}>🛡️</span>
      </div>

      <div className="progress-header-text">Analyzing Account</div>
      <p className="progress-subheader">
        We're checking this account for safety signals. This usually takes about 10 seconds.
      </p>

      {/* Progress bar */}
      <div style={{ height: 6, borderRadius: 999, background: 'var(--bg-input)', marginBottom: '2.25rem', overflow: 'hidden', boxShadow: 'var(--shadow-inset)' }}>
        <div style={{
          height: '100%', borderRadius: 999,
          background: 'var(--gradient-primary)',
          width: `${progress}%`,
          transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)',
          boxShadow: '0 0 12px var(--primary-glow)',
        }} />
      </div>

      {/* Steps */}
      <div className="progress-steps-list">
        {STEPS.map((step, idx) => {
          const state = idx < currentStepIndex ? 'completed' : idx === currentStepIndex ? 'active' : 'pending';
          return (
            <div key={step.label} className={`progress-item ${state}`}>
              <div className="progress-icon">
                {state === 'completed' ? (
                  <span style={{ fontSize: '1.1rem' }}>✅</span>
                ) : state === 'active' ? (
                  <div className="progress-spinner" />
                ) : (
                  <span style={{ fontSize: '1rem', opacity: 0.35 }}>{step.icon}</span>
                )}
              </div>
              <span style={{ flex: 1 }}>{step.label}</span>
              {state === 'completed' && (
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--success)', letterSpacing: '0.02em' }}>
                  Done
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Reassurance note */}
      <div style={{
        borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem',
        fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.6,
      }}>
        🔒 Your search is private. We do not store usernames or share your data.
      </div>
    </div>
  );
};
