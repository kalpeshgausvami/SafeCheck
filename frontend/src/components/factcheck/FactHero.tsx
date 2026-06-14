import React, { useRef, useEffect, useState } from 'react';
import type { FactExampleKey } from '../factCheckData';
import { isInstagramReelUrl } from '../factCheckData';

interface FactHeroProps {
  reelUrl: string;
  setReelUrl: (u: string) => void;
  onAnalyze: () => void;
  onSelectExample: (key: FactExampleKey) => void;
}

const examples: {
  key: FactExampleKey; emoji: string; label: string;
  account: string; desc: string; verdict: string; verdictColor: string; bg: string;
}[] = [
  {
    key: 'health',
    emoji: '🍋',
    label: 'Lemon water cures cancer in 3 days',
    account: '@natural_health_tips',
    desc: 'A reel claiming hot lemon water destroys cancer cells and advising viewers to stop chemotherapy.',
    verdict: 'FALSE',
    verdictColor: '#ef4444',
    bg: 'rgba(239,68,68,0.07)',
  },
  {
    key: 'tech',
    emoji: '🏢',
    label: 'Transparent solar glass for skyscrapers',
    account: '@sciencedailyfeed',
    desc: 'A reel about see-through solar windows that can turn entire buildings into solar generators.',
    verdict: 'TRUE',
    verdictColor: '#10b981',
    bg: 'rgba(16,185,129,0.07)',
  },
  {
    key: 'conspiracy',
    emoji: '📡',
    label: '5G towers secretly installed to harm people',
    account: '@truth_uncensored',
    desc: 'A reel claiming 5G towers were secretly installed during COVID lockdowns to cause cancer.',
    verdict: 'PARTLY TRUE',
    verdictColor: '#f59e0b',
    bg: 'rgba(245,158,11,0.07)',
  },
];

// Validate URL on keystroke
function getUrlState(url: string): 'empty' | 'invalid' | 'valid' {
  if (!url.trim()) return 'empty';
  if (isInstagramReelUrl(url)) return 'valid';
  if (url.includes('instagram') || url.includes('reel')) return 'invalid';
  if (url.length > 8) return 'invalid';
  return 'empty';
}

export const FactHero: React.FC<FactHeroProps> = ({ reelUrl, setReelUrl, onAnalyze, onSelectExample }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const urlState = getUrlState(reelUrl);
  const [pasted, setPasted] = useState(false);

  // Particle canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    let animId: number;
    const resize = () => { canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; };
    resize();
    window.addEventListener('resize', resize);
    const dots: { x: number; y: number; r: number; dx: number; dy: number; alpha: number }[] = [];
    for (let i = 0; i < 36; i++) {
      dots.push({ x: Math.random() * (canvas.width || 800), y: Math.random() * (canvas.height || 500), r: Math.random() * 1.6 + 0.3, dx: (Math.random() - 0.5) * 0.28, dy: (Math.random() - 0.5) * 0.28, alpha: Math.random() * 0.28 + 0.08 });
    }
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const isDark = document.body.classList.contains('dark');
      const col = isDark ? '99,102,241' : '37,99,235';
      dots.forEach(p => {
        p.x += p.dx; p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${col},${p.alpha})`; ctx.fill();
      });
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', resize); };
  }, []);

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); if (urlState === 'valid') onAnalyze(); };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pasted = e.clipboardData.getData('text');
    if (isInstagramReelUrl(pasted)) { setPasted(true); setTimeout(() => setPasted(false), 2000); }
  };

  return (
    <section style={{ textAlign: 'center', maxWidth: 860, margin: '0 auto 5rem auto', position: 'relative' }}>
      <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 0, borderRadius: 32 }} />

      <div style={{ position: 'relative', zIndex: 1 }}>

        {/* Instagram Reels badge */}
        <div className="hero-badge" style={{ marginBottom: '1.75rem' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
            <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
            <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
          </svg>
          <span>Instagram Reel Fact Checker · Paste Any Reel Link</span>
        </div>

        {/* Headline */}
        <h1 className="hero-title" style={{ marginBottom: '1.1rem' }}>
          Is This Reel True or False?
        </h1>
        <p className="hero-subtitle" style={{ marginBottom: '2.5rem' }}>
          Paste any Instagram Reel link. We'll extract the claim inside the video<br /> and tell you if it's <strong style={{ color: '#10b981', fontWeight: 700 }}>True</strong>, <strong style={{ color: '#ef4444', fontWeight: 700 }}>False</strong>, or <strong style={{ color: '#f59e0b', fontWeight: 700 }}>Partially True</strong> — in plain English.
        </p>

        {/* Stats bar */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1px', marginBottom: '2.25rem', flexWrap: 'wrap' }}>
          {[
            { label: 'Reels Checked', value: '500K+' },
            { label: 'Verdict Accuracy', value: '96%' },
            { label: 'Analysis Time', value: '~12s' },
          ].map(({ label, value }, i) => (
            <div key={label} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 22px',
              background: 'var(--bg-glass-strong)', backdropFilter: 'blur(16px)',
              border: '1px solid var(--border-color)',
              borderRadius: i === 0 ? '14px 0 0 14px' : i === 2 ? '0 14px 14px 0' : '0',
              boxShadow: 'var(--shadow-md)',
            }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
              <span style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>{value}</span>
            </div>
          ))}
        </div>

        {/* URL Input */}
        <form onSubmit={handleSubmit} style={{ maxWidth: 700, margin: '0 auto 0.75rem auto' }}>
          <div className={`reel-url-box${urlState === 'valid' ? ' reel-url-box--valid' : urlState === 'invalid' ? ' reel-url-box--invalid' : ''}`}>
            {/* Instagram icon prefix */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0, paddingLeft: 4 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 9, flexShrink: 0,
                background: 'linear-gradient(135deg, #f58529, #dd2a7b, #8134af)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
                </svg>
              </div>
            </div>

            <input
              type="url"
              className="reel-url-input"
              placeholder="https://www.instagram.com/reel/ABC123xyz/"
              value={reelUrl}
              onChange={e => setReelUrl(e.target.value)}
              onPaste={handlePaste}
              aria-label="Instagram Reel URL"
              id="reel-url-input"
              spellCheck={false}
              autoComplete="off"
            />

            {/* Validation icon */}
            <div style={{ flexShrink: 0, display: 'flex', alignItems: 'center', paddingRight: 4 }}>
              {urlState === 'valid' && (
                <span style={{ fontSize: '1.1rem', animation: 'verdictPop 0.3s ease both' }}>✅</span>
              )}
              {urlState === 'invalid' && (
                <span style={{ fontSize: '1.1rem' }}>❌</span>
              )}
            </div>

            <button
              type="submit"
              className="btn-analyze"
              disabled={urlState !== 'valid'}
              id="fact-check-reel-btn"
              style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem', flexShrink: 0 }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" />
              </svg>
              <span>Fact-Check Reel</span>
            </button>
          </div>
        </form>

        {/* Validation hint */}
        <div style={{ marginBottom: '2.5rem', height: 20 }}>
          {urlState === 'invalid' && (
            <p style={{ fontSize: '0.8rem', color: '#ef4444', fontWeight: 600, animation: 'fadeInUp 0.2s ease both' }}>
              ⚠️ Please paste a valid Instagram Reel link (e.g. instagram.com/reel/…)
            </p>
          )}
          {urlState === 'valid' && pasted && (
            <p style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 600, animation: 'fadeInUp 0.2s ease both' }}>
              ✅ Instagram Reel link detected — ready to check!
            </p>
          )}
          {urlState === 'empty' && (
            <p style={{ fontSize: '0.77rem', color: 'var(--text-muted)' }}>
              Free to use · No sign-in needed · Works on any public Instagram Reel
            </p>
          )}
        </div>

        {/* Example Reel cards */}
        <h3 className="example-title">Try these example reels</h3>
        <div className="example-grid" style={{ maxWidth: 880, margin: '0 auto' }}>
          {examples.map(ex => (
            <div
              key={ex.key}
              className="example-card"
              id={`reel-example-${ex.key}`}
              onClick={() => onSelectExample(ex.key)}
              style={{ '--card-glow': ex.verdictColor + '30', textAlign: 'left' } as React.CSSProperties}
            >
              {/* Mock reel thumbnail */}
              <div style={{
                width: '100%', height: 90, borderRadius: 12, marginBottom: 12,
                background: `linear-gradient(135deg, ${ex.verdictColor}18, ${ex.verdictColor}08)`,
                border: `1px solid ${ex.verdictColor}25`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                position: 'relative', overflow: 'hidden',
              }}>
                {/* Reel play button overlay */}
                <div style={{
                  position: 'absolute', inset: 0,
                  background: 'linear-gradient(135deg,rgba(0,0,0,0.06) 0%,rgba(0,0,0,0.02) 100%)',
                }}>
                  {/* Fake reel lines */}
                  {[20, 38, 55, 72].map(top => (
                    <div key={top} style={{
                      position: 'absolute', left: 14, right: 14, top,
                      height: 6, borderRadius: 4,
                      background: `${ex.verdictColor}20`,
                    }} />
                  ))}
                </div>
                <span style={{ fontSize: '2.8rem', position: 'relative', zIndex: 1 }}>{ex.emoji}</span>
                {/* Play icon */}
                <div style={{
                  position: 'absolute', bottom: 8, right: 10,
                  width: 24, height: 24, borderRadius: '50%',
                  background: 'rgba(0,0,0,0.45)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <svg width="9" height="9" viewBox="0 0 16 16" fill="#fff">
                    <polygon points="5,2 14,8 5,14" />
                  </svg>
                </div>
                {/* Account tag */}
                <div style={{
                  position: 'absolute', top: 8, left: 10,
                  background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(8px)',
                  borderRadius: 20, padding: '2px 8px',
                  fontSize: '0.64rem', fontWeight: 700, color: '#fff', letterSpacing: '0.01em',
                }}>
                  {ex.account}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  📹 Instagram Reel
                </span>
                <span style={{
                  fontSize: '0.65rem', fontWeight: 800, textTransform: 'uppercase',
                  padding: '3px 9px', borderRadius: 999,
                  background: ex.bg, color: ex.verdictColor,
                  border: `1px solid ${ex.verdictColor}40`, letterSpacing: '0.06em',
                }}>
                  {ex.verdict}
                </span>
              </div>

              <div style={{ fontWeight: 800, fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: 5, letterSpacing: '-0.01em', lineHeight: 1.35 }}>
                {ex.label}
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                {ex.desc}
              </p>

              <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.77rem', fontWeight: 700, color: 'var(--primary)' }}>
                <span>Fact-Check This Reel</span>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
                </svg>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};
