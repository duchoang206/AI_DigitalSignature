import { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, Send, Shield, Leaf, Ghost, Plus, Fingerprint, AlertCircle, CheckCircle2, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

type Document = {
  id: string;
  name: string;
  uploader: string;
  status: 'Chờ duyệt' | '✅ Đã có hiệu lực' | '❌ Bị can thiệp' | '🚨 Vi phạm định danh';
  isTampered: boolean;
  isAuthorized: boolean;
  timestamp: string;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  text: string;
  isAlert?: boolean;
};

const getRandomScore = (min: number, max: number) => (Math.random() * (max - min) + min).toFixed(1);

export default function App() {
  const [activeTab, setActiveTab] = useState<'employee' | 'manager'>('employee');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isManagerAuthenticated, setIsManagerAuthenticated] = useState(false);
  
  const [employeeChat, setEmployeeChat] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Chào mừng Hoàng Xuân Đức. Hệ thống ký số Zero-Trust đã sẵn sàng. Bạn muốn trình ký tài liệu nào?' }
  ]);
  
  const [managerChat, setManagerChat] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Chào Sếp. Vui lòng quét mặt để truy cập Nhật ký bảo mật.' }
  ]);

  const [webcamState, setWebcamState] = useState<{ 
    isOpen: boolean; 
    phase: 'signing' | 'approving' | 'manager_login' | null; 
    targetDocId: string | null 
  }>({
    isOpen: false,
    phase: null,
    targetDocId: null
  });

  const [isHackedUI, setIsHackedUI] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [activeFileName, setActiveFileName] = useState<string>('');
  const [confidence, setConfidence] = useState('0');
  const [scanResult, setScanResult] = useState<'success' | 'fail' | 'scanning'>('scanning');
  const [wizardResult, setWizardResult] = useState<'success' | 'fail'>('success');
  
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [employeeChat, managerChat, activeTab]);

  // AUTO-TRIGGER MANAGER LOGIN
  useEffect(() => {
    if (activeTab === 'manager' && !isManagerAuthenticated && !webcamState.isOpen) {
      setWebcamState({ isOpen: true, phase: 'manager_login', targetDocId: null });
    }
  }, [activeTab, isManagerAuthenticated]);

  // WIZARD OF OZ KEYBOARD LISTENER
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!webcamState.isOpen) return;
      if (e.key === 'f' || e.key === '0') setWizardResult('fail');
      if (e.key === 's' || e.key === '1') setWizardResult('success');
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [webcamState.isOpen]);

  // WEBCAM SCAN LOGIC
  useEffect(() => {
    let timer: any;
    let confidenceInterval: any;

    if (webcamState.isOpen) {
      setConfidence('0');
      setScanResult('scanning');
      const startWebcam = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          streamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(e => console.error(e));
          }
          
          confidenceInterval = setInterval(() => {
            setConfidence(prev => {
              const target = wizardResult === 'fail' ? 75 : 99.9;
              const current = parseFloat(prev);
              if (current >= target) return target.toString();
              return (current + Math.random() * 20).toFixed(1);
            });
          }, 200);

          timer = setTimeout(() => {
            clearInterval(confidenceInterval);
            const finalScore = wizardResult === 'fail' ? getRandomScore(20, 75) : getRandomScore(90, 100);
            setConfidence(finalScore);

            if (wizardResult === 'fail') {
              setScanResult('fail');
              const msg = `🚨 CẢNH BÁO: Độ khớp chỉ đạt ${finalScore}%. Truy cập bị từ chối. Đối tượng không có quyền quản trị!`;
              if (activeTab === 'employee') setEmployeeChat(prev => [...prev, { role: 'assistant', text: msg, isAlert: true }]);
              else setManagerChat(prev => [...prev, { role: 'assistant', text: msg, isAlert: true }]);
              
              if (webcamState.phase === 'signing') {
                const violationDoc: Document = {
                  id: Date.now().toString(),
                  name: activeFileName || "Unknown_File.pdf",
                  uploader: 'Đối tượng không xác định',
                  status: '🚨 Vi phạm định danh',
                  isTampered: false,
                  isAuthorized: false,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                };
                setDocuments(prev => [violationDoc, ...prev]);
              }
              
              setTimeout(() => {
                setWebcamState(prev => ({ ...prev, isOpen: false }));
                if (webcamState.phase === 'manager_login') setActiveTab('employee');
              }, 2000);
            } else {
              setScanResult('success');
              const msg = `✅ Xác thực thành công (Độ khớp: ${finalScore}%). Quyền quản trị đã được mở khóa.`;
              if (activeTab === 'employee') setEmployeeChat(prev => [...prev, { role: 'assistant', text: msg }]);
              else setManagerChat(prev => [...prev, { role: 'assistant', text: msg }]);
              
              setTimeout(() => handleScanSuccess(), 1000);
            }
          }, 3000);
        } catch (err) {
          setWebcamState(prev => ({ ...prev, isOpen: false }));
        }
      };
      startWebcam();
    }

    return () => {
      if (timer) clearTimeout(timer);
      if (confidenceInterval) clearInterval(confidenceInterval);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, [webcamState.isOpen, wizardResult]);

  const handleScanSuccess = () => {
    const { phase, targetDocId } = webcamState;
    setWebcamState(prev => ({ ...prev, isOpen: false }));

    if (phase === 'manager_login') {
      setIsManagerAuthenticated(true);
    } else if (phase === 'signing') {
      const fileName = activeFileName || "Bao_cao_tai_chinh.pdf";
      const newDoc: Document = {
        id: Date.now().toString(),
        name: fileName,
        uploader: 'Hoàng Xuân Đức',
        status: 'Chờ duyệt',
        isTampered: false,
        isAuthorized: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };
      setDocuments(prev => [newDoc, ...prev]);
    } else if (phase === 'approving' && targetDocId) {
      setDocuments(prev => prev.map(d => d.id === targetDocId ? { ...d, status: '✅ Đã có hiệu lực' } : d));
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setActiveFileName(file.name);
    setEmployeeChat(prev => [...prev, { role: 'assistant', text: `Đã nhận file [${file.name}]. Đang quét mặt để xác thực danh tính...` }]);
    setTimeout(() => {
      setWebcamState({ isOpen: true, phase: 'signing', targetDocId: null });
    }, 1000);
  };

  const handleHackerAttack = () => {
    if (documents.length === 0) return;
    setDocuments(prev => prev.map((doc, idx) => idx === 0 ? {
      ...doc,
      name: `[ĐÃ BỊ SỬA] ${doc.name}`,
      isTampered: true,
      status: '❌ Bị can thiệp'
    } : doc));
    setIsHackedUI(true);
    setTimeout(() => setIsHackedUI(false), 3000);
    setEmployeeChat(prev => [...prev, { role: 'assistant', text: '🚨 Cảnh báo: Tệp tin vừa bị can thiệp trái phép trên đường truyền!', isAlert: true }]);
  };

  const currentChat = activeTab === 'employee' ? employeeChat : managerChat;

  const stats = {
    total: documents.length,
    pending: documents.filter(d => d.status === 'Chờ duyệt').length,
    violations: documents.filter(d => d.status === '🚨 Vi phạm định danh').length
  };

  return (
    <div className={`h-screen w-full flex flex-col overflow-hidden bg-zinc-950 text-emerald-50 font-['Inter'] relative transition-all duration-300 ${isHackedUI ? 'ring-[20px] ring-red-600/40 ring-inset' : ''}`}>
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx,.json" />

      {/* HEADER */}
      <header className="h-16 border-b border-emerald-900/30 flex justify-between items-center px-8 bg-zinc-950/50 backdrop-blur-md z-50">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 ${isHackedUI ? 'bg-red-600' : 'bg-emerald-600'} rounded-lg flex items-center justify-center shadow-lg transition-all`}>
            <Shield size={18} className="text-white" />
          </div>
          <span className="font-bold tracking-tight text-lg flex items-center gap-2">Surface City <Leaf size={14} className="text-emerald-500" /></span>
        </div>

        <div className="bg-zinc-900/80 p-1 rounded-xl flex border border-emerald-900/20 relative min-w-[300px]">
          <motion.div 
            className="absolute h-[calc(100%-8px)] w-[calc(50%-4px)] bg-emerald-600/20 border border-emerald-600/30 rounded-lg"
            animate={{ left: activeTab === 'employee' ? '4px' : 'calc(50% + 0px)' }}
            transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
          />
          <button onClick={() => { setActiveTab('employee'); setIsManagerAuthenticated(false); }} className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all relative z-10 ${activeTab === 'employee' ? 'text-emerald-300' : 'text-zinc-500'}`}>Nhân viên</button>
          <button onClick={() => setActiveTab('manager')} className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all relative z-10 ${activeTab === 'manager' ? 'text-emerald-300' : 'text-zinc-500'}`}>Quản trị viên</button>
        </div>

        <div className="flex items-center gap-4">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-widest text-emerald-900">{isManagerAuthenticated ? 'Sếp đã đăng nhập' : 'Zero-Trust Protection'}</span>
        </div>
      </header>

      {/* MAIN BODY */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className="flex-[7] p-12 overflow-y-auto relative bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.03),transparent_40%)]">
          <AnimatePresence mode="wait">
            {activeTab === 'employee' ? (
              <motion.div key="employee" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-4xl mx-auto h-full flex flex-col">
                <div className="mb-12"><h2 className="text-4xl font-extrabold tracking-tight mb-2">Trình ký Nhân viên</h2><p className="text-emerald-400/40 text-sm font-medium italic">Zero-Trust Identity Capture Layer.</p></div>
                <div className="flex-1 flex flex-col">
                  <div onClick={() => fileInputRef.current?.click()} className="group relative block w-full py-28 border-2 border-dashed border-emerald-900/20 rounded-[2.5rem] bg-zinc-900/40 backdrop-blur-xl hover:bg-emerald-950/10 hover:border-emerald-500/40 transition-all cursor-pointer text-center overflow-hidden">
                    <UploadCloud size={32} className="text-emerald-500/50 mx-auto mb-6" />
                    <p className="text-lg font-bold text-emerald-100/80">Tải tài liệu lên để ký số</p>
                  </div>
                  <div className="mt-12 space-y-4">
                    {documents.filter(d => d.uploader === 'Hoàng Xuân Đức').map(doc => (
                      <div key={doc.id} className={`p-6 border rounded-2xl flex items-center justify-between backdrop-blur-md ${doc.isTampered ? 'bg-red-500/5 border-red-500/20' : 'bg-zinc-900/40 border-emerald-900/10'}`}>
                        <div className="flex items-center gap-4"><FileText className={doc.isTampered ? 'text-red-500' : 'text-emerald-900'} /><div><p className={`font-semibold text-sm ${doc.isTampered ? 'text-red-400' : ''}`}>{doc.name}</p><p className="text-[10px] text-zinc-600 font-black uppercase mt-1">Gửi lúc: {doc.timestamp}</p></div></div>
                        <span className={`text-[10px] px-4 py-1.5 rounded-full font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400`}>{doc.status}</span>
                      </div>
                    ))}
                  </div>
                  {documents.length > 0 && documents.some(d => d.uploader === 'Hoàng Xuân Đức' && !d.isTampered) && (
                    <button onClick={handleHackerAttack} className="mt-20 mx-auto block text-[10px] text-emerald-950 hover:text-red-800 transition-colors uppercase font-black tracking-widest flex items-center gap-2"><Ghost size={12} /> 😈 MITM Attack Demo</button>
                  )}
                </div>
              </motion.div>
            ) : isManagerAuthenticated ? (
              <motion.div key="manager" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-6xl mx-auto h-full flex flex-col">
                <div className="mb-12 flex justify-between items-end">
                  <div><h2 className="text-4xl font-extrabold tracking-tight mb-2">Trung tâm Điều hành</h2><p className="text-emerald-400/40 text-sm font-medium italic">Security Audit & Violation Logs.</p></div>
                  <div className="flex gap-4">
                    <div className="bg-zinc-900/50 border border-emerald-900/10 p-4 rounded-2xl min-w-[120px]"><p className="text-[10px] text-zinc-500 font-black uppercase mb-1">Tổng hồ sơ</p><p className="text-2xl font-bold">{stats.total}</p></div>
                    <div className="bg-zinc-900/50 border border-emerald-900/10 p-4 rounded-2xl min-w-[120px]"><p className="text-[10px] text-zinc-500 font-black uppercase mb-1">Chờ duyệt</p><p className="text-2xl font-bold text-blue-400">{stats.pending}</p></div>
                    <div className="bg-zinc-900/50 border border-red-900/20 p-4 rounded-2xl min-w-[120px]"><p className="text-[10px] text-red-900 font-black uppercase mb-1">Vi phạm</p><p className="text-2xl font-bold text-red-500">{stats.violations}</p></div>
                  </div>
                </div>

                <div className="bg-zinc-900/40 border border-emerald-900/10 rounded-3xl overflow-hidden backdrop-blur-xl">
                  <table className="w-full text-left">
                    <thead className="bg-emerald-950/20 border-b border-emerald-900/10"><tr className="text-[10px] font-black text-emerald-900 uppercase tracking-widest"><th className="px-8 py-5">Thời gian</th><th className="px-8 py-5">Người gửi</th><th className="px-8 py-5">Tài liệu</th><th className="px-8 py-5">Trạng thái</th><th className="px-8 py-5 text-right">Hành động</th></tr></thead>
                    <tbody className="divide-y divide-emerald-900/5">
                      {documents.length === 0 ? (
                        <tr><td colSpan={5} className="px-8 py-32 text-center text-emerald-900/40 italic">Nhật ký bảo mật chưa có dữ liệu.</td></tr>
                      ) : (
                        documents.map(doc => (
                          <tr key={doc.id} className={`hover:bg-emerald-900/5 transition-all ${!doc.isAuthorized ? 'bg-red-600/5' : ''}`}>
                            <td className="px-8 py-6 text-xs text-zinc-500 font-mono">{doc.timestamp}</td>
                            <td className="px-8 py-6">
                              <span className={`text-sm font-bold ${doc.isAuthorized ? 'text-blue-400' : 'text-red-500'}`}>{doc.uploader}</span>
                              {!doc.isAuthorized && <p className="text-[9px] text-red-900 font-black uppercase mt-0.5">Không thuộc công ty</p>}
                            </td>
                            <td className="px-8 py-6 font-semibold text-sm text-zinc-300">{doc.name}</td>
                            <td className="px-8 py-6">
                               {doc.status === '🚨 Vi phạm định danh' ? (
                                 <span className="text-[9px] bg-red-600/10 text-red-500 border border-red-500/20 px-3 py-1 rounded-full font-black uppercase">❌ Vi phạm định danh</span>
                               ) : doc.status === '❌ Bị can thiệp' ? (
                                 <span className="text-[9px] bg-red-600/10 text-red-500 border border-red-500/20 px-3 py-1 rounded-full font-black uppercase">🚨 Đã can thiệp</span>
                               ) : (
                                 <span className={`text-[9px] px-3 py-1 rounded-full font-black uppercase border ${doc.status.includes('✅') ? 'bg-emerald-600/10 text-emerald-400 border-emerald-400/20' : 'bg-blue-600/10 text-blue-400 border-blue-400/20'}`}>{doc.status}</span>
                               )}
                            </td>
                            <td className="px-8 py-6 text-right">
                              {!doc.isAuthorized ? (
                                <button className="px-4 py-2 bg-red-600/10 text-red-500 text-[9px] font-black uppercase rounded-xl border border-red-500/20 flex items-center gap-2 ml-auto"><AlertCircle size={14} /> Nhật ký lỗi</button>
                              ) : doc.status === 'Chờ duyệt' ? (
                                <button onClick={() => {
                                  setWebcamState({ isOpen: true, phase: 'approving', targetDocId: doc.id });
                                  setManagerChat(prev => [...prev, { role: 'assistant', text: 'Yêu cầu quét mặt Sếp để hoàn tất phê duyệt...' }]);
                                }} className="px-6 py-2 bg-emerald-600 text-white text-[9px] font-black uppercase rounded-xl">Phê duyệt</button>
                              ) : (
                                <div className="text-emerald-400 text-[9px] font-black uppercase flex items-center justify-end gap-2"><CheckCircle2 size={14} /> Đã phê duyệt</div>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            ) : (
              <motion.div key="manager_lock" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-full">
                 <div className="bg-zinc-900/60 border border-emerald-500/20 p-12 rounded-[3rem] backdrop-blur-xl text-center max-w-md shadow-2xl relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 to-transparent pointer-events-none" />
                    <div className="w-20 h-20 bg-emerald-600/20 rounded-3xl flex items-center justify-center mx-auto mb-8">
                       <Lock size={40} className="text-emerald-500" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4">Cổng vào Quản trị viên</h3>
                    <p className="text-sm text-zinc-500 leading-relaxed mb-8">Bạn cần thực hiện quét mặt xác thực danh tính để truy cập vào trung tâm điều hành bảo mật.</p>
                    <button onClick={() => setWebcamState({ isOpen: true, phase: 'manager_login', targetDocId: null })} className="px-8 py-4 bg-emerald-600 text-white text-xs font-black uppercase tracking-widest rounded-2xl shadow-lg shadow-emerald-600/20 hover:bg-emerald-500 transition-all">Bắt đầu quét mặt</button>
                 </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* WEBCAM HUD MODAL */}
          <AnimatePresence>
            {webcamState.isOpen && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-[100] flex items-center justify-center bg-zinc-950/90 backdrop-blur-md p-10">
                 <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className={`bg-zinc-900 border ${scanResult === 'fail' ? 'border-red-500' : scanResult === 'success' ? 'border-emerald-500' : 'border-emerald-900/20'} rounded-[3rem] overflow-hidden shadow-2xl max-w-2xl w-full relative transition-colors duration-500`}>
                    <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start z-30 pointer-events-none font-mono text-[9px] uppercase">
                       <div className="text-emerald-400/60">MODEL: FaceNet-v512<br />ID: AUTHORIZED USER</div>
                       <div className="text-right text-emerald-400/60">STATUS: {scanResult === 'scanning' ? 'SCANNING' : scanResult.toUpperCase()}<br />MATCH: {confidence}%</div>
                    </div>
                    <div className="relative aspect-video bg-black overflow-hidden">
                       <video ref={videoRef} className={`w-full h-full object-cover grayscale opacity-50 ${scanResult === 'fail' ? 'sepia-[0.5] hue-rotate-[-50deg]' : ''}`} muted playsInline />
                       <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                          <motion.div animate={{ width: '260px', height: '260px' }} className={`relative border-2 ${scanResult === 'fail' ? 'border-red-500 shadow-[0_0_30px_#ef4444]' : scanResult === 'success' ? 'border-emerald-500 shadow-[0_0_20px_#10b981]' : 'border-emerald-500/30'} rounded-3xl flex items-center justify-center`}>
                             <Plus size={20} className="absolute -top-3 -left-3 text-emerald-400" /><Plus size={20} className="absolute -top-3 -right-3 text-emerald-400" /><Plus size={20} className="absolute -bottom-3 -left-3 text-emerald-400" /><Plus size={20} className="absolute -bottom-3 -right-3 text-emerald-400" />
                             <motion.div animate={{ top: ['10%', '90%', '10%'] }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className={`absolute left-0 w-full h-0.5 ${scanResult === 'fail' ? 'bg-red-400' : 'bg-emerald-400'} z-10`} />
                             <div className={`absolute -bottom-10 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] font-mono font-black ${scanResult === 'fail' ? 'bg-red-600/20 text-red-400' : 'bg-emerald-600/20 text-emerald-400'} border border-white/10 backdrop-blur-md`}>
                                {scanResult === 'scanning' ? 'ANALYZING...' : scanResult === 'fail' ? 'AUTH FAILED' : `MATCH: ${confidence}%`}
                             </div>
                             <Fingerprint size={64} className="text-emerald-500/10 animate-pulse" />
                          </motion.div>
                       </div>
                    </div>
                    <div className="p-8 bg-zinc-900/80 flex justify-between items-center relative">
                       <div className="text-left"><p className="text-xs font-bold text-emerald-100 uppercase tracking-widest">{scanResult === 'fail' ? 'Truy cập bị từ chối' : 'Biometric Extraction Layer'}</p><p className="text-[10px] text-zinc-500 font-mono mt-1">Extracting embeddings...</p></div>
                       <div onClick={() => setWizardResult('success')} className="absolute bottom-0 left-0 w-8 h-8 opacity-0 cursor-default" />
                       <div onClick={() => setWizardResult('fail')} className="absolute bottom-0 right-0 w-8 h-8 opacity-0 cursor-default" />
                    </div>
                 </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* CHAT PANEL */}
        <div className="flex-[3] bg-zinc-900/40 border-l border-emerald-900/10 flex flex-col backdrop-blur-3xl">
          <div className="p-6 border-b border-emerald-900/10 flex items-center gap-3"><div className={`w-2 h-2 rounded-full ${isHackedUI ? 'bg-red-500' : 'bg-emerald-500'} animate-pulse`} /><span className="text-[10px] font-black uppercase text-emerald-900 tracking-widest">AI Audit Copilot</span></div>
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-emerald-950/5">
            {currentChat.map((msg, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-emerald-600 text-white rounded-tr-none' : msg.isAlert ? 'bg-red-600/20 text-red-400 border border-red-500/30' : 'bg-zinc-800/80 text-emerald-50/80 border border-emerald-900/20 rounded-tl-none'}`}>{msg.text}</div>
              </motion.div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="p-6 border-t border-emerald-900/10"><div className="relative"><input type="text" value={userInput} onChange={(e) => setUserInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && (setEmployeeChat(p => [...p, {role:'user', text:userInput}]), setUserInput(''))} placeholder="Giám sát an ninh..." className="w-full bg-zinc-900/50 border border-emerald-900/20 rounded-2xl py-4 pl-6 pr-14 text-sm focus:border-emerald-500 transition-all outline-none" /><button className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center text-white"><Send size={18} /></button></div></div>
        </div>
      </div>
    </div>
  );
}
