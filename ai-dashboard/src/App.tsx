import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, Bell, Settings, Shield, Cpu, 
  Activity, Users, Zap, AlertTriangle, 
  CheckCircle, Database, Lock, Terminal, Key
} from 'lucide-react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  // Digital Signature State
  const [sigMsg, setSigMsg] = useState('hello world');
  const [sigPriv, setSigPriv] = useState('');
  const [sigPubX, setSigPubX] = useState('');
  const [sigPubY, setSigPubY] = useState('');
  const [sigR, setSigR] = useState('');
  const [sigS, setSigS] = useState('');
  const [sigResult, setSigResult] = useState('');
  
  // AI Guardian State
  const [guardIp, setGuardIp] = useState('192.168.1.100');
  const [guardMsg, setGuardMsg] = useState('sign_request');
  const [guardSuccess, setGuardSuccess] = useState(true);
  const [guardResult, setGuardResult] = useState<any>(null);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { type: 'spring', stiffness: 100 } }
  };

  // API Calls
  const generateKeys = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/sig/keys', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ curve: 'secp112r1', algo: 'ECDSA' })
      });
      const data = await res.json();
      if (data.success) {
        setSigPriv(data.private_key);
        setSigPubX(data.public_key.x);
        setSigPubY(data.public_key.y);
        setSigResult(`Keys generated in ${data.time_ms}ms`);
      }
    } catch (e) { setSigResult('Error generating keys'); }
  };

  const signMessage = async () => {
    if (!sigPriv) return alert('Generate keys first');
    try {
      const res = await fetch('http://localhost:5000/api/sig/sign', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: sigMsg, private_key: sigPriv, curve: 'secp112r1', algo: 'ECDSA' })
      });
      const data = await res.json();
      if (data.success) {
        setSigR(data.signature.r);
        setSigS(data.signature.s);
        setSigResult(`Message signed in ${data.time_ms}ms`);
      }
    } catch (e) { setSigResult('Error signing message'); }
  };

  const verifySignature = async () => {
    if (!sigR || !sigS) return alert('Sign a message first');
    try {
      const res = await fetch('http://localhost:5000/api/sig/verify', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: sigMsg, r: sigR, s: sigS, qx: sigPubX, qy: sigPubY, curve: 'secp112r1', algo: 'ECDSA' })
      });
      const data = await res.json();
      if (data.success) {
        setSigResult(data.valid ? `✅ Valid Signature (${data.time_ms}ms)` : `❌ Invalid Signature (${data.time_ms}ms)`);
      }
    } catch (e) { setSigResult('Error verifying signature'); }
  };

  const checkGuardian = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/guard/check', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: guardIp, message: guardMsg, success: guardSuccess })
      });
      const data = await res.json();
      if (data.success) {
        setGuardResult(data);
      }
    } catch (e) { alert('Error contacting AI Guardian API'); }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <motion.header className="header glass-panel" initial={{ y: -50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
        <div className="brand">
          <div className="brand-logo">
            <div className="ms-logo">
              <div className="tl"></div><div className="tr"></div>
              <div className="bl"></div><div className="br"></div>
            </div>
            <span className="brand-text">Microsoft | Surfacecity</span>
          </div>
          <div className="brand-subtitle">
            <div>AI Digital Signature</div>
            <div className="brand-subtext">Security Engine</div>
          </div>
        </div>

        <div className="search-bar">
          <Search size={18} color="rgba(255,255,255,0.5)" />
          <input type="text" placeholder="Search devices, models, threats..." />
        </div>

        <div className="header-actions">
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} className="icon-btn"><Bell size={20} /></motion.button>
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} className="icon-btn"><Settings size={20} /></motion.button>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg, #00d2ff, #3a7bd5)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', marginLeft: '8px', cursor: 'pointer' }}>
            A
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="main-content">
        {/* Sidebar */}
        <motion.aside className="sidebar glass-panel" initial={{ x: -50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <div className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}><Activity size={20} /><span>Overview</span></div>
          <div className={`nav-item ${activeTab === 'digital_signature' ? 'active' : ''}`} onClick={() => setActiveTab('digital_signature')}><Lock size={20} /><span>Digital Signature</span></div>
          <div className={`nav-item ${activeTab === 'ai_guardian' ? 'active' : ''}`} onClick={() => setActiveTab('ai_guardian')}><Shield size={20} /><span>AI IP Guardian</span></div>
        </motion.aside>

        {/* Dashboard Content */}
        <motion.main className="dashboard" variants={containerVariants} initial="hidden" animate="visible">
          
          {activeTab === 'overview' && (
            <>
              <div className="dashboard-header">
                <div className="dashboard-title">
                  <h1>System Intelligence Overview</h1>
                  <p>Real-time monitoring of Microsoft Surface City AI endpoints</p>
                </div>
                <motion.button className="primary-btn" whileHover={{ scale: 1.05, boxShadow: "0 8px 25px rgba(0, 210, 255, 0.4)" }} whileTap={{ scale: 0.95 }}><Zap size={18} />Run Diagnostics</motion.button>
              </div>

              <div className="stats-grid">
                <motion.div variants={itemVariants} className="stat-card glass-card">
                  <div className="stat-header"><span>Active Surface Devices</span><div className="stat-icon"><Terminal size={20} /></div></div>
                  <h3 className="stat-value">1,492</h3>
                  <div className="stat-change positive"><span>+12.5%</span> from last week</div>
                </motion.div>
                <motion.div variants={itemVariants} className="stat-card glass-card">
                  <div className="stat-header"><span>Signatures Verified</span><div className="stat-icon"><Lock size={20} /></div></div>
                  <h3 className="stat-value">845,201</h3>
                  <div className="stat-change positive"><span>+5.2%</span> from last week</div>
                </motion.div>
                <motion.div variants={itemVariants} className="stat-card glass-card">
                  <div className="stat-header"><span>Threats Blocked</span><div className="stat-icon" style={{ color: '#ff3366', background: 'rgba(255, 51, 102, 0.1)' }}><Shield size={20} /></div></div>
                  <h3 className="stat-value">3,829</h3>
                  <div className="stat-change negative"><span>-2.4%</span> from last week</div>
                </motion.div>
                <motion.div variants={itemVariants} className="stat-card glass-card">
                  <div className="stat-header"><span>AI Model Accuracy</span><div className="stat-icon"><Cpu size={20} /></div></div>
                  <h3 className="stat-value">99.8%</h3>
                  <div className="stat-change positive"><span>Stable</span> network</div>
                </motion.div>
              </div>

              <div className="details-grid">
                <motion.div variants={itemVariants} className="chart-card glass-card">
                  <h3 className="card-title">Network Activity & Verification Load</h3>
                  <div className="fake-chart">
                    <svg width="100%" height="100%" preserveAspectRatio="none" viewBox="0 0 100 100">
                      <path d="M0,80 Q10,60 20,70 T40,40 T60,60 T80,20 T100,30 L100,100 L0,100 Z" fill="rgba(0, 210, 255, 0.1)" stroke="none"/>
                      <path d="M0,80 Q10,60 20,70 T40,40 T60,60 T80,20 T100,30" fill="none" stroke="#00d2ff" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                  </div>
                </motion.div>
                <motion.div variants={itemVariants} className="glass-card">
                  <h3 className="card-title">Recent Alerts</h3>
                  <div className="activity-list">
                    <motion.div className="activity-item" whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.02)' }}>
                      <div className="activity-icon" style={{ color: '#ffcc00', background: 'rgba(255, 204, 0, 0.1)' }}><AlertTriangle size={18} /></div>
                      <div className="activity-details"><h4>Anomalous Signature</h4><p>Surface Pro 11 - IP: 192.168.1.45</p></div>
                      <div className="activity-time">2m ago</div>
                    </motion.div>
                  </div>
                </motion.div>
              </div>
            </>
          )}

          {activeTab === 'digital_signature' && (
            <motion.div variants={itemVariants} className="algorithm-container glass-card">
              <h2 className="card-title" style={{ fontSize: '1.8rem', marginBottom: '24px' }}>ECDSA Digital Signature</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label>Message to Sign</label>
                  <textarea value={sigMsg} onChange={e => setSigMsg(e.target.value)} rows={4} className="form-control" />
                </div>
                
                <div className="form-group">
                  <label>Private Key (d)</label>
                  <input readOnly value={sigPriv} className="form-control mono-font" placeholder="Generated Private Key" />
                </div>
                
                <div className="form-group">
                  <label>Public Key (Qx, Qy)</label>
                  <input readOnly value={sigPubX ? `X: ${sigPubX} | Y: ${sigPubY}` : ''} className="form-control mono-font" placeholder="Generated Public Key" />
                </div>

                <div className="form-group">
                  <label>Signature (r, s)</label>
                  <input readOnly value={sigR ? `R: ${sigR} | S: ${sigS}` : ''} className="form-control mono-font" placeholder="Generated Signature" />
                </div>

                <div className="btn-group">
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn gen-btn" onClick={generateKeys}><Key size={18} /> Generate Keys</motion.button>
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn sign-btn" onClick={signMessage}><Lock size={18} /> Sign</motion.button>
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn verify-btn" onClick={verifySignature}><CheckCircle size={18} /> Verify</motion.button>
                </div>

                {sigResult && (
                  <div className="result-box">
                    <strong>Result:</strong> {sigResult}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'ai_guardian' && (
            <motion.div variants={itemVariants} className="algorithm-container glass-card">
              <h2 className="card-title" style={{ fontSize: '1.8rem', marginBottom: '24px' }}>AI IP Guardian (Isolation Forest)</h2>
              <div className="form-grid">
                <div style={{ display: 'flex', gap: '16px' }}>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>IP Address</label>
                    <input value={guardIp} onChange={e => setGuardIp(e.target.value)} className="form-control mono-font" />
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>Action Message</label>
                    <input value={guardMsg} onChange={e => setGuardMsg(e.target.value)} className="form-control mono-font" />
                  </div>
                  <div className="form-group" style={{ display: 'flex', alignItems: 'center', paddingTop: '24px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', margin: 0 }}>
                      <input type="checkbox" checked={guardSuccess} onChange={e => setGuardSuccess(e.target.checked)} style={{ width: '20px', height: '20px' }} />
                      Success Status
                    </label>
                  </div>
                </div>

                <div className="btn-group">
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn sign-btn" onClick={checkGuardian}><Shield size={18} /> Check IP Anomaly</motion.button>
                </div>

                {guardResult && (
                  <div className={`result-box ${guardResult.result.status}`}>
                    <h4>Check Result: {guardResult.result.status.toUpperCase()}</h4>
                    <p><strong>Reason:</strong> {guardResult.result.reason} (Layer: {guardResult.result.layer})</p>
                    <p><strong>Anomaly Score:</strong> {guardResult.result.score.toFixed(3)}</p>
                    <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '12px 0' }} />
                    <h5>IP Stats History:</h5>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      <li>Total Requests: {guardResult.stats.total}</li>
                      <li>Fail Rate: {(guardResult.stats.fail_rate * 100).toFixed(1)}%</li>
                      <li>Currently Blocked: {guardResult.stats.is_blocked ? 'Yes 🚫' : 'No ✅'}</li>
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}

        </motion.main>
      </div>
    </div>
  );
}

export default App;
