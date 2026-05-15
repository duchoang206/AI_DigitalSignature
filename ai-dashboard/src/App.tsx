import { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, Send, Shield, Leaf, Ghost, Plus, Fingerprint } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './index.css';

type Document = {
  id: string;
  name: string;
  uploader: string;
  status: 'Chờ duyệt' | '✅ Đã có hiệu lực' | '❌ Bị can thiệp (Đã chặn)';
  isTampered: boolean;
  timestamp: string;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  text: string;
  isAlert?: boolean;
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'employee' | 'manager'>('employee');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isRegistered, setIsRegistered] = useState(true);
  
  const [employeeChat, setEmployeeChat] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Chào mừng Hoàng Xuân Đức. Hệ thống ký số Zero-Trust đã sẵn sàng. Bạn muốn trình ký tài liệu nào?' }
  ]);
  
  const [managerChat, setManagerChat] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Chào Sếp. Hệ thống sẵn sàng kiểm tra tính toàn vẹn của văn bản.' }
  ]);

  const [webcamState, setWebcamState] = useState<{ 
    isOpen: boolean; 
    phase: 'enrollment' | 'signing' | 'approving' | null; 
    targetDocId: string | null 
  }>({
    isOpen: false,
    phase: null,
    targetDocId: null
  });

  const [isHackedUI, setIsHackedUI] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [activeFileName, setActiveFileName] = useState<string>('');
  const [confidence, setConfidence] = useState(0);
  const [scanResult, setScanResult] = useState<'success' | 'fail' | 'scanning'>('scanning');
  const [wizardResult, setWizardResult] = useState<'success' | 'fail'>('success');
  
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [employeeChat, managerChat, activeTab]);

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

  // WEBCAM SCAN LOGIC (Simulation with Wizard of Oz)
  useEffect(() => {
    let timer: any;
    let confidenceInterval: any;

    if (webcamState.isOpen) {
      setConfidence(0);
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
              const target = wizardResult === 'fail' ? 14.2 : 98.7;
              if (prev >= target) return target;
              return +(prev + Math.random() * 20).toFixed(1);
            });
          }, 200);

          timer = setTimeout(() => {
            clearInterval(confidenceInterval);
            if (wizardResult === 'fail' && webcamState.phase !== 'enrollment') {
              setScanResult('fail');
              setEmployeeChat(prev => [...prev, { 
                role: 'assistant', 
                text: '🚨 CẢNH BÁO: Khuôn mặt không khớp với dữ liệu sinh trắc học của Hoàng Xuân Đức. Định danh thất bại. Hệ thống từ chối mở khóa Private Key!',
                isAlert: true 
              }]);
              setTimeout(() => setWebcamState(prev => ({ ...prev, isOpen: false })), 2000);
            } else {
              setScanResult('success');
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

    if (phase === 'enrollment') {
      setIsRegistered(true);
      setEmployeeChat(prev => [...prev, { role: 'assistant', text: '✅ Đã lưu vector đặc trưng khuôn mặt của Hoàng Xuân Đức. Cặp khóa Private/Public Key đã được khởi tạo an toàn.' }]);
    } else if (phase === 'signing') {
      const fileName = activeFileName || "Bao_cao_tai_chinh.pdf";
      const newDoc: Document = {
        id: Date.now().toString(),
        name: fileName,
        uploader: 'Hoàng Xuân Đức',
        status: 'Chờ duyệt',
        isTampered: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setDocuments(prev => [...prev, newDoc]);
      setEmployeeChat(prev => [...prev, { role: 'assistant', text: `✅ Định danh chính xác: Hoàng Xuân Đức. Đang tạo chữ ký số ECDSA...` }]);
    } else if (phase === 'approving' && targetDocId) {
      setDocuments(prev => prev.map(d => d.id === targetDocId ? { ...d, status: '✅ Đã có hiệu lực' } : d));
      setManagerChat(prev => [...prev, { role: 'assistant', text: '✅ Xác thực Sếp thành công. Chữ ký kép đã được áp dụng, văn bản chính thức có hiệu lực.' }]);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setActiveFileName(file.name);
    setEmployeeChat(prev => [...prev, { role: 'assistant', text: `Đã nhận file [${file.name}]. Đang quét mặt để ký số...` }]);
    setTimeout(() => {
      setWebcamState({ isOpen: true, phase: 'signing', targetDocId: null });
    }, 1000);
  };

  const handleHackerAttack = () => {
    if (documents.length === 0) return;
    setDocuments(prev => prev.map((doc, idx) => idx === 0 ? {
      ...doc,
      name: `[ĐÃ BỊ SỬA] ${doc.name}`,
      isTampered: true
    } : doc));
    setIsHackedUI(true);
    setTimeout(() => setIsHackedUI(false), 3000);
    setEmployeeChat(prev => [...prev, { role: 'assistant', text: '🚨 Cảnh báo: Tệp tin vừa bị can thiệp trái phép trên đường truyền!', isAlert: true }]);
  };

  const handleManagerApprove = (doc: Document) => {
    if (doc.isTampered) {
      setIsHackedUI(true);
      setManagerChat(prev => [...prev, { 
        role: 'assistant', 
        text: '🚨 BÁO ĐỘNG: Mã băm của tài liệu KHÔNG KHỚP với chữ ký số. Tài liệu đã bị chỉnh sửa!',
        isAlert: true 
      }]);
      setDocuments(prev => prev.map(d => d.id === doc.id ? { ...d, status: '❌ Bị can thiệp (Đã chặn)' } : d));
      setTimeout(() => setIsHackedUI(false), 4000);
    } else {
      setManagerChat(prev => [...prev, { role: 'assistant', text: 'Yêu cầu xác thực khuôn mặt Quản trị viên...' }]);
      setWebcamState({ isOpen: true, phase: 'approving', targetDocId: doc.id });
    }
  };

  const currentChat = activeTab === 'employee' ? employeeChat : managerChat;

  return (
    <div className={`h-screen w-full flex flex-col overflow-hidden bg-zinc-950 text-emerald-50 font-['Inter'] relative transition-all duration-300 ${isHackedUI ? 'ring-[20px] ring-red-600/40 ring-inset' : ''}`}>
      
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx,.json" />

      {/* HEADER */}
      <header className="h-16 border-b border-emerald-900/30 flex justify-between items-center px-8 bg-zinc-950/50 backdrop-blur-md z-50">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 ${isHackedUI ? 'bg-red-600' : 'bg-emerald-600'} rounded-lg flex items-center justify-center shadow-lg transition-colors`}>
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
          <button onClick={() => setActiveTab('employee')} className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all relative z-10 ${activeTab === 'employee' ? 'text-emerald-300' : 'text-zinc-500'}`}>Nhân viên</button>
          <button onClick={() => setActiveTab('manager')} className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all relative z-10 ${activeTab === 'manager' ? 'text-emerald-300' : 'text-zinc-500'}`}>Quản trị viên</button>
        </div>

        <div className="flex items-center gap-4">
          <div className={`h-2 w-2 rounded-full ${isRegistered ? 'bg-emerald-500' : 'bg-zinc-700'}`} />
          <span className="text-[10px] font-black uppercase tracking-widest text-emerald-900">{isRegistered ? 'Đã kích hoạt' : 'Chưa đăng ký'}</span>
        </div>
      </header>

      {/* MAIN BODY */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className="flex-[7] p-12 overflow-y-auto relative bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.03),transparent_40%)]">
          <AnimatePresence mode="wait">
            {activeTab === 'employee' ? (
              <motion.div key="employee" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-4xl mx-auto h-full flex flex-col">
                <div className="mb-12 flex justify-between items-end">
                  <div><h2 className="text-4xl font-extrabold tracking-tight mb-2">Trình ký Nhân viên</h2><p className="text-emerald-400/40 text-sm font-medium italic">Zero-Trust Identity Protocol.</p></div>
                </div>

                <div className="flex-1 flex flex-col transition-all duration-700">
                  <div onClick={() => fileInputRef.current?.click()} className="group relative block w-full py-28 border-2 border-dashed border-emerald-900/20 rounded-[2.5rem] bg-zinc-900/40 backdrop-blur-xl hover:bg-emerald-950/10 hover:border-emerald-500/40 transition-all cursor-pointer text-center">
                    <UploadCloud size={32} className="text-emerald-500/50 mx-auto mb-6" />
                    <p className="text-lg font-bold text-emerald-100/80">Tải tài liệu lên để ký số</p>
                  </div>

                  <div className="mt-12 space-y-4">
                    {documents.map(doc => (
                      <div key={doc.id} className={`p-6 border rounded-2xl flex items-center justify-between backdrop-blur-md ${doc.isTampered ? 'bg-red-500/5 border-red-500/20' : 'bg-zinc-900/40 border-emerald-900/10'}`}>
                        <div className="flex items-center gap-4"><FileText className={doc.isTampered ? 'text-red-500' : 'text-emerald-900'} /><div><p className={`font-semibold text-sm ${doc.isTampered ? 'text-red-400' : ''}`}>{doc.name}</p><p className="text-[10px] text-zinc-600 font-black uppercase mt-1">Sở hữu: {doc.uploader}</p></div></div>
                        <span className={`text-[10px] px-4 py-1.5 rounded-full font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400`}>{doc.status}</span>
                      </div>
                    ))}
                  </div>

                  {documents.length > 0 && !documents[0].isTampered && (
                    <button onClick={handleHackerAttack} className="mt-20 mx-auto block text-[10px] text-emerald-950 hover:text-red-800 transition-colors uppercase font-black tracking-widest flex items-center gap-2"><Ghost size={12} /> 😈 MITM Attack Demo</button>
                  )}
                </div>

              </motion.div>
            ) : (
              <motion.div key="manager" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-5xl mx-auto h-full flex flex-col">
                <div className="mb-12"><h2 className="text-4xl font-extrabold tracking-tight mb-2">Quản lý Tài liệu</h2></div>
                <div className="bg-zinc-900/40 border border-emerald-900/10 rounded-3xl overflow-hidden backdrop-blur-xl">
                  <table className="w-full text-left">
                    <thead className="bg-emerald-950/20 border-b border-emerald-900/10"><tr className="text-[10px] font-black text-emerald-900"><th className="px-8 py-5">Tài liệu</th><th className="px-8 py-5">Người gửi</th><th className="px-8 py-5 text-right">Hành động</th></tr></thead>
                    <tbody className="divide-y divide-emerald-900/5">
                      {documents.length === 0 ? (
                        <tr><td colSpan={3} className="px-8 py-32 text-center text-emerald-900/40 italic">Hiện chưa có tài liệu chờ duyệt.</td></tr>
                      ) : (
                        documents.map(doc => (
                          <tr key={doc.id} className={`hover:bg-emerald-900/5 ${doc.isTampered ? 'bg-red-500/5' : ''}`}>
                            <td className="px-8 py-6 flex items-center gap-3 font-semibold text-sm"><FileText size={18} className={doc.isTampered ? 'text-red-500' : 'text-emerald-900'} />{doc.name}</td>
                            <td className="px-8 py-6 text-sm text-zinc-500">{doc.uploader}</td>
                            <td className="px-8 py-6 text-right">
                              {doc.status === 'Chờ duyệt' ? (
                                <button onClick={() => handleManagerApprove(doc)} className="px-6 py-2 bg-emerald-600 text-white text-[10px] font-black rounded-xl">Kiểm tra & Phê duyệt</button>
                              ) : <span className="text-[10px] font-black text-emerald-400">{doc.status}</span>}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* WEBCAM HUD MODAL (WIZARD OF OZ) */}
          <AnimatePresence>
            {webcamState.isOpen && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-[100] flex items-center justify-center bg-zinc-950/90 backdrop-blur-md p-10">
                 <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className={`bg-zinc-900 border ${scanResult === 'fail' ? 'border-red-500' : scanResult === 'success' ? 'border-emerald-500' : 'border-emerald-900/20'} rounded-[3rem] overflow-hidden shadow-2xl max-w-2xl w-full relative transition-colors duration-500`}>
                    
                    {/* HUD TELEMETRY */}
                    <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start z-30 pointer-events-none font-mono text-[9px] uppercase">
                       <div className="text-emerald-400/60">MODEL: FaceNet-v512<br />ID: HOANG XUAN DUC</div>
                       <div className="text-right text-emerald-400/60">STATUS: {scanResult === 'scanning' ? 'SCANNING' : scanResult.toUpperCase()}<br />MATCH: {confidence}%</div>
                    </div>

                    <div className="relative aspect-video bg-black overflow-hidden">
                       <video ref={videoRef} className={`w-full h-full object-cover grayscale opacity-50 ${scanResult === 'fail' ? 'sepia-[0.5] hue-rotate-[-50deg]' : ''}`} muted playsInline />
                       
                       {/* FEATURE GRID */}
                       <div className="absolute inset-0 grid grid-cols-10 grid-rows-10 opacity-10 pointer-events-none">
                          {Array.from({ length: 100 }).map((_, i) => <div key={i} className="border-[0.5px] border-emerald-500/20" />)}
                       </div>

                       {/* BOUNDING BOX */}
                       <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                          <motion.div 
                            animate={{ width: '260px', height: '260px' }}
                            className={`relative border-2 ${scanResult === 'fail' ? 'border-red-500 shadow-[0_0_30px_#ef4444]' : scanResult === 'success' ? 'border-emerald-500 shadow-[0_0_20px_#10b981]' : 'border-emerald-500/30'} rounded-3xl flex items-center justify-center`}
                          >
                             <Plus size={20} className="absolute -top-3 -left-3 text-emerald-400" />
                             <Plus size={20} className="absolute -top-3 -right-3 text-emerald-400" />
                             <Plus size={20} className="absolute -bottom-3 -left-3 text-emerald-400" />
                             <Plus size={20} className="absolute -bottom-3 -right-3 text-emerald-400" />
                             
                             <motion.div animate={{ top: ['10%', '90%', '10%'] }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className={`absolute left-0 w-full h-0.5 ${scanResult === 'fail' ? 'bg-red-400' : 'bg-emerald-400'} z-10`} />
                             
                             <div className={`absolute -bottom-10 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-[10px] font-mono font-black ${scanResult === 'fail' ? 'bg-red-600/20 text-red-400' : 'bg-emerald-600/20 text-emerald-400'} border border-white/10 backdrop-blur-md`}>
                                {scanResult === 'scanning' ? 'ANALYZING...' : scanResult === 'fail' ? 'AUTH FAILED' : `MATCH: ${confidence}%`}
                             </div>
                             <Fingerprint size={64} className="text-emerald-500/10 animate-pulse" />
                          </motion.div>
                       </div>

                       {scanResult === 'fail' && <div className="absolute inset-0 bg-red-600/10 animate-pulse" />}
                       {scanResult === 'success' && <div className="absolute inset-0 bg-emerald-600/10 animate-pulse" />}
                    </div>
                    
                    <div className="p-8 bg-zinc-900/80 flex justify-between items-center relative">
                       <div className="text-left">
                          <p className="text-xs font-bold text-emerald-100 uppercase tracking-widest">{scanResult === 'fail' ? 'Truy cập bị từ chối' : 'Biometric Extraction Layer'}</p>
                          <p className="text-[10px] text-zinc-500 font-mono mt-1">Extracting embeddings...</p>
                       </div>

                       {/* INVISIBLE CLICK ZONES (WIZARD OF OZ) */}
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
          <div className="p-6 border-b border-emerald-900/10 flex items-center gap-3"><div className={`w-2 h-2 rounded-full ${isHackedUI ? 'bg-red-500' : 'bg-emerald-500'} animate-pulse`} /><span className="text-[10px] font-black uppercase text-emerald-900 tracking-widest">AI Zero-Trust Assistant</span></div>
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-emerald-950/5">
            {currentChat.map((msg, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-emerald-600 text-white rounded-tr-none' : msg.isAlert ? 'bg-red-600/20 text-red-400 border border-red-500/30' : 'bg-zinc-800/80 text-emerald-50/80 border border-emerald-900/20 rounded-tl-none'}`}>{msg.text}</div>
              </motion.div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="p-6 border-t border-emerald-900/10"><div className="relative"><input type="text" value={userInput} onChange={(e) => setUserInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && (setEmployeeChat(p => [...p, {role:'user', text:userInput}]), setUserInput(''))} placeholder="Hệ thống bảo vệ..." className="w-full bg-zinc-900/50 border border-emerald-900/20 rounded-2xl py-4 pl-6 pr-14 text-sm focus:border-emerald-500 transition-all outline-none" /><button className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center text-white"><Send size={18} /></button></div></div>
        </div>
      </div>
    </div>
  );
}
