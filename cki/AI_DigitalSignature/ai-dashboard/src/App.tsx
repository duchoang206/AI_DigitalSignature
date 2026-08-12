import { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, Send, Shield, Ghost, Plus, ScanFace, AlertCircle, CheckCircle2, Lock, Eye, EyeOff, X } from 'lucide-react';
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
  fileUrl?: string;
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
  const [viewedDocIds, setViewedDocIds] = useState<string[]>([]);
  const [previewDoc, setPreviewDoc] = useState<Document | null>(null);
  
  const [employeeChat, setEmployeeChat] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Xin chào, tôi giúp gì được cho bạn?' }
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
  const [activeFileUrl, setActiveFileUrl] = useState<string>('');
  const [confidence, setConfidence] = useState('0');
  const [scanResult, setScanResult] = useState<'success' | 'fail' | 'scanning'>('scanning');
  const [wizardResult, setWizardResult] = useState<'success' | 'fail'>('success');
  
  const [currentBannerIndex, setCurrentBannerIndex] = useState(0);
  const banners = [
    '/banner1.png',
    '/banner2.png',
    '/banner3.png'
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentBannerIndex(prev => (prev + 1) % banners.length);
    }, 3000);
    return () => clearInterval(timer);
  }, [banners.length]);

  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [employeeChat, managerChat, activeTab]);

  // CHATBOT SCRIPT LOGIC
  useEffect(() => {
    const lastMessage = employeeChat[employeeChat.length - 1];
    if (lastMessage && lastMessage.role === 'user') {
      const userText = lastMessage.text.toLowerCase();
      let reply = 'Tôi là AI Copilot. Tôi có thể hướng dẫn bạn cách tải tài liệu lên và trình ký an toàn trên hệ thống Zero-Trust.';
      
      if (userText.includes('chào')) {
        reply = 'Chào bạn, tôi giúp gì được cho bạn?';
      } else if (userText.includes('cách làm như nào') || userText.includes('cách làm')) {
        reply = 'Bạn hãy tải tài liệu cần ký lên và nhìn vào camera để xác thực nhé';
      } else if (userText.includes('trình tài liệu') || userText.includes('ký') || userText.includes('sếp')) {
        reply = 'Để trình tài liệu, bạn hãy nhấn vào khu vực tải file ở bên trái (có biểu tượng đám mây), chọn tài liệu cần ký. Sau khi tải lên, hệ thống sẽ yêu cầu quét khuôn mặt của bạn để xác thực danh tính trước khi đưa vào hàng đợi chờ Sếp duyệt nhé.';
      }

      const timer = setTimeout(() => {
        setEmployeeChat(prev => [...prev, { role: 'assistant', text: reply }]);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [employeeChat]);

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
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        fileUrl: activeFileUrl
      };
      setDocuments(prev => [newDoc, ...prev]);
    } else if (phase === 'approving' && targetDocId) {
      setDocuments(prev => prev.map(d => d.id === targetDocId ? { ...d, status: '✅ Đã có hiệu lực' } : d));
    }
  };

  const handleViewDocument = (doc: Document) => {
    setPreviewDoc(doc);
    if (!viewedDocIds.includes(doc.id)) {
      setViewedDocIds(prev => [...prev, doc.id]);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fileUrl = URL.createObjectURL(file);
    setActiveFileName(file.name);
    setActiveFileUrl(fileUrl);
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
    <div className={`h-screen w-full flex flex-col overflow-hidden bg-[#f8fafc] text-slate-800 font-['Inter'] relative transition-all duration-300 ${isHackedUI ? 'ring-[20px] ring-red-500/30 ring-inset' : ''}`}>
      <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-blue-400/20 rounded-full blur-[120px] pointer-events-none animate-float" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-400/20 rounded-full blur-[120px] pointer-events-none animate-float-delayed" />
      
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx,.json" />

      {/* HEADER */}
      <header className="h-20 border-b border-white/60 flex justify-between items-center px-8 bg-white/65 backdrop-blur-[12px] z-50 shadow-[0_10px_30px_rgba(0,0,0,0.03)]">
        <div className="flex items-center gap-4 bg-[#3b82f6] px-5 py-2.5 rounded-xl shadow-[0_4px_15px_rgba(59,130,246,0.3)] group cursor-pointer hover:shadow-[0_8px_25px_rgba(59,130,246,0.5)] transition-all">
          {/* Microsoft Logo */}
          <div className="flex items-center gap-2">
            <div className="grid grid-cols-2 gap-[2px]">
              <div className="w-2.5 h-2.5 bg-[#f25022]"></div>
              <div className="w-2.5 h-2.5 bg-[#7fba00]"></div>
              <div className="w-2.5 h-2.5 bg-[#00a4ef]"></div>
              <div className="w-2.5 h-2.5 bg-[#ffb900]"></div>
            </div>
            <span className="text-white font-semibold text-lg tracking-tight leading-none mb-0.5">Microsoft</span>
          </div>
          
          {/* Divider */}
          <div className="w-px h-5 bg-white/40"></div>
          
          {/* Surfacecity Logo */}
          <div className="flex flex-col justify-center">
            <div className="flex gap-1 mb-[3px]">
              <div className="w-2 h-2 rounded-full bg-[#7fba00]"></div>
              <div className="w-2 h-2 rounded-full bg-[#00a4ef]"></div>
              <div className="w-2 h-2 rounded-full bg-[#f25022]"></div>
              <div className="w-2 h-2 rounded-full bg-[#ffb900]"></div>
            </div>
            <span className="text-white font-bold text-xs tracking-wide leading-none">Surfacecity</span>
          </div>
        </div>

        <div className="bg-slate-100/80 backdrop-blur-md p-1.5 rounded-2xl flex border border-white relative min-w-[320px] shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]">
          <motion.div 
            className="absolute h-[calc(100%-12px)] w-[calc(50%-6px)] bg-white border border-slate-200/60 rounded-xl shadow-[0_4px_12px_rgba(0,0,0,0.05)]"
            animate={{ left: activeTab === 'employee' ? '6px' : 'calc(50% + 0px)' }}
            transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
          />
          <button onClick={() => { setActiveTab('employee'); setIsManagerAuthenticated(false); }} className={`flex-1 py-2 text-sm font-bold rounded-xl transition-all relative z-10 ${activeTab === 'employee' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>Nhân viên</button>
          <button onClick={() => setActiveTab('manager')} className={`flex-1 py-2 text-sm font-bold rounded-xl transition-all relative z-10 ${activeTab === 'manager' ? 'text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>Quản trị viên</button>
        </div>

        <div className="flex items-center gap-4 bg-white/80 backdrop-blur-[12px] px-5 py-2.5 rounded-full border border-white shadow-[0_8px_16px_rgba(0,0,0,0.04)]">
          <div className="h-2.5 w-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)] animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-widest text-blue-600">{isManagerAuthenticated ? 'Sếp đã đăng nhập' : 'Zero-Trust Protection'}</span>
        </div>
      </header>

      {/* MAIN BODY */}
      <div className="flex flex-1 overflow-hidden relative z-10">
        <div className="flex-[7] p-12 overflow-y-auto relative custom-scrollbar">
          <AnimatePresence mode="wait">
            {activeTab === 'employee' ? (
              <motion.div key="employee" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-4xl mx-auto h-full flex flex-col">
                <div className="mb-12"><h2 className="text-5xl font-extrabold tracking-tight mb-2 text-slate-800">Trình ký Nhân viên</h2><p className="text-blue-500/80 text-sm font-medium italic">Zero-Trust Identity Capture Layer.</p></div>
                <div className="flex-1 flex flex-col">
                  <div onClick={() => fileInputRef.current?.click()} className="animate-float group relative block w-[70%] mx-auto py-20 border border-white rounded-[3rem] bg-white/65 backdrop-blur-[12px] shadow-[0_20px_40px_-10px_rgba(0,0,0,0.06)] hover:bg-white/90 hover:border-blue-200 hover:-translate-y-2 hover:shadow-[0_30px_60px_-15px_rgba(59,130,246,0.15)] transition-all duration-500 cursor-pointer text-center overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-white/40 to-transparent pointer-events-none" />
                    <UploadCloud size={48} className="text-blue-400 mx-auto mb-6 group-hover:scale-110 group-hover:text-blue-500 transition-transform duration-500" />
                    <p className="text-xl font-bold text-slate-700 group-hover:text-blue-600 transition-colors">Tải tài liệu lên để ký số</p>
                    <p className="text-sm text-slate-400 mt-2 font-medium">Hỗ trợ PDF, DOCX, JSON</p>
                  </div>



                  <div className="mt-8 space-y-6">
                    {documents.filter(d => d.uploader === 'Hoàng Xuân Đức').map((doc, idx) => (
                      <div key={doc.id} className={`animate-float-delayed p-6 border rounded-[2rem] flex items-center justify-between backdrop-blur-[12px] shadow-[0_15px_35px_rgba(0,0,0,0.05)] transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_25px_50px_rgba(59,130,246,0.12)] relative overflow-hidden group ${doc.isTampered ? 'bg-red-50/80 border-red-200 hover:border-red-300 hover:shadow-[0_20px_50px_rgba(239,68,68,0.15)]' : 'bg-white/65 border-white hover:border-blue-200'}`} style={{ animationDelay: `${idx * 0.2}s` }}>
                        <div className="absolute inset-0 bg-gradient-to-r from-white/40 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity" />
                        <div className="flex items-center gap-5 relative z-10"><div className={`p-4 rounded-xl ${doc.isTampered ? 'bg-red-100/50' : 'bg-blue-50/50'} backdrop-blur-md`}><FileText className={doc.isTampered ? 'text-red-500' : 'text-blue-500'} /></div><div><p className={`font-semibold text-base ${doc.isTampered ? 'text-red-600' : 'text-slate-800'}`}>{doc.name}</p><p className="text-[10px] text-slate-400 font-black uppercase mt-1 tracking-wider">Gửi lúc: {doc.timestamp}</p></div></div>
                        <span className={`relative z-10 text-[10px] px-5 py-2 rounded-full font-black uppercase tracking-widest border ${doc.isTampered ? 'bg-red-100 text-red-600 border-red-200' : 'bg-blue-50 text-blue-600 border-blue-200 shadow-sm'}`}>{doc.status}</span>
                      </div>
                    ))}
                  </div>
                  {documents.length > 0 && documents.some(d => d.uploader === 'Hoàng Xuân Đức' && !d.isTampered) && (
                    <button onClick={handleHackerAttack} className="mt-20 mx-auto block text-xs text-slate-400 hover:text-red-500 transition-colors uppercase font-black tracking-widest flex items-center gap-2 hover:drop-shadow-[0_0_10px_rgba(239,68,68,0.3)]"><Ghost size={14} /> 😈 MITM Attack Demo</button>
                  )}

                  {/* BANNER CAROUSEL */}
                  <div className="mt-12 animate-float bg-white/65 border border-white rounded-[2rem] p-3 backdrop-blur-[12px] shadow-[0_15px_35px_-10px_rgba(0,0,0,0.05)] hover:shadow-[0_25px_50px_-15px_rgba(59,130,246,0.1)] transition-all relative overflow-hidden group">
                    <div className="relative w-full aspect-[21/9] sm:aspect-[3/1] rounded-[1.5rem] overflow-hidden bg-slate-100">
                      <AnimatePresence mode="wait">
                        <motion.img 
                          key={currentBannerIndex}
                          src={banners[currentBannerIndex]}
                          initial={{ opacity: 0, x: 50 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -50 }}
                          transition={{ duration: 0.5 }}
                          className="absolute inset-0 w-full h-full object-cover"
                          alt="Promotion Banner"
                        />
                      </AnimatePresence>
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10 bg-black/20 px-3 py-1.5 rounded-full backdrop-blur-md">
                        {banners.map((_, i) => (
                          <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i === currentBannerIndex ? 'w-6 bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]' : 'w-2 bg-white/50'}`} />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ) : isManagerAuthenticated ? (
              <motion.div key="manager" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="max-w-6xl mx-auto h-full flex flex-col">
                <div className="mb-12 flex justify-between items-end">
                  <div><h2 className="text-5xl font-extrabold tracking-tight mb-2 text-slate-800">Trung tâm Điều hành</h2><p className="text-blue-500/80 text-sm font-medium italic">Security Audit & Violation Logs.</p></div>
                  <div className="flex gap-5">
                    <div className="animate-float-delayed bg-white/65 backdrop-blur-[12px] border border-white p-6 rounded-[2rem] min-w-[140px] shadow-[0_15px_35px_rgba(0,0,0,0.04)] hover:-translate-y-2 hover:shadow-[0_25px_50px_rgba(0,0,0,0.08)] transition-all duration-500 relative overflow-hidden group">
                      <div className="absolute inset-0 bg-gradient-to-br from-white/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      <p className="text-[10px] text-slate-400 font-black uppercase mb-2 relative z-10">Tổng hồ sơ</p><p className="text-3xl font-black text-slate-800 relative z-10">{stats.total}</p>
                    </div>
                    <div className="animate-float-delayed bg-white/65 backdrop-blur-[12px] border border-white p-6 rounded-[2rem] min-w-[140px] shadow-[0_15px_35px_rgba(59,130,246,0.05)] hover:-translate-y-2 hover:shadow-[0_25px_50px_rgba(59,130,246,0.12)] hover:border-blue-200 transition-all duration-500 relative overflow-hidden group" style={{ animationDelay: '0.2s' }}>
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      <p className="text-[10px] text-blue-500 font-black uppercase mb-2 relative z-10">Chờ duyệt</p><p className="text-3xl font-black text-blue-600 relative z-10">{stats.pending}</p>
                    </div>
                    <div className="animate-float-delayed bg-white/65 backdrop-blur-[12px] border border-white p-6 rounded-[2rem] min-w-[140px] shadow-[0_15px_35px_rgba(239,68,68,0.05)] hover:-translate-y-2 hover:shadow-[0_25px_50px_rgba(239,68,68,0.12)] hover:border-red-200 transition-all duration-500 relative overflow-hidden group" style={{ animationDelay: '0.4s' }}>
                      <div className="absolute inset-0 bg-gradient-to-br from-red-50/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      <p className="text-[10px] text-red-500 font-black uppercase mb-2 relative z-10">Vi phạm</p><p className="text-3xl font-black text-red-600 relative z-10">{stats.violations}</p>
                    </div>
                  </div>
                </div>
                {/* Q2 Internal Report */}
                <div className="mb-8 animate-float bg-white/65 border border-white rounded-[2.5rem] p-8 backdrop-blur-[12px] shadow-[0_15px_35px_-10px_rgba(0,0,0,0.05)] hover:shadow-[0_25px_50px_-15px_rgba(59,130,246,0.1)] transition-all relative overflow-hidden group">
                   <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white/50 to-purple-50/50 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                   <div className="flex justify-between items-start mb-6 relative z-10">
                      <div>
                         <h3 className="text-2xl font-extrabold text-slate-800 tracking-tight">Báo Cáo Nội Bộ - Quý II / 2026</h3>
                         <p className="text-sm font-medium text-slate-500 mt-1">Đánh giá Hệ thống Zero-Trust & Chữ ký số ECDSA</p>
                      </div>
                      <span className="text-xs font-black text-emerald-600 bg-emerald-50 border border-emerald-200 px-4 py-2 rounded-full shadow-sm flex items-center gap-2">
                        <CheckCircle2 size={16} /> HOẠT ĐỘNG ỔN ĐỊNH
                      </span>
                   </div>
                   
                   <div className="grid grid-cols-3 gap-6 relative z-10">
                      <div className="bg-white/80 border border-slate-100 p-5 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
                         <div className="flex items-center gap-3 mb-3"><Shield className="text-blue-500" size={24} /><h4 className="text-sm font-bold text-slate-700">Tỷ lệ Bảo mật</h4></div>
                         <p className="text-4xl font-black text-slate-800">100<span className="text-lg text-slate-400">%</span></p>
                         <p className="text-[10px] uppercase font-bold text-emerald-500 mt-2 bg-emerald-50 inline-block px-2 py-0.5 rounded-md border border-emerald-100 shadow-sm">Không có rò rỉ</p>
                      </div>
                      <div className="bg-white/80 border border-slate-100 p-5 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
                         <div className="flex items-center gap-3 mb-3"><ScanFace className="text-purple-500" size={24} /><h4 className="text-sm font-bold text-slate-700">Lượt Quét AI</h4></div>
                         <p className="text-4xl font-black text-slate-800">14,250</p>
                         <p className="text-[10px] uppercase font-bold text-emerald-500 mt-2 bg-emerald-50 inline-block px-2 py-0.5 rounded-md border border-emerald-100 shadow-sm">Tăng 12% so với Q1</p>
                      </div>
                      <div className="bg-white/80 border border-slate-100 p-5 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all">
                         <div className="flex items-center gap-3 mb-3"><FileText className="text-orange-500" size={24} /><h4 className="text-sm font-bold text-slate-700">Tài liệu Ký số</h4></div>
                         <p className="text-4xl font-black text-slate-800">8,924</p>
                         <p className="text-[10px] uppercase font-bold text-emerald-500 mt-2 bg-emerald-50 inline-block px-2 py-0.5 rounded-md border border-emerald-100 shadow-sm">100% Xác thực ECDSA</p>
                      </div>
                   </div>
                </div>

                <div className="animate-float bg-white/65 border border-white rounded-[2.5rem] overflow-hidden backdrop-blur-[12px] shadow-[0_20px_50px_-10px_rgba(0,0,0,0.08)] relative z-10 hover:shadow-[0_30px_60px_-15px_rgba(59,130,246,0.1)] transition-all duration-500">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50/80 border-b border-slate-100"><tr className="text-[10px] font-black text-slate-400 uppercase tracking-widest"><th className="px-8 py-5">Thời gian</th><th className="px-8 py-5">Người gửi</th><th className="px-8 py-5">Tài liệu</th><th className="px-8 py-5">Trạng thái</th><th className="px-8 py-5 text-right">Hành động</th></tr></thead>
                    <tbody className="divide-y divide-slate-100">
                      {documents.length === 0 ? (
                        <tr><td colSpan={5} className="px-8 py-32 text-center text-slate-400 italic">Nhật ký bảo mật chưa có dữ liệu.</td></tr>
                      ) : (
                        documents.map(doc => (
                          <tr key={doc.id} className={`group hover:bg-white hover:shadow-[0_5px_15px_rgba(0,0,0,0.03)] transition-all duration-300 ${!doc.isAuthorized ? 'bg-red-50/30' : ''}`}>
                            <td className="px-8 py-6 text-xs text-slate-500 font-mono group-hover:text-blue-500 transition-colors">{doc.timestamp}</td>
                            <td className="px-8 py-6">
                              <span className={`text-sm font-bold ${doc.isAuthorized ? 'text-slate-800 group-hover:text-blue-600' : 'text-red-600'}`}>{doc.uploader}</span>
                              {!doc.isAuthorized && <p className="text-[9px] text-red-500 font-black uppercase mt-1 tracking-wider">Không thuộc công ty</p>}
                            </td>
                            <td className="px-8 py-6">
                              <div className="flex items-center gap-2">
                                <button 
                                  onClick={() => handleViewDocument(doc)} 
                                  className="font-semibold text-sm text-slate-700 hover:text-blue-600 hover:underline transition-colors flex items-center gap-2 group/btn text-left cursor-pointer bg-transparent border-none outline-none p-0"
                                >
                                  <FileText size={16} className="text-slate-400 group-hover/btn:text-blue-500 transition-colors shrink-0" />
                                  <span className="truncate max-w-[200px]">{doc.name}</span>
                                </button>
                                
                                {doc.isAuthorized && doc.status === 'Chờ duyệt' && (
                                  viewedDocIds.includes(doc.id) ? (
                                    <span className="flex items-center gap-1 text-[9px] bg-emerald-50 text-emerald-600 border border-emerald-100 px-2 py-0.5 rounded-md font-bold whitespace-nowrap shadow-sm">
                                      <Eye size={10} /> Đã xem
                                    </span>
                                  ) : (
                                    <span className="flex items-center gap-1 text-[9px] bg-slate-100 text-slate-500 border border-slate-200 px-2 py-0.5 rounded-md font-bold whitespace-nowrap shadow-sm">
                                      <EyeOff size={10} /> Chưa xem
                                    </span>
                                  )
                                )}
                              </div>
                            </td>
                            <td className="px-8 py-6">
                               {doc.status === '🚨 Vi phạm định danh' ? (
                                 <span className="text-[9px] bg-red-100 text-red-600 border border-red-200 px-4 py-1.5 rounded-full font-black uppercase shadow-sm">❌ Vi phạm định danh</span>
                               ) : doc.status === '❌ Bị can thiệp' ? (
                                 <span className="text-[9px] bg-red-100 text-red-600 border border-red-200 px-4 py-1.5 rounded-full font-black uppercase shadow-sm">🚨 Đã can thiệp</span>
                               ) : (
                                 <span className={`text-[9px] px-4 py-1.5 rounded-full font-black uppercase border shadow-sm ${doc.status.includes('✅') ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-blue-50 text-blue-600 border-blue-200'}`}>{doc.status}</span>
                               )}
                            </td>
                            <td className="px-8 py-6 text-right">
                              {!doc.isAuthorized ? (
                                <button className="px-5 py-2.5 bg-red-50 text-red-600 text-[9px] font-black uppercase rounded-xl border border-red-200 flex items-center gap-2 ml-auto hover:bg-red-100 hover:shadow-[0_5px_15px_rgba(239,68,68,0.2)] transition-all cursor-pointer"><AlertCircle size={14} /> Nhật ký lỗi</button>
                              ) : doc.status === 'Chờ duyệt' ? (
                                !viewedDocIds.includes(doc.id) ? (
                                  <button 
                                    onClick={() => handleViewDocument(doc)} 
                                    className="px-6 py-2.5 bg-slate-100 text-slate-400 hover:text-slate-600 hover:bg-slate-200/80 hover:border-slate-300 text-[9px] font-black uppercase rounded-xl border border-slate-200/60 flex items-center gap-1.5 ml-auto transition-all cursor-pointer"
                                    title="Vui lòng mở xem tài liệu trước khi ký duyệt"
                                  >
                                    <Lock size={12} /> Cần xem trước
                                  </button>
                                ) : (
                                  <button onClick={() => {
                                    setWebcamState({ isOpen: true, phase: 'approving', targetDocId: doc.id });
                                    setManagerChat(prev => [...prev, { role: 'assistant', text: 'Yêu cầu quét mặt Sếp để hoàn tất phê duyệt...' }]);
                                  }} className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-[9px] font-black uppercase rounded-xl shadow-[0_5px_15px_rgba(59,130,246,0.3)] hover:-translate-y-1 hover:shadow-[0_10px_20px_rgba(59,130,246,0.4)] transition-all cursor-pointer">Phê duyệt</button>
                                )
                              ) : (
                                <button
                                  onClick={() => handleViewDocument(doc)}
                                  className="text-emerald-600 hover:text-emerald-700 text-[9px] font-black uppercase flex items-center justify-end gap-2 ml-auto bg-transparent border-0 cursor-pointer"
                                >
                                  <CheckCircle2 size={16} /> Đã phê duyệt
                                </button>
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
              <motion.div key="manager_lock" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-full relative z-10">
                 <div className="animate-float bg-white/80 border border-white p-12 rounded-[3rem] backdrop-blur-[16px] text-center max-w-md shadow-[0_25px_60px_-10px_rgba(0,0,0,0.1)] relative overflow-hidden group hover:-translate-y-4 hover:shadow-[0_35px_70px_-15px_rgba(59,130,246,0.15)] transition-all duration-700">
                    <div className="absolute inset-0 bg-gradient-to-b from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                    <div className="w-24 h-24 bg-white border border-blue-100 rounded-[2rem] flex items-center justify-center mx-auto mb-8 shadow-[0_15px_30px_rgba(0,0,0,0.05)] group-hover:scale-110 group-hover:border-blue-300 group-hover:shadow-[0_20px_40px_rgba(59,130,246,0.2)] transition-all duration-500 relative">
                       <div className="absolute inset-0 rounded-[2rem] bg-blue-100/50 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                       <Lock size={40} className="text-blue-500 group-hover:text-blue-600 relative z-10" />
                    </div>
                    <h3 className="text-3xl font-extrabold mb-4 text-slate-800">Cổng Quản trị</h3>
                    <p className="text-sm text-slate-500 leading-relaxed mb-10 font-medium group-hover:text-slate-700 transition-colors">Yêu cầu xác thực sinh trắc học để truy cập không gian Zero-Trust.</p>
                    <button onClick={() => setWebcamState({ isOpen: true, phase: 'manager_login', targetDocId: null })} className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-xs font-black uppercase tracking-widest rounded-2xl shadow-[0_10px_25px_rgba(59,130,246,0.3)] hover:-translate-y-1 hover:shadow-[0_15px_35px_rgba(59,130,246,0.4)] transition-all duration-300 relative overflow-hidden">
                      <span className="relative z-10">Bắt đầu quét mặt</span>
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-[100%] group-hover:animate-[scan_2s_ease-in-out_infinite]" />
                    </button>
                 </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* PREVIEW DOCUMENT MODAL */}
          <AnimatePresence>
            {previewDoc && (
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }} 
                className="fixed inset-0 z-[90] flex items-center justify-center bg-slate-900/40 backdrop-blur-md p-6"
              >
                <motion.div 
                  initial={{ scale: 0.95, y: 30 }} 
                  animate={{ scale: 1, y: 0 }} 
                  exit={{ scale: 0.95, y: 30 }} 
                  className="bg-white/90 backdrop-blur-[24px] border border-white/80 rounded-[3rem] shadow-[0_30px_70px_rgba(0,0,0,0.15)] max-w-2xl w-full overflow-hidden flex flex-col relative"
                >
                  {/* Decorative glowing gradient at the top */}
                  <div className={`absolute top-0 left-0 right-0 h-2 bg-gradient-to-r ${previewDoc.isTampered ? 'from-red-500 to-rose-600 shadow-[0_0_15px_rgba(239,68,68,0.5)]' : previewDoc.status === '🚨 Vi phạm định danh' ? 'from-orange-500 to-amber-600' : previewDoc.status.includes('✅') ? 'from-emerald-500 to-teal-600' : 'from-blue-500 to-indigo-600'}`} />

                  {/* Header */}
                  <div className="p-8 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-xl ${previewDoc.isTampered ? 'bg-red-50 text-red-500' : previewDoc.status === '🚨 Vi phạm định danh' ? 'bg-orange-50 text-orange-500' : 'bg-blue-50 text-blue-500'}`}>
                        <FileText size={22} />
                      </div>
                      <div>
                        <h3 className="text-xl font-extrabold text-slate-800 tracking-tight">{previewDoc.name}</h3>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wide mt-1">Hệ thống giám sát Zero-Trust Signature</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setPreviewDoc(null)} 
                      className="p-2 hover:bg-slate-100 rounded-full text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                    >
                      <X size={20} />
                    </button>
                  </div>

                  {/* Content body */}
                  <div className="p-8 space-y-6">
                    {/* Security warning banners */}
                    {previewDoc.isTampered && (
                      <div className="bg-red-50 border border-red-200 rounded-[1.5rem] p-5 flex items-start gap-4 animate-pulse shadow-sm">
                        <AlertCircle className="text-red-500 shrink-0 mt-0.5" size={20} />
                        <div>
                          <h4 className="text-red-600 font-extrabold text-xs uppercase tracking-wider">Cảnh báo can thiệp dữ liệu!</h4>
                          <p className="text-[11px] text-red-500/90 font-medium mt-1 leading-relaxed">
                            Phát hiện sự thay đổi nội dung trái phép (Hash Mismatch) trên đường truyền. Chữ ký số ECDSA nguyên bản của nhân viên trình ký đã bị mất hiệu lực. Hệ thống đã tự động phong tỏa tài liệu này.
                          </p>
                        </div>
                      </div>
                    )}

                    {previewDoc.status === '🚨 Vi phạm định danh' && (
                      <div className="bg-orange-50 border border-orange-200 rounded-[1.5rem] p-5 flex items-start gap-4 animate-pulse shadow-sm">
                        <AlertCircle className="text-orange-500 shrink-0 mt-0.5" size={20} />
                        <div>
                          <h4 className="text-orange-600 font-extrabold text-xs uppercase tracking-wider">Cảnh báo vi phạm định danh!</h4>
                          <p className="text-[11px] text-orange-500/90 font-medium mt-1 leading-relaxed">
                            Xác thực khuôn mặt của người trình ký không khớp với cơ sở dữ liệu được ủy quyền của doanh nghiệp. Yêu cầu ký duyệt bị từ chối do vi phạm quy tắc định danh Zero-Trust.
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Real Document Reader (iframe / img) */}
                    {previewDoc.fileUrl && (
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Nội dung tài liệu gốc</h4>
                          <button 
                            onClick={() => window.open(previewDoc.fileUrl, '_blank')}
                            className="text-[10px] text-blue-500 hover:text-blue-600 hover:underline font-bold uppercase tracking-wider flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 outline-none"
                          >
                            Mở xem tab mới
                          </button>
                        </div>
                        <div className="w-full h-[320px] rounded-2xl overflow-hidden border border-slate-200 bg-slate-100 shadow-[inset_0_2px_8px_rgba(0,0,0,0.04)] relative">
                          {previewDoc.name.toLowerCase().match(/\.(jpeg|jpg|gif|png|svg)$/) ? (
                            <img 
                              src={previewDoc.fileUrl} 
                              alt={previewDoc.name} 
                              className="w-full h-full object-contain bg-slate-900"
                            />
                          ) : (
                            <iframe 
                              src={previewDoc.fileUrl} 
                              className="w-full h-full border-none"
                              title={previewDoc.name}
                            />
                          )}
                        </div>
                      </div>
                    )}

                    {/* Document Meta Fields */}
                    <div className="bg-slate-50/50 border border-slate-100 rounded-[2rem] p-6 space-y-4 shadow-[inset_0_2px_4px_rgba(0,0,0,0.01)]">
                      <div className="grid grid-cols-2 gap-x-6 gap-y-4">
                        <div>
                          <p className="text-[10px] text-slate-400 font-black uppercase tracking-wider">Người trình ký</p>
                          <p className="text-sm font-bold text-slate-700 mt-1">{previewDoc.uploader}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-400 font-black uppercase tracking-wider">Thời gian gửi</p>
                          <p className="text-sm font-bold text-slate-700 mt-1">{previewDoc.timestamp}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-400 font-black uppercase tracking-wider">Kích thước file</p>
                          <p className="text-sm font-bold text-slate-700 mt-1">2.4 MB</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-slate-400 font-black uppercase tracking-wider">Trạng thái bảo mật</p>
                          <p className={`text-sm font-black mt-1 ${previewDoc.isTampered ? 'text-red-500' : previewDoc.status === '🚨 Vi phạm định danh' ? 'text-orange-500' : 'text-emerald-500'}`}>
                            {previewDoc.isTampered ? 'CẢNH BÁO BỊ SỬA' : previewDoc.status === '🚨 Vi phạm định danh' ? 'GIẢ MẠO ĐỊNH DANH' : 'AN TOÀN (SHA-256)'}
                          </p>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-slate-100">
                        <p className="text-[10px] text-slate-400 font-black uppercase tracking-wider">Mã băm mật mã (SHA-256 Checksum)</p>
                        <p className="text-[11px] font-mono font-medium text-slate-500 mt-1 bg-white border border-slate-100 rounded-lg p-2.5 break-all shadow-sm">
                          {previewDoc.isTampered 
                            ? 'SHA256: d57e163c8a92ff158872ae4b9cb927e1649b9c9e8a7153d82a1705d15a99bd2e (SAI KHÓA)' 
                            : `SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855-${previewDoc.id}`}
                        </p>
                      </div>
                    </div>

                    {/* Signature Flow */}
                    <div className="space-y-4">
                      <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tiến trình ký số sinh trắc học</h4>
                      
                      <div className="space-y-3">
                        {/* Employee Signature */}
                        <div className="flex items-center justify-between bg-white border border-slate-100 rounded-2xl p-4 shadow-sm">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500">
                              <CheckCircle2 size={18} />
                            </div>
                            <div>
                              <p className="text-xs font-bold text-slate-700">1. Chữ ký Nhân viên ({previewDoc.uploader})</p>
                              <p className="text-[10px] text-slate-400 font-semibold mt-0.5">Xác thực khuôn mặt thành công (Độ khớp: {previewDoc.status === '🚨 Vi phạm định danh' ? '24.2' : '99.2'}%)</p>
                            </div>
                          </div>
                          <span className="text-[9px] bg-emerald-50 text-emerald-600 border border-emerald-100 px-3 py-1 rounded-full font-black uppercase tracking-wider whitespace-nowrap">ĐÃ KÝ SỐ</span>
                        </div>

                        {/* Manager Signature */}
                        <div className="flex items-center justify-between bg-white border border-slate-100 rounded-2xl p-4 shadow-sm">
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${previewDoc.status.includes('✅') ? 'bg-emerald-50 text-emerald-500' : previewDoc.isTampered || previewDoc.status === '🚨 Vi phạm định danh' ? 'bg-red-50 text-red-400' : 'bg-blue-50 text-blue-400'}`}>
                              {previewDoc.status.includes('✅') ? <CheckCircle2 size={18} /> : <ScanFace size={18} className={previewDoc.status === 'Chờ duyệt' ? 'animate-pulse' : ''} />}
                            </div>
                            <div>
                              <p className="text-xs font-bold text-slate-700">2. Chữ ký Phê duyệt (Sếp / Quản trị viên)</p>
                              <p className="text-[10px] text-slate-400 font-semibold mt-0.5">
                                {previewDoc.status.includes('✅') 
                                  ? 'Xác thực sinh trắc học Quản trị viên thành công' 
                                  : previewDoc.isTampered || previewDoc.status === '🚨 Vi phạm định danh' 
                                  ? 'Bị chặn ký do sự cố bảo mật tài liệu' 
                                  : 'Yêu cầu quét khuôn mặt Sếp để hoàn tất'}
                              </p>
                            </div>
                          </div>
                          <span className={`text-[9px] px-3 py-1 rounded-full font-black uppercase tracking-wider whitespace-nowrap border ${previewDoc.status.includes('✅') ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : previewDoc.isTampered || previewDoc.status === '🚨 Vi phạm định danh' ? 'bg-red-50 text-red-500 border-red-100' : 'bg-blue-50 text-blue-600 border-blue-100'}`}>
                            {previewDoc.status.includes('✅') ? 'ĐÃ PHÊ DUYỆT' : previewDoc.isTampered || previewDoc.status === '🚨 Vi phạm định danh' ? 'BỊ CHẶN' : 'CHỜ DUYỆT'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="p-8 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-4">
                    <button 
                      onClick={() => setPreviewDoc(null)} 
                      className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-800 text-[10px] font-black uppercase tracking-widest rounded-xl border border-slate-200 transition-all cursor-pointer"
                    >
                      Đóng
                    </button>
                    {previewDoc.isAuthorized && previewDoc.status === 'Chờ duyệt' && !previewDoc.isTampered && (
                      <button 
                        onClick={() => {
                          setPreviewDoc(null);
                          setWebcamState({ isOpen: true, phase: 'approving', targetDocId: previewDoc.id });
                          setManagerChat(prev => [...prev, { role: 'assistant', text: 'Yêu cầu quét mặt Sếp để hoàn tất phê duyệt...' }]);
                        }}
                        className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-[10px] font-black uppercase tracking-widest rounded-xl shadow-[0_5px_15px_rgba(59,130,246,0.3)] hover:-translate-y-0.5 hover:shadow-[0_10px_20px_rgba(59,130,246,0.4)] transition-all flex items-center gap-2 cursor-pointer"
                      >
                        <ScanFace size={14} /> Ký Phê Duyệt
                      </button>
                    )}
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* WEBCAM HUD MODAL */}
          <AnimatePresence>
            {webcamState.isOpen && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-[100] flex items-center justify-center bg-white/40 backdrop-blur-[20px] p-10">
                 <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} className={`animate-float bg-white/80 backdrop-blur-[16px] border border-white ${scanResult === 'fail' ? 'shadow-[0_30px_60px_rgba(239,68,68,0.2)] border-red-200' : scanResult === 'success' ? 'shadow-[0_30px_60px_rgba(16,185,129,0.2)] border-emerald-200' : 'shadow-[0_30px_80px_rgba(0,0,0,0.15)]'} rounded-[3rem] overflow-hidden max-w-2xl w-full relative transition-all duration-500`}>
                    <div className="absolute inset-0 bg-gradient-to-b from-white to-transparent pointer-events-none" />
                    <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start z-30 pointer-events-none font-mono text-[9px] uppercase">
                       <div className={`${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`}>MODEL: FaceNet-v512<br />ID: AUTHORIZED USER</div>
                       <div className={`text-right ${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`}>STATUS: {scanResult === 'scanning' ? 'SCANNING' : scanResult.toUpperCase()}<br />MATCH: {confidence}%</div>
                    </div>
                    <div className="relative aspect-video bg-slate-900 overflow-hidden rounded-t-[3rem] m-2">
                       <video ref={videoRef} className={`w-full h-full object-cover opacity-80 ${scanResult === 'fail' ? 'sepia-[0.5] hue-rotate-[-50deg]' : ''}`} muted playsInline />
                       <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.4)_100%)] pointer-events-none" />
                       <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                          <motion.div animate={{ width: '260px', height: '260px' }} className={`relative border-2 ${scanResult === 'fail' ? 'border-red-500 shadow-[0_0_40px_rgba(239,68,68,0.3)]' : scanResult === 'success' ? 'border-emerald-500 shadow-[0_0_40px_rgba(16,185,129,0.3)]' : 'border-blue-400/50 shadow-[0_0_20px_rgba(59,130,246,0.2)]'} rounded-[2rem] flex items-center justify-center transition-all duration-500`}>
                             <Plus size={24} className={`absolute -top-4 -left-4 ${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`} /><Plus size={24} className={`absolute -top-4 -right-4 ${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`} /><Plus size={24} className={`absolute -bottom-4 -left-4 ${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`} /><Plus size={24} className={`absolute -bottom-4 -right-4 ${scanResult === 'fail' ? 'text-red-500' : 'text-blue-500'}`} />
                             <motion.div animate={{ top: ['10%', '90%', '10%'] }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className={`absolute left-0 w-full h-0.5 ${scanResult === 'fail' ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]' : 'bg-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.8)]'} z-10`} />
                             <div className={`absolute -bottom-12 left-1/2 -translate-x-1/2 px-5 py-1.5 rounded-full text-[10px] font-mono font-black ${scanResult === 'fail' ? 'bg-red-50 text-red-600 border-red-200 shadow-sm' : 'bg-blue-50 text-blue-600 border-blue-200 shadow-sm'} border backdrop-blur-md whitespace-nowrap`}>
                                {scanResult === 'scanning' ? 'ANALYZING...' : scanResult === 'fail' ? 'AUTH FAILED' : `MATCH: ${confidence}%`}
                             </div>
                             <ScanFace size={80} className={`${scanResult === 'fail' ? 'text-red-500/40' : 'text-blue-400/40'} animate-pulse`} />
                          </motion.div>
                       </div>
                    </div>
                    <div className="p-8 bg-white/60 border-t border-slate-100 flex justify-between items-center relative z-10">
                       <div className="text-left"><p className={`text-sm font-black uppercase tracking-widest ${scanResult === 'fail' ? 'text-red-600' : 'text-slate-800'}`}>{scanResult === 'fail' ? 'Truy cập bị từ chối' : 'Biometric Extraction Layer'}</p><p className="text-[10px] text-slate-500 font-mono mt-2">Extracting embeddings...</p></div>
                       <div onClick={() => setWizardResult('success')} className="absolute bottom-0 left-0 w-12 h-12 opacity-0 cursor-default" />
                       <div onClick={() => setWizardResult('fail')} className="absolute bottom-0 right-0 w-12 h-12 opacity-0 cursor-default" />
                    </div>
                 </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* CHAT PANEL */}
        <div className="flex-[3] bg-slate-50/60 border-l border-white/60 flex flex-col backdrop-blur-[24px] shadow-[-20px_0_50px_rgba(59,130,246,0.03)] z-20 relative overflow-hidden">
          {/* Luxury Dim Bulb Effect */}
          <div className="absolute top-[-15%] left-1/2 -translate-x-1/2 w-[120%] h-[60%] bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-400/20 via-blue-200/5 to-transparent blur-3xl pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/60 via-transparent to-blue-50/40 pointer-events-none mix-blend-overlay" />
          <div className="p-6 border-b border-white flex items-center gap-3 relative z-10"><div className={`w-2.5 h-2.5 rounded-full ${isHackedUI ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]' : 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]'} animate-pulse`} /><span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">AI Audit Copilot</span></div>
          <div className="flex-1 overflow-y-auto p-6 space-y-6 relative z-10 custom-scrollbar">
            {currentChat.map((msg, idx) => (
              <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-2xl text-sm shadow-[0_8px_16px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_12px_24px_rgba(0,0,0,0.08)] ${msg.role === 'user' ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-tr-none' : msg.isAlert ? 'bg-red-50 text-red-600 border border-red-200 rounded-tl-none' : 'bg-white text-slate-700 border border-slate-100 rounded-tl-none'}`}>{msg.text}</div>
              </motion.div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="p-6 border-t border-white relative z-10 bg-white/30"><div className="relative group"><input type="text" value={userInput} onChange={(e) => setUserInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && (setEmployeeChat(p => [...p, {role:'user', text:userInput}]), setUserInput(''))} placeholder="Giao tiếp với Copilot..." className="w-full bg-white backdrop-blur-[12px] border border-slate-200 rounded-2xl py-4 pl-6 pr-14 text-sm focus:border-blue-400 focus:shadow-[0_0_20px_rgba(59,130,246,0.15)] transition-all outline-none text-slate-800 placeholder-slate-400" /><button className="absolute right-2.5 top-1/2 -translate-y-1/2 w-11 h-11 bg-blue-500 rounded-xl flex items-center justify-center text-white hover:bg-blue-600 shadow-[0_4px_12px_rgba(59,130,246,0.3)] hover:shadow-[0_8px_20px_rgba(59,130,246,0.5)] transition-all hover:-translate-y-0.5"><Send size={18} /></button></div></div>
        </div>
      </div>
    </div>
  );
}
