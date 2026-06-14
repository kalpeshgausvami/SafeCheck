import React, { useState, useEffect } from 'react';
import { ShieldCheck, Search, Sun, Moon } from 'lucide-react';

type AppMode = 'account' | 'factcheck';

interface NavbarProps {
  activeMode: AppMode;
  onSwitchMode: (mode: AppMode) => void;
  onNavigateHome: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeMode, onSwitchMode, onNavigateHome, theme, onToggleTheme }) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className="app-header"
      style={{ boxShadow: scrolled ? '0 4px 32px rgba(0,0,0,0.1)' : undefined }}
    >
      {/* Brand */}
      <div className="header-logo" onClick={onNavigateHome} id="nav-home-logo" style={{ flexShrink: 0 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: 'var(--gradient-primary)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 16px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.25)',
          flexShrink: 0,
        }}>
          <ShieldCheck style={{ width: 20, height: 20, color: '#fff' }} />
        </div>
        <span style={{ letterSpacing: '-0.03em', fontSize: '1.05rem' }}>
          Safe<span style={{ color: 'var(--primary)' }}>Check</span>
        </span>
      </div>

      {/* Mode switcher — center pill */}
      <div style={{
        display: 'flex', alignItems: 'center',
        background: 'var(--bg-input)',
        border: '1px solid var(--border-color)',
        borderRadius: 12, padding: 4, gap: 2,
      }}>
        <button
          id="mode-account-btn"
          onClick={() => onSwitchMode('account')}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '7px 14px', borderRadius: 9,
            border: 'none',
            background: activeMode === 'account' ? 'var(--bg-glass-strong)' : 'transparent',
            color: activeMode === 'account' ? 'var(--primary)' : 'var(--text-secondary)',
            fontFamily: 'var(--font-sans)', fontSize: '0.84rem', fontWeight: 700,
            cursor: 'pointer', transition: 'all 0.22s cubic-bezier(0.4,0,0.2,1)',
            boxShadow: activeMode === 'account' ? 'var(--shadow-sm)' : 'none',
            whiteSpace: 'nowrap',
          }}
        >
          <ShieldCheck style={{ width: 14, height: 14 }} />
          <span>Account Safety</span>
        </button>

        <button
          id="mode-factcheck-btn"
          onClick={() => onSwitchMode('factcheck')}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '7px 14px', borderRadius: 9,
            border: 'none',
            background: activeMode === 'factcheck' ? 'var(--bg-glass-strong)' : 'transparent',
            color: activeMode === 'factcheck' ? 'var(--primary)' : 'var(--text-secondary)',
            fontFamily: 'var(--font-sans)', fontSize: '0.84rem', fontWeight: 700,
            cursor: 'pointer', transition: 'all 0.22s cubic-bezier(0.4,0,0.2,1)',
            boxShadow: activeMode === 'factcheck' ? 'var(--shadow-sm)' : 'none',
            whiteSpace: 'nowrap',
          }}
        >
          <Search style={{ width: 14, height: 14 }} />
          <span>Fact Checker</span>
        </button>
      </div>

      {/* Right: theme toggle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
        <button
          onClick={onToggleTheme}
          title="Toggle theme"
          aria-label="Toggle light/dark theme"
          id="theme-toggle-btn"
          style={{
            position: 'relative', display: 'inline-flex',
            height: 30, width: 54, alignItems: 'center',
            borderRadius: 999, padding: '0 3px', cursor: 'pointer',
            border: theme === 'dark' ? '1px solid rgba(99,102,241,0.4)' : '1px solid rgba(37,99,235,0.25)',
            background: theme === 'dark' ? 'linear-gradient(135deg,#0a0a14,#12121e)' : 'linear-gradient(135deg,#dbeafe,#eff6ff)',
            transition: 'all 0.3s cubic-bezier(0.4,0,0.2,1)', outline: 'none',
          }}
        >
          <span style={{
            display: 'flex', width: 22, height: 22, alignItems: 'center', justifyContent: 'center', borderRadius: '50%',
            transform: theme === 'dark' ? 'translateX(22px)' : 'translateX(0)',
            transition: 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1)',
            background: theme === 'dark' ? 'linear-gradient(135deg,#6366f1,#818cf8)' : 'linear-gradient(135deg,#2563eb,#3b82f6)',
            boxShadow: theme === 'dark' ? '0 2px 8px rgba(99,102,241,0.5)' : '0 2px 8px rgba(37,99,235,0.45)',
          }}>
            {theme === 'dark' ? <Moon style={{ width: 12, height: 12, color: '#fff' }} /> : <Sun style={{ width: 12, height: 12, color: '#fff' }} />}
          </span>
        </button>
      </div>
    </header>
  );
};
