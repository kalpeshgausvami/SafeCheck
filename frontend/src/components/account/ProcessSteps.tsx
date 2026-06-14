import React from 'react';

const STEPS = [
  {
    num: '1',
    icon: '🔤',
    title: 'Enter a Username',
    desc: 'Type any Instagram username into the search bar and click "Check Account".',
  },
  {
    num: '2',
    icon: '🔍',
    title: 'We Analyze the Account',
    desc: 'Our system checks the account for warning signs, unusual patterns, and suspicious behaviour.',
  },
  {
    num: '3',
    icon: '🛡️',
    title: 'Get Your Safety Report',
    desc: 'See a clear, plain-English result: Safe, Needs Attention, or High Risk — with simple explanations.',
  },
  {
    num: '4',
    icon: '✅',
    title: 'Take the Right Action',
    desc: 'Follow our recommended steps to stay safe — whether to trust, verify, or report the account.',
  },
];

export const ProcessSteps: React.FC = () => {
  return (
    <section id="how-it-works" className="process-card" style={{ marginBottom: '4rem' }}>
      <div className="process-header">
        <h3>How It Works</h3>
        <p>Four simple steps to find out if an account is safe</p>
      </div>

      <div className="process-steps">
        {STEPS.map(step => (
          <div key={step.num} className="process-step">
            <div className="step-num">{step.icon}</div>
            <div className="step-title">{step.title}</div>
            <p className="step-desc">{step.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
