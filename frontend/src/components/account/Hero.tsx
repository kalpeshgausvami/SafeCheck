import React, { useEffect, useRef } from 'react';
import type { ExampleKey } from '../mockData';

interface HeroProps {
  username: string;
  setUsername: (u: string) => void;
  onAnalyze: () => void;
  onSelectExample: (key: ExampleKey) => void;
}

const examples: { key: ExampleKey; emoji: string; label: string; status: string; statusColor: string; bg: string; desc: string }[] = [
  {
    key: 'danger',
    emoji: '🛍️',
    label: '@tech_shop_deals',
    status: 'High Risk',
    statusColor: '#ef4444',
    bg: 'rgba(239,68,68,0.07)',
    desc: 'A suspicious store account with very few followers and crypto payment requests.',
  },
  {
    key: 'safe',
    emoji: '🍜',
    label: '@food_blogger_maya',
    status: 'Safe Account',
    statusColor: '#10b981',
    bg: 'rgba(16,185,129,0.07)',
    desc: 'A genuine food blogger with 4 years of activity and 84K real followers.',
  },
  {
    key: 'caution',
    emoji: '📈',
    label: '@crypto_gains_daily',
    status: 'Needs Attention',
    statusColor: '#f59e0b',
    bg: 'rgba(245,158,11,0.07)',
    desc: 'Promises unrealistic daily earnings — common in financial scam accounts.',
  },
];

export const Hero: React.FC<HeroProps> = ({ username, setUsername, onAnalyze, onSelectExample }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    const resize = () => { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; };
    resize();
    window.addEventListener('resize', resize);

    // Subtle floating dots
    const dots: { x: number; y: number; r: number; dx: number; dy: number; alpha: number }[] = [];
    for (let i = 0; i < 40; i++) {
      dots.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.8 + 0.4,
        dx: (Math.random() - 0.5) * 0.3,
        dy: (Math.random() - 0.5) * 0.3,
        alpha: Math.random() * 0.35 + 0.1,
      });
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const isDark = document.body.classList.contains('dark');
      const color = isDark ? '16,185,129' : '37,99,235';

      dots.forEach(p => {
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color},${p.alpha})`;
        ctx.fill();
      });

      for (let i = 0; i < dots.length; i++) {
        for (let j = i + 1; j < dots.length; j++) {
          const dist = Math.hypot(dots[i].x - dots[j].x, dots[i].y - dots[j].y);
          if (dist < 90) {
            ctx.beginPath();
            ctx.moveTo(dots[i].x, dots[i].y);
            ctx.lineTo(dots[j].x, dots[j].y);
            ctx.strokeStyle = `rgba(${color},${0.08 * (1 - dist / 90)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize); };
  }, []);

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); if (username.trim()) onAnalyze(); };

  return (
    <section style={{ textAlign: 'center', maxWidth: 860, margin: '0 auto 5rem auto', position: 'relative' }}>
      <canvas ref={canvasRef} style={{
        position: 'absolute', inset: 0, width: '100%', height: '100%',
        pointerEvents: 'none', zIndex: 0, borderRadius: 32,
      }} />

      <div style={{ position: 'relative', zIndex: 1 }}>

        {/* Shield badge */}
        <div className="hero-badge" style={{ marginBottom: '1.75rem' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Free Account Safety Checker · Instant Results</span>
        </div>

        {/* Headline */}
        <h1 className="hero-title" style={{ marginBottom: '1.1rem' }}>
          Is This Instagram Account Safe?
        </h1>

        {/* Subtitle */}
        <p className="hero-subtitle" style={{ marginBottom: '2.5rem' }}>
          Check any account for scams, fake profiles, and suspicious activity.<br />
          <strong style={{ color: 'var(--primary)', fontWeight: 700 }}>No technical knowledge needed</strong> — results in seconds.
        </p>

        {/* Stats bar */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1px', marginBottom: '2.25rem', flexWrap: 'wrap' }}>
          {[
            { label: 'Accounts Checked', value: '2M+' },
            { label: 'Accuracy', value: '97%' },
            { label: 'Detection Time', value: '~10s' },
          ].map(({ label, value }, i) => (
            <div key={label} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 22px',
              background: 'var(--bg-glass-strong)',
              backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-color)',
              borderRadius: i === 0 ? '14px 0 0 14px' : i === 2 ? '0 14px 14px 0' : '0',
              boxShadow: 'var(--shadow-md)',
            }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
              <span style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>{value}</span>
            </div>
          ))}
        </div>

        {/* Search box */}
        <form onSubmit={handleSubmit} className="search-container" style={{ maxWidth: 680, margin: '0 auto 1rem auto' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            marginLeft: '0.75rem', flexShrink: 0,
            color: 'var(--primary)', fontWeight: 700, fontSize: '1.05rem',
          }}>
            @
          </div>
          <input
            type="text"
            className="search-input"
            placeholder="Enter an Instagram username…"
            value={username}
            onChange={e => setUsername(e.target.value.replace('@', ''))}
            aria-label="Instagram username"
          />
          <button type="submit" className="btn-analyze" disabled={!username.trim()} id="check-account-btn">
            <span>Check Account</span>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </button>
        </form>

        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '3.5rem' }}>
          Free to use · No sign-in required · Results are for informational purposes only
        </p>

        {/* Example cards */}
        <div>
          <h3 className="example-title">Try these example accounts</h3>
          <div className="example-grid" style={{ maxWidth: 880, margin: '0 auto' }}>
            {examples.map(ex => (
              <div
                key={ex.key}
                className="example-card"
                onClick={() => onSelectExample(ex.key)}
                id={`example-${ex.key}`}
                style={{ '--card-glow': ex.statusColor + '30', textAlign: 'left' } as React.CSSProperties}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ fontSize: '1.8rem' }}>{ex.emoji}</div>
                  <span style={{
                    fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase',
                    padding: '3px 10px', borderRadius: 999,
                    background: ex.bg, color: ex.statusColor,
                    border: `1px solid ${ex.statusColor}40`, letterSpacing: '0.06em',
                  }}>
                    {ex.status}
                  </span>
                </div>

                <div style={{ fontWeight: 800, fontSize: '0.97rem', color: 'var(--text-primary)', marginBottom: 5, letterSpacing: '-0.01em' }}>
                  {ex.label}
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                  {ex.desc}
                </p>

                <div style={{
                  marginTop: 14, paddingTop: 12,
                  borderTop: '1px solid var(--border-color)',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  fontSize: '0.78rem', fontWeight: 700, color: 'var(--primary)',
                }}>
                  <span>Analyze Account</span>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
