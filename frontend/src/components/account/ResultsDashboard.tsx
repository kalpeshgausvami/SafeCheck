import React, { useEffect, useRef, useState } from 'react';
import type { AccountSafetyData } from '../mockData';

interface ResultsDashboardProps {
  data: AccountSafetyData;
  onBack: () => void;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const statusConfig = {
  safe: {
    label: 'Safe Account',
    emoji: '✅',
    color: '#10b981',
    bg: 'rgba(16,185,129,0.08)',
    border: 'rgba(16,185,129,0.25)',
    ringColor: '#10b981',
    tagline: 'This account appears genuine and trustworthy.',
  },
  caution: {
    label: 'Needs Attention',
    emoji: '⚠️',
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.08)',
    border: 'rgba(245,158,11,0.25)',
    ringColor: '#f59e0b',
    tagline: 'Some warning signs were found. Proceed with care.',
  },
  danger: {
    label: 'High Risk Account',
    emoji: '🚨',
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.08)',
    border: 'rgba(239,68,68,0.25)',
    ringColor: '#ef4444',
    tagline: 'Serious warning signs detected. Be very careful.',
  },
};

const severityColor = { low: '#94a3b8', medium: '#f59e0b', high: '#ef4444' };
const severityBg    = { low: 'rgba(148,163,184,0.08)', medium: 'rgba(245,158,11,0.08)', high: 'rgba(239,68,68,0.08)' };
const severityBorder= { low: 'rgba(148,163,184,0.2)',  medium: 'rgba(245,158,11,0.25)',  high: 'rgba(239,68,68,0.25)' };

function formatNumber(n: number) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(n);
}

// ─── Trust Score Circle ───────────────────────────────────────────────────────
const TrustScoreCircle: React.FC<{ score: number; color: string }> = ({ score, color }) => {
  const [displayed, setDisplayed] = useState(0);
  const ref = useRef<number>(0);

  useEffect(() => {
    ref.current = 0;
    setDisplayed(0);
    const duration = 1200;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const val = Math.round(eased * score);
      setDisplayed(val);
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [score]);

  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (displayed / 100) * circumference;

  return (
    <div style={{ position: 'relative', width: 160, height: 160, margin: '0 auto' }}>
      <svg width="160" height="160" viewBox="0 0 160 160" style={{ transform: 'rotate(-90deg)' }}>
        {/* Track */}
        <circle cx="80" cy="80" r="52" fill="none" stroke="var(--border-color)" strokeWidth="10" />
        {/* Progress */}
        <circle
          cx="80" cy="80" r="52"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.05s linear', filter: `drop-shadow(0 0 8px ${color}80)` }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.04em', lineHeight: 1 }}>
          {displayed}
        </span>
        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          out of 100
        </span>
      </div>
    </div>
  );
};

// ─── Risk Meter Bar ───────────────────────────────────────────────────────────
const RiskMeter: React.FC<{ score: number }> = ({ score }) => {
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const t = setTimeout(() => setWidth(score), 100);
    return () => clearTimeout(t);
  }, [score]);

  const meterColor = score >= 75 ? '#10b981' : score >= 45 ? '#f59e0b' : '#ef4444';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        <span>🔴 High Risk</span>
        <span>🟡 Caution</span>
        <span>🟢 Safe</span>
      </div>
      <div style={{ height: 12, borderRadius: 999, background: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)', position: 'relative', boxShadow: 'var(--shadow-inset)' }}>
        {/* Track overlay */}
        <div style={{ position: 'absolute', inset: 0, borderRadius: 999, background: 'rgba(0,0,0,0.15)' }} />
        {/* Pointer */}
        <div style={{
          position: 'absolute',
          left: `${width}%`,
          top: '50%',
          transform: 'translate(-50%, -50%)',
          width: 22, height: 22,
          borderRadius: '50%',
          background: '#fff',
          border: `3px solid ${meterColor}`,
          boxShadow: `0 2px 12px ${meterColor}80`,
          transition: 'left 1.2s cubic-bezier(0.34,1.56,0.64,1)',
          zIndex: 2,
        }} />
      </div>
      <div style={{ textAlign: 'center', marginTop: 10, fontSize: '0.82rem', fontWeight: 700, color: meterColor }}>
        Safety Score: {score}/100
      </div>
    </div>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────
export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ data, onBack }) => {
  const cfg = statusConfig[data.safetyStatus];

  // Download simple report
  const downloadReport = () => {
    const lines = [
      `SafeCheck Account Safety Report`,
      `================================`,
      `Account: @${data.username}`,
      `Display Name: ${data.displayName}`,
      `Safety Status: ${cfg.label}`,
      `Trust Score: ${data.trustScore}/100`,
      ``,
      `Summary`,
      `-------`,
      data.safetySummary,
      ``,
      `Account Details`,
      `---------------`,
      `Followers: ${formatNumber(data.followerCount)}`,
      `Following: ${formatNumber(data.followingCount)}`,
      `Posts: ${data.postCount}`,
      `Account Age: ${data.accountAge}`,
      `Verified: ${data.isVerified ? 'Yes' : 'No'}`,
      ``,
      `Warning Signs Found`,
      `-------------------`,
      ...(data.warningIndicators.length === 0
        ? ['None — this account looks clean!']
        : data.warningIndicators.map(w => `${w.icon} ${w.label}: ${w.description}`)),
      ``,
      `Recommended Actions`,
      `-------------------`,
      ...data.recommendations.map((r, i) => `${i + 1}. ${r}`),
      ``,
      `Generated by SafeCheck · ${new Date().toLocaleDateString()}`,
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `safecheck-@${data.username}.txt`;
    a.click();
  };

  return (
    <div className="results-wrapper">

      {/* ── Back button ─────────────────────────────────── */}
      <button onClick={onBack} className="btn-back" id="back-to-home-btn" style={{ marginBottom: '2rem' }}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
        <span>Check another account</span>
      </button>

      {/* ══════════════════════════════════════════════════
          SECTION A: Account Overview Card
      ══════════════════════════════════════════════════ */}
      <div className="results-overview-card" style={{
        border: `1.5px solid ${cfg.border}`,
        background: cfg.bg,
      }}>
        {/* Profile info row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flexShrink: 0 }}>
            <img
              src={data.profilePicUrl}
              alt={data.displayName}
              style={{ width: 80, height: 80, borderRadius: '50%', objectFit: 'cover', border: `3px solid ${cfg.color}`, boxShadow: `0 0 20px ${cfg.color}50` }}
              onError={e => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1511367461989-f85a21fda167?auto=format&fit=crop&q=80&w=200'; }}
            />
            {data.isVerified && (
              <span title="Verified" style={{ position: 'absolute', bottom: 2, right: 2, fontSize: '1.1rem' }}>✅</span>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 4 }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{data.displayName}</h2>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-secondary)' }}>@{data.username}</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 10, maxWidth: 480 }}>{data.bio}</p>

            {/* Quick stats row */}
            <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
              {[
                { label: 'Followers', value: formatNumber(data.followerCount) },
                { label: 'Following', value: formatNumber(data.followingCount) },
                { label: 'Posts', value: String(data.postCount) },
                { label: 'Account Age', value: data.accountAge },
              ].map(s => (
                <div key={s.label}>
                  <div style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)' }}>{s.value}</div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Status badge */}
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
            padding: '1.25rem 1.75rem', borderRadius: 20,
            background: cfg.bg, border: `1.5px solid ${cfg.border}`,
            boxShadow: `0 0 24px ${cfg.color}30`,
            textAlign: 'center', flexShrink: 0,
          }}>
            <span style={{ fontSize: '2.5rem', lineHeight: 1 }}>{cfg.emoji}</span>
            <span style={{ fontWeight: 800, fontSize: '0.95rem', color: cfg.color, letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>{cfg.label}</span>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', maxWidth: 120, textAlign: 'center', lineHeight: 1.4 }}>{cfg.tagline}</span>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════
          SECTION B + C: Trust Score & Summary
      ══════════════════════════════════════════════════ */}
      <div className="results-score-row">

        {/* Trust Score */}
        <div className="results-card results-score-card">
          <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '1.25rem', textAlign: 'center' }}>
            Safety Rating
          </div>
          <TrustScoreCircle score={data.trustScore} color={cfg.ringColor} />
          <div style={{ marginTop: '1.5rem' }}>
            <RiskMeter score={data.trustScore} />
          </div>
        </div>

        {/* Safety Summary */}
        <div className="results-card results-summary-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1rem' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: cfg.bg, border: `1px solid ${cfg.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>
              🔍
            </div>
            <h3 style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>What We Found</h3>
          </div>
          <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.75, fontWeight: 450 }}>
            {data.safetySummary}
          </p>
          {data.warningIndicators.length === 0 && (
            <div style={{
              marginTop: '1.25rem', padding: '0.9rem 1.1rem',
              background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)',
              borderRadius: 12, fontSize: '0.85rem', fontWeight: 600, color: '#10b981',
              display: 'flex', alignItems: 'center', gap: 8,
            }}>
              ✅ No warning signs were detected for this account.
            </div>
          )}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════
          SECTION D: Warning Signs
      ══════════════════════════════════════════════════ */}
      {data.warningIndicators.length > 0 && (
        <div className="results-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>
              ⚠️
            </div>
            <div>
              <h3 style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
                Warning Signs Found
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>
                {data.warningIndicators.length} issue{data.warningIndicators.length !== 1 ? 's' : ''} detected
              </p>
            </div>
          </div>

          <div className="warning-grid">
            {data.warningIndicators.map((w, i) => (
              <div key={i} className="warning-card" style={{
                borderColor: severityBorder[w.severity],
                background: severityBg[w.severity],
              }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                  <span style={{ fontSize: '1.5rem', lineHeight: 1, flexShrink: 0, marginTop: 2 }}>{w.icon}</span>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{w.label}</span>
                      <span style={{
                        fontSize: '0.62rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em',
                        padding: '2px 8px', borderRadius: 999,
                        background: severityBg[w.severity], color: severityColor[w.severity],
                        border: `1px solid ${severityBorder[w.severity]}`,
                      }}>
                        {w.severity === 'high' ? '⚠ High' : w.severity === 'medium' ? '● Medium' : '○ Low'}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{w.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════
          SECTION E: Recommended Actions
      ══════════════════════════════════════════════════ */}
      <div className="results-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(37,99,235,0.08)', border: '1px solid rgba(37,99,235,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>
            💡
          </div>
          <h3 style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            What Should You Do?
          </h3>
        </div>

        <div className="action-list">
          {data.recommendations.map((rec, i) => (
            <div key={i} className="action-item">
              <div className="action-check">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{rec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════
          SECTION F: Download Report
      ══════════════════════════════════════════════════ */}
      <div className="results-download-bar">
        <div>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: 2 }}>
            Save this report
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Download a simple text summary you can share or keep for your records
          </div>
        </div>
        <button
          id="download-report-btn"
          className="btn-analyze"
          onClick={downloadReport}
          style={{ flexShrink: 0, padding: '0.7rem 1.5rem', fontSize: '0.88rem' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download Report
        </button>
      </div>

      {/* Disclaimer */}
      <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.6, marginTop: '0.5rem', maxWidth: 600, margin: '1rem auto 0' }}>
        ⚠️ Results are based on publicly available signals and are for informational purposes only. Always use your own judgement when interacting with unfamiliar accounts online.
      </p>

    </div>
  );
};
