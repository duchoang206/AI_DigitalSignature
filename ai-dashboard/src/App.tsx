import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, Bell, Settings, Shield, Cpu, 
  Activity, Users, Zap, AlertTriangle, 
  CheckCircle, Database, Lock, Terminal, Key,
  UploadCloud, FileText
} from 'lucide-react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  // Digital Signature State
  const [sigPriv, setSigPriv] = useState('');
  const [sigPubX, setSigPubX] = useState('');
  const [sigPubY, setSigPubY] = useState('');
  const [sigR, setSigR] = useState('');
  const [sigS, setSigS] = useState('');
  const [sigResult, setSigResult] = useState('');
  const [sigMsg, setSigMsg] = useState('');
  
  // File states
  const [signFile, setSignFile] = useState<File | null>(null);
  const [verifyDocFile, setVerifyDocFile] = useState<File | null>(null);
  const [verifySigFile, setVerifySigFile] = useState<File | null>(null);
  
  // AI Guardian State
  const [guardIp, setGuardIp] = useState('192.168.1.100');
  const [guardMsg, setGuardMsg] = useState('sign_request');
  const [guardSuccess, setGuardSuccess] = useState(true);
  const [guardResult, setGuardResult] = useState<any>(null);

  // Simulation State
  const [isSimulating, setIsSimulating] = useState(false);
  const simulationRef = useRef<number | null>(null);

  // Helper: SHA-256 Hash File
  const calculateHash = async (file: File) => {
    const arrayBuffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

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

  const signDocument = async () => {
    if (!sigPriv) return alert('Generate keys first');
    if (!signFile) return alert('Please select a file to sign');
    try {
      const fileHash = await calculateHash(signFile);
      setSigMsg(`File: ${signFile.name}\nHash: ${fileHash}`);

      const res = await fetch('http://localhost:5000/api/sig/sign', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: fileHash, private_key: sigPriv, curve: 'secp112r1', algo: 'ECDSA' })
      });
      const data = await res.json();
      if (data.success) {
        setSigR(data.signature.r);
        setSigS(data.signature.s);
        setSigResult(`File signed successfully in ${data.time_ms}ms`);
        
        const sigData = {
          filename: signFile.name,
          hash: fileHash,
          r: data.signature.r,
          s: data.signature.s,
          qx: sigPubX,
          qy: sigPubY,
          curve: 'secp112r1',
          algo: 'ECDSA'
        };
        const blob = new Blob([JSON.stringify(sigData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${signFile.name.split('.')[0]}.sig`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) { setSigResult('Error signing document'); }
  };

  const verifyDocument = async () => {
    if (!verifyDocFile || !verifySigFile) return alert('Please upload both Document and .sig file');
    try {
      const sigText = await verifySigFile.text();
      const sigData = JSON.parse(sigText);
      const fileHash = await calculateHash(verifyDocFile);

      const res = await fetch('http://localhost:5000/api/sig/verify', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: fileHash, r: sigData.r, s: sigData.s, qx: sigData.qx, qy: sigData.qy, curve: sigData.curve || 'secp112r1', algo: sigData.algo || 'ECDSA' })
      });
      const data = await res.json();
      if (data.success) {
        setSigResult(data.valid 
          ? `✅ Verification Successful: Document is authentic (${data.time_ms}ms)` 
          : `❌ Verification Failed: Document has been tampered with! (${data.time_ms}ms)`);
      }
    } catch (e) { setSigResult('Error parsing signature file or verifying'); }
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

  const toggleSimulation = () => {
    if (isSimulating) {
      if (simulationRef.current) clearInterval(simulationRef.current);
      setIsSimulating(false);
    } else {
      setIsSimulating(true);
      simulationRef.current = window.setInterval(async () => {
        try {
          const res = await fetch('http://localhost:5000/api/guard/check', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: guardIp, message: 'DDoS_Attack_Simulation', success: false })
          });
          const data = await res.json();
          if (data.success) {
            setGuardResult(data);
          }
        } catch (e) {}
      }, 200);
    }
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
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <motion.div variants={itemVariants} className="algorithm-container glass-card" style={{ flex: 1, minWidth: '300px' }}>
                <h2 className="card-title" style={{ fontSize: '1.4rem', marginBottom: '16px' }}><Lock size={20} style={{display:'inline', marginRight:'8px', verticalAlign:'middle'}}/> Sign Document (Creator)</h2>
                <div className="form-grid">
                  <div className="form-group">
                    <label>1. Generate your Identity Keys</label>
                    <div className="btn-group" style={{marginTop:0}}>
                      <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn gen-btn" onClick={generateKeys}><Key size={18} /> Generate Keys</motion.button>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Private Key (Keep Secret!)</label>
                    <input readOnly value={sigPriv} className="form-control mono-font" placeholder="Generated Private Key" />
                  </div>
                  
                  <div className="form-group">
                    <label>2. Choose Document to Sign</label>
                    <div className="file-upload-zone">
                      <input type="file" id="signFileInput" onChange={(e) => setSignFile(e.target.files?.[0] || null)} style={{display: 'none'}} />
                      <label htmlFor="signFileInput" className="file-label">
                        <UploadCloud size={32} color="#00d2ff"/>
                        <span style={{color: '#fff'}}>{signFile ? signFile.name : "Select PDF or any file..."}</span>
                      </label>
                    </div>
                  </div>

                  <div className="btn-group">
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn sign-btn" onClick={signDocument}><FileText size={18} /> Sign & Download .sig</motion.button>
                  </div>
                </div>
              </motion.div>

              <motion.div variants={itemVariants} className="algorithm-container glass-card" style={{ flex: 1, minWidth: '300px' }}>
                <h2 className="card-title" style={{ fontSize: '1.4rem', marginBottom: '16px' }}><CheckCircle size={20} style={{display:'inline', marginRight:'8px', verticalAlign:'middle'}}/> Verify Document (Partner)</h2>
                <div className="form-grid">
                  
                  <div className="form-group">
                    <label>1. Upload Received Document</label>
                    <div className="file-upload-zone">
                      <input type="file" id="verifyDocInput" onChange={(e) => setVerifyDocFile(e.target.files?.[0] || null)} style={{display: 'none'}} />
                      <label htmlFor="verifyDocInput" className="file-label">
                        <UploadCloud size={32} color="#00d2ff"/>
                        <span style={{color: '#fff'}}>{verifyDocFile ? verifyDocFile.name : "Select received Document..."}</span>
                      </label>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>2. Upload Signature File (.sig)</label>
                    <div className="file-upload-zone">
                      <input type="file" accept=".sig,.json" id="verifySigInput" onChange={(e) => setVerifySigFile(e.target.files?.[0] || null)} style={{display: 'none'}} />
                      <label htmlFor="verifySigInput" className="file-label" style={{borderColor: '#ffcc00'}}>
                        <Lock size={32} color="#ffcc00"/>
                        <span style={{color: '#fff'}}>{verifySigFile ? verifySigFile.name : "Select .sig file..."}</span>
                      </label>
                    </div>
                  </div>

                  <div className="btn-group" style={{marginTop: 'auto'}}>
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn verify-btn" onClick={verifyDocument}><Shield size={18} /> Verify Authenticity</motion.button>
                  </div>
                </div>
              </motion.div>
              
              {sigResult && (
                <div style={{width: '100%'}}>
                  <div className={`result-box ${sigResult.includes('❌') ? 'block' : 'allow'}`} style={{ fontSize: '1.1rem', padding: '20px' }}>
                    <strong>Action Result:</strong><br/>{sigResult}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'ai_guardian' && (
            <motion.div variants={itemVariants} className="algorithm-container glass-card" style={{ maxWidth: '900px' }}>
              <h2 className="card-title" style={{ fontSize: '1.8rem', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                AI IP Guardian (Isolation Forest)
                {isSimulating && <span style={{fontSize: '0.9rem', color: '#ff3366', background: 'rgba(255,51,102,0.1)', padding: '4px 12px', borderRadius: '12px'}}>🔴 UNDER ATTACK</span>}
              </h2>
              <div className="form-grid">
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                  <div className="form-group" style={{ flex: 1, minWidth: '200px' }}>
                    <label>Target IP Address</label>
                    <input value={guardIp} onChange={e => setGuardIp(e.target.value)} className="form-control mono-font" />
                  </div>
                  <div className="form-group" style={{ flex: 1, minWidth: '200px' }}>
                    <label>Manual Action Message</label>
                    <input value={guardMsg} onChange={e => setGuardMsg(e.target.value)} className="form-control mono-font" />
                  </div>
                  <div className="form-group" style={{ display: 'flex', alignItems: 'center', paddingTop: '24px', minWidth: '150px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', margin: 0 }}>
                      <input type="checkbox" checked={guardSuccess} onChange={e => setGuardSuccess(e.target.checked)} style={{ width: '20px', height: '20px' }} />
                      Success Status
                    </label>
                  </div>
                </div>

                <div className="btn-group">
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn sign-btn" onClick={checkGuardian}><Shield size={18} /> Check Single Request</motion.button>
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="action-btn" style={{background: isSimulating ? '#ff3366' : 'linear-gradient(135deg, #ff9a44 0%, #fc6076 100%)'}} onClick={toggleSimulation}>
                    <Zap size={18} /> {isSimulating ? "Stop Attack Simulation" : "🚀 Simulate DDoS Attack"}
                  </motion.button>
                </div>

                {guardResult && (
                  <div className={`result-box ${guardResult.result.status}`}>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
                      <div>
                        <h4 style={{fontSize: '1.2rem', margin: '0 0 8px 0'}}>Security Status: <span style={{textTransform: 'uppercase'}}>{guardResult.result.status}</span></h4>
                        <p style={{margin: '4px 0'}}><strong>Reason:</strong> {guardResult.result.reason} (Layer: {guardResult.result.layer})</p>
                        <p style={{margin: '4px 0'}}><strong>Anomaly Score:</strong> <span style={{color: guardResult.result.score < 0 ? '#ff3366' : '#00ff88', fontWeight: 'bold'}}>{guardResult.result.score.toFixed(3)}</span> (Threshold: ~0.0)</p>
                      </div>
                      <div style={{textAlign: 'right', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px', minWidth: '160px'}}>
                        <h5 style={{margin: '0 0 8px 0', color: '#a0a0c0'}}>IP Stats Tracker</h5>
                        <p style={{margin: '4px 0', fontSize: '1.2rem', fontWeight: 'bold'}}>{guardResult.stats.total} Requests</p>
                        <p style={{margin: '4px 0', color: guardResult.stats.fail_rate > 0.5 ? '#ff3366' : '#a0a0c0'}}>Fail Rate: {(guardResult.stats.fail_rate * 100).toFixed(1)}%</p>
                        <p style={{margin: '4px 0'}}>Blocked: {guardResult.stats.is_blocked ? '🚫 YES' : '✅ NO'}</p>
                      </div>
                    </div>
                    {isSimulating && guardResult.result.status === 'block' && (
                      <div style={{marginTop: '16px', color: '#ffcc00', fontWeight: 'bold'}}>
                        ⚠️ AI HAS IDENTIFIED AND ISOLATED THE ATTACKER!
                      </div>
                    )}
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
