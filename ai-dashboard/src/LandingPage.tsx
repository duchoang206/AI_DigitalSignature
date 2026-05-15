import { motion } from 'framer-motion';
import { ArrowRight, Shield, Lock, Cpu } from 'lucide-react';
import './index.css';

interface LandingPageProps {
  onEnter: () => void;
}

export default function LandingPage({ onEnter }: LandingPageProps) {
  return (
    <div className="landing-container">
      {/* Background Gradients */}
      <div className="ambient-light-1"></div>
      <div className="ambient-light-2"></div>

      <header className="landing-header">
        <div className="brand">
          <div className="ms-logo" style={{ transform: 'scale(1.2)' }}>
            <div className="tl"></div><div className="tr"></div>
            <div className="bl"></div><div className="br"></div>
          </div>
          <span className="brand-text" style={{marginLeft: '12px'}}>Surfacecity AI</span>
        </div>
        <nav className="landing-nav">
          <a href="#features">Features</a>
          <a href="#security">Security</a>
          <a href="#about">About</a>
        </nav>
        <button className="nav-cta" onClick={onEnter}>Sign In</button>
      </header>

      <main className="landing-main">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="hero-section"
        >
          <div className="hero-badge">
            <span className="badge-dot"></span>
            Next-Gen Cryptography Protocol v2.0
          </div>
          
          <h1 className="hero-title">
            Securing the Future<br />with AI-Driven Cryptography.
          </h1>
          
          <p className="hero-subtitle">
            Unleash the power of Elliptic Curve Digital Signatures combined with real-time AI anomaly detection. Protect your identity, secure your documents, and neutralize threats instantly.
          </p>

          <div className="hero-actions">
            <button className="primary-cta" onClick={onEnter}>
              Enter Dashboard <ArrowRight size={20} />
            </button>
            <button className="secondary-cta">
              View Documentation
            </button>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          className="features-preview"
        >
          <div className="feature-card linear-card">
            <div className="feature-icon"><Lock size={24} /></div>
            <h3>Biometric ECDSA</h3>
            <p>Zero-click face authentication seamlessly integrated with ECDSA signing.</p>
          </div>
          <div className="feature-card linear-card">
            <div className="feature-icon"><Shield size={24} /></div>
            <h3>AI Threat Guardian</h3>
            <p>Isolation Forest algorithm protecting endpoints from DDoS and intrusions.</p>
          </div>
          <div className="feature-card linear-card">
            <div className="feature-icon"><Cpu size={24} /></div>
            <h3>Neural Copilot</h3>
            <p>Intelligent assistant for rapid workflow execution and anti-spoofing.</p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
