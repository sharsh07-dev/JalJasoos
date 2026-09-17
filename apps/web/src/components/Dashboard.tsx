"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Droplet, Activity, Battery, Wifi, LogOut, Map, AlertCircle, Wrench, ChevronRight, CheckCircle2, Building, Database, BarChart2, Layers, Camera } from 'lucide-react';

// Apple HIG Colors
const APPLE = {
  blue: '#0071E3',
  green: '#34C759',
  red: '#FF3B30',
  orange: '#FF9500',
  gray: '#86868B',
  dark: '#1D1D1F',
  bg: '#F5F5F7',
  white: '#FFFFFF'
};

let GLOBAL_IS_LEAK_ACTIVE = false;
let GLOBAL_VALVE_STATE: 'OPEN' | 'CLOSING' | 'CLOSED' = 'OPEN';
let GLOBAL_REPAIR_STEP: 'IDLE' | 'IN_PROGRESS' | 'VERIFYING' | 'VERIFIED' | 'FAILED' = 'IDLE';
let GLOBAL_PREVIOUS_ROLE: string | null = null;
let GLOBAL_REPAIR_LOGS: any[] = [];
if (typeof window !== 'undefined') {
  try {
    const saved = localStorage.getItem('jaljasoos_repair_logs');
    if (saved) GLOBAL_REPAIR_LOGS = JSON.parse(saved);
  } catch (e) {}
}

export default function Dashboard() {
  const { user, logout, loading, login } = useAuth();
  const [data, setData] = useState<any[]>([]);
  
  const [isLeakActive, _setIsLeakActive] = useState(GLOBAL_IS_LEAK_ACTIVE);
  const [valveState, _setValveState] = useState(GLOBAL_VALVE_STATE);
  const [repairStep, _setRepairStep] = useState(GLOBAL_REPAIR_STEP);
  const [showMap, setShowMap] = useState(false);
  const [activeAdminTab, setActiveAdminTab] = useState('OVERVIEW');
  const [adminModal, setAdminModal] = useState<{type: string, title: string, placeholder?: string, step: 'INPUT' | 'PROCESSING' | 'SUCCESS'} | null>(null);
  const [proofPhoto, setProofPhoto] = useState<string | null>(null);
  const [repairLogs, setRepairLogs] = useState<any[]>(GLOBAL_REPAIR_LOGS);

  const setIsLeakActive = (val: boolean) => {
    GLOBAL_IS_LEAK_ACTIVE = val;
    _setIsLeakActive(val);
  };

  const setValveState = (val: 'OPEN' | 'CLOSING' | 'CLOSED') => {
    GLOBAL_VALVE_STATE = val;
    _setValveState(val);
  };

  const setRepairStep = (val: 'IDLE' | 'IN_PROGRESS' | 'VERIFYING' | 'VERIFIED' | 'FAILED') => {
    GLOBAL_REPAIR_STEP = val;
    _setRepairStep(val);
  };
  
  // VERCEL PROTOTYPE: Purely client-side simulation (No Backend)
  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick += 1;
      
      setData(prev => {
        const newData = prev.length >= 25 ? [...prev.slice(1)] : [...prev];
        const now = new Date();
        
        let flow = 15.0 + Math.sin(tick * 0.1) * 2.0;
        let pressure = 2.8 + Math.cos(tick * 0.2) * 0.1;
        let acoustic = 0.1 + Math.random() * 0.05;
        
        if (valveState === 'CLOSED') {
          flow = 0.0;
          pressure = 3.0; 
          acoustic = 0.02;
        } else if (isLeakActive) {
          flow += 12.0; 
          pressure -= 1.2; 
          acoustic += 0.8 + Math.random() * 0.2; 
        }
        
        newData.push({
          time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          flow: Number(flow.toFixed(2)),
          pressure: Number(pressure.toFixed(2)),
          acoustic: Number(acoustic.toFixed(3))
        });
        
        return newData;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isLeakActive, valveState]);

  const triggerPhysicalLeak = () => {
    if (valveState !== 'OPEN') return;
    setIsLeakActive(true);
    setRepairStep('IDLE');
    
    // Auto-close simulation
    setTimeout(() => {
      setValveState('CLOSING');
      setTimeout(() => {
        setValveState('CLOSED');
        setIsLeakActive(false);
      }, 3000);
    }, 4000);
  };

  const triggerRealLeak = () => {
    triggerPhysicalLeak();
  };

  const triggerValve = () => {
    if (valveState === 'OPEN') {
      setValveState('CLOSING');
      setTimeout(() => {
        setValveState('CLOSED');
        setIsLeakActive(false);
      }, 3000);
    }
  };

  const repairPipe = () => {
    setValveState('OPEN');
    setIsLeakActive(false);
  };

  if (loading) return null;
  if (!user) return null;

  // ----------------------------------------------------------------------
  // COMMON COMPONENTS
  // ----------------------------------------------------------------------
  const Header = () => (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 border-b border-black/5 px-6 py-4 mb-8">
      <div className="max-w-[1200px] mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
            <Droplet className="text-white" strokeWidth={2} size={18} />
          </div>
          <h1 className="text-[19px] font-semibold tracking-tight text-[#1D1D1F]">
            JalJasoos <span className="text-[#86868B] font-normal mx-1">|</span> <span className="text-[#86868B] font-normal text-[17px]">{user.role.replace('_', ' ')}</span>
          </h1>
        </div>
        <div className="flex items-center gap-6">
          {GLOBAL_PREVIOUS_ROLE === 'SUPER_ADMIN' && user.role !== 'SUPER_ADMIN' && (
            <button 
              onClick={() => {
                GLOBAL_PREVIOUS_ROLE = null;
                login('SUPER_ADMIN');
              }} 
              className="text-[13px] font-medium text-[#1D1D1F] hover:text-[#0071E3] transition-colors flex items-center gap-1.5 bg-[#F5F5F7] hover:bg-[#E5E5EA] px-4 py-1.5 rounded-full"
            >
              ← Back to Global Admin
            </button>
          )}
          <button 
            onClick={() => {
              GLOBAL_PREVIOUS_ROLE = null;
              logout();
            }} 
            className="text-[14px] font-medium text-[#FF3B30] hover:text-[#FF3B30]/80 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );

  const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
    <div className={`bg-white rounded-[24px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-6 ${className}`}>
      {children}
    </div>
  );

  // ----------------------------------------------------------------------
  // RESIDENT DASHBOARD
  // ----------------------------------------------------------------------
  if (user.role === 'RESIDENT') {
    const weeklyData = [
      { day: 'Mon', usage: 240 },
      { day: 'Tue', usage: 210 },
      { day: 'Wed', usage: 280 },
      { day: 'Thu', usage: 265 },
      { day: 'Fri', usage: 310 },
      { day: 'Sat', usage: 350 },
      { day: 'Sun', usage: 284 },
    ];

    return (
      <div className="min-h-screen bg-[#F5F5F7] font-sans selection:bg-[#0071E3] selection:text-white pb-12">
        <Header />
        <div className="max-w-[1000px] mx-auto px-4 sm:px-6 space-y-6">
          
          <div className="mb-8">
            <h2 className="text-[32px] font-semibold tracking-tight text-[#1D1D1F]">
              My Apartment
            </h2>
            <p className="text-[17px] text-[#86868B] mt-1">A-304 • Simplicity Society</p>
          </div>

          {/* ACTIVE ALERT */}
          {isLeakActive && (
            <div className="bg-[#FF3B30]/10 border border-[#FF3B30]/20 rounded-[24px] p-5 flex items-start gap-4 shadow-sm animate-in fade-in slide-in-from-top-2 duration-300">
               <div className="bg-[#FF3B30] text-white p-2.5 rounded-full shrink-0">
                  <AlertCircle size={24} strokeWidth={2.5} />
               </div>
               <div className="flex-1">
                  <h3 className="text-[18px] font-semibold text-[#FF3B30] tracking-tight">Possible Water Leak</h3>
                  <p className="text-[14.5px] text-[#1D1D1F] mt-1 font-medium">Unusual continuous water usage detected in your apartment.</p>
                  <button className="mt-4 bg-white border border-[#E5E5EA] text-[#1D1D1F] px-5 py-2.5 rounded-full text-[13px] font-semibold shadow-[0_2px_10px_rgb(0,0,0,0.04)] hover:bg-[#F5F5F7] transition-colors">
                    View Details
                  </button>
               </div>
            </div>
          )}

          {/* METRICS */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="flex flex-col justify-center py-6">
              <p className="text-[12px] font-bold text-[#86868B] mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <Droplet size={14} className="text-[#0071E3]" strokeWidth={2.5}/> Today's Consumption
              </p>
              <p className="text-[40px] font-semibold tracking-tight text-[#1D1D1F] leading-none mt-1">
                284<span className="text-[18px] text-[#86868B] font-normal ml-1">L</span>
              </p>
            </Card>
            
            <Card className="flex flex-col justify-center py-6">
              <p className="text-[12px] font-bold text-[#86868B] mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart2 size={14} className="text-[#34C759]" strokeWidth={2.5}/> Weekly Average
              </p>
              <p className="text-[40px] font-semibold tracking-tight text-[#1D1D1F] leading-none mt-1">
                245<span className="text-[18px] text-[#86868B] font-normal ml-1">L/day</span>
              </p>
            </Card>
            
            <Card className="flex flex-col justify-center py-6">
              <p className="text-[12px] font-bold text-[#86868B] mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <Activity size={14} className="text-[#FF9500]" strokeWidth={2.5}/> Estimated Usage
              </p>
              <p className="text-[40px] font-semibold tracking-tight text-[#1D1D1F] leading-none mt-1">
                ₹340<span className="text-[18px] text-[#86868B] font-normal ml-1">/mo</span>
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
             {/* CHART */}
             <Card className="h-full flex flex-col">
               <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-6">Weekly Consumption</h3>
               <div className="flex-1 min-h-[220px] w-full">
                 <ResponsiveContainer width="100%" height="100%">
                   <BarChart data={weeklyData}>
                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5EA" />
                     <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 13}} dy={10} />
                     <YAxis axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 13}} dx={-10} />
                     <Tooltip cursor={{fill: '#F5F5F7'}} contentStyle={{borderRadius: '12px', border: '1px solid #E5E5EA', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', fontWeight: 500}} />
                     <Bar dataKey="usage" fill="#0071E3" radius={[6, 6, 0, 0]} barSize={32} isAnimationActive={false} />
                   </BarChart>
                 </ResponsiveContainer>
               </div>
             </Card>

             {/* NOTIFICATIONS */}
             <Card className="h-full">
               <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-6">Recent Notifications</h3>
               <div className="space-y-4">
                  {isLeakActive && (
                    <div className="flex gap-4 p-4 bg-[#F5F5F7] rounded-[16px]">
                       <div className="bg-[#FF3B30]/10 text-[#FF3B30] p-2.5 rounded-full shrink-0 h-fit"><AlertCircle size={18} strokeWidth={2.5}/></div>
                       <div>
                         <p className="text-[14px] font-semibold text-[#1D1D1F]">High Usage Alert</p>
                         <p className="text-[13px] text-[#86868B] mt-0.5 leading-snug">Unusual consumption detected. Please verify there are no open taps.</p>
                         <p className="text-[11px] text-[#86868B] mt-2 font-bold uppercase tracking-wider">Just Now</p>
                       </div>
                    </div>
                  )}
                  <div className="flex gap-4 p-4 bg-[#F5F5F7] rounded-[16px]">
                     <div className="bg-[#FF9500]/10 text-[#FF9500] p-2.5 rounded-full shrink-0 h-fit"><Wrench size={18} strokeWidth={2.5}/></div>
                     <div>
                       <p className="text-[14px] font-semibold text-[#1D1D1F]">Planned Water Shutdown</p>
                       <p className="text-[13px] text-[#86868B] mt-0.5 leading-snug">Maintenance scheduled for Main Tank A. Water unavailable between 2 PM - 4 PM.</p>
                       <p className="text-[11px] text-[#86868B] mt-2 font-bold uppercase tracking-wider">Yesterday</p>
                     </div>
                  </div>
                  <div className="flex gap-4 p-4 bg-[#F5F5F7] rounded-[16px]">
                     <div className="bg-[#34C759]/10 text-[#34C759] p-2.5 rounded-full shrink-0 h-fit"><Building size={18} strokeWidth={2.5}/></div>
                     <div>
                       <p className="text-[14px] font-semibold text-[#1D1D1F]">Quarterly Filter Maintenance</p>
                       <p className="text-[13px] text-[#86868B] mt-0.5 leading-snug">Your block's RO filters were successfully replaced.</p>
                       <p className="text-[11px] text-[#86868B] mt-2 font-bold uppercase tracking-wider">Oct 12</p>
                     </div>
                  </div>
               </div>
             </Card>
          </div>
        </div>
      </div>
    );
  }

  // ----------------------------------------------------------------------
  // MAINTENANCE STAFF DASHBOARD
  // ----------------------------------------------------------------------
  if (user.role === 'MAINTENANCE_STAFF') {
    const handleStartRepair = () => {
      setRepairStep('IN_PROGRESS');
      setProofPhoto(null);
    };
    
    const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
          const img = new Image();
          img.onload = () => {
            const canvas = document.createElement('canvas');
            const MAX_WIDTH = 600;
            const scaleSize = MAX_WIDTH / img.width;
            canvas.width = MAX_WIDTH;
            canvas.height = img.height * scaleSize;
            const ctx = canvas.getContext('2d');
            if (ctx) ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const base64 = canvas.toDataURL('image/jpeg', 0.6); // Compress to save localStorage quota
            setProofPhoto(base64);
          };
          img.src = event.target?.result as string;
        };
        reader.readAsDataURL(file);
      }
    };

    const handleRepairCompleted = () => {
      setRepairStep('VERIFYING');
      setTimeout(() => {
        setRepairStep('VERIFIED');
        repairPipe();

        if (proofPhoto) {
          const newLog = {
             id: Date.now(),
             date: new Date().toLocaleString(),
             node: 'NODE-A3-04',
             photo: proofPhoto
          };
          const updatedLogs = [newLog, ...GLOBAL_REPAIR_LOGS];
          GLOBAL_REPAIR_LOGS = updatedLogs;
          setRepairLogs(updatedLogs);
          try {
            localStorage.setItem('jaljasoos_repair_logs', JSON.stringify(updatedLogs));
          } catch (e) {
            console.error("Storage quota exceeded", e);
          }
        }
      }, 4000);
    };

    return (
      <div className="min-h-screen bg-[#F5F5F7] font-sans selection:bg-[#0071E3] selection:text-white pb-12">
        <Header />
        <div className="max-w-[700px] mx-auto px-6 space-y-6">
          <div className="mb-8">
            <h2 className="text-[32px] font-semibold tracking-tight text-[#1D1D1F]">Active Task</h2>
            <p className="text-[17px] text-[#86868B] mt-1">Field operations and repairs</p>
          </div>

          {(isLeakActive || valveState === 'CLOSED' || repairStep === 'VERIFIED') ? (
            <Card className={`border-2 ${repairStep === 'VERIFIED' ? 'border-[#34C759]/30 shadow-[0_8px_30px_rgb(52,199,89,0.12)]' : (repairStep === 'VERIFYING' ? 'border-[#0071E3]/30 shadow-[0_8px_30px_rgb(0,113,227,0.12)]' : 'border-[#FF3B30]/30 shadow-[0_8px_30px_rgb(255,59,48,0.12)]')}`}>
              
              {/* Header */}
              <div className="flex justify-between items-start mb-6">
                <div className="flex gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${repairStep === 'VERIFIED' ? 'bg-[#34C759]/10' : (repairStep === 'VERIFYING' ? 'bg-[#0071E3]/10' : 'bg-[#FF3B30]/10')}`}>
                    {repairStep === 'VERIFIED' ? <CheckCircle2 className="text-[#34C759]" size={24} /> : (repairStep === 'VERIFYING' ? <Activity className="text-[#0071E3]" size={24} /> : <AlertCircle className="text-[#FF3B30]" size={24} />)}
                  </div>
                  <div>
                    {repairStep === 'VERIFIED' ? (
                      <span className="inline-block px-2 py-1 bg-[#34C759] text-white text-[11px] font-bold rounded-md uppercase tracking-wide mb-1">Resolved</span>
                    ) : (
                      <span className="inline-block px-2 py-1 bg-[#FF3B30] text-white text-[11px] font-bold rounded-md uppercase tracking-wide mb-1">Urgent Request</span>
                    )}
                    <h3 className="text-[22px] font-semibold text-[#1D1D1F]">
                      {repairStep === 'VERIFIED' ? 'Repair Verified' : (repairStep === 'VERIFYING' ? 'System Verification' : 'High Pressure Pipe Burst')}
                    </h3>
                    <p className="text-[15px] text-[#86868B] mt-1">NODE-A3-04 • Simplicity Society</p>
                  </div>
                </div>
              </div>

              {repairStep === 'VERIFYING' && (
                <div className="py-8 text-center space-y-4">
                   <div className="w-12 h-12 border-4 border-[#F5F5F7] border-t-[#0071E3] rounded-full animate-spin mx-auto mb-6"></div>
                   <p className="text-[15px] font-medium text-[#1D1D1F]">Running system diagnostics...</p>
                   <ul className="text-[13px] text-[#86868B] text-left max-w-[200px] mx-auto space-y-2 mt-4">
                     <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#34C759]"/> Pressure returned to baseline</li>
                     <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#34C759]"/> Flow normalizing</li>
                     <li className="flex items-center gap-2"><Activity size={14} className="text-[#0071E3] animate-pulse"/> Analyzing acoustic signature...</li>
                   </ul>
                </div>
              )}

              {repairStep === 'VERIFIED' && (
                <div className="py-6 text-center">
                   <div className="text-[64px] mb-4">🟢</div>
                   <h3 className="text-[20px] font-semibold text-[#1D1D1F]">REPAIR VERIFIED</h3>
                   <p className="text-[15px] text-[#86868B] mt-2 mb-8">All sensor readings have returned to optimal baseline parameters.</p>
                   <button onClick={() => setRepairStep('IDLE')} className="px-8 py-3 bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] rounded-full font-medium text-[15px] transition-colors">
                     Back to Tasks
                   </button>
                </div>
              )}

              {(repairStep === 'IDLE' || repairStep === 'IN_PROGRESS') && (
                <>
                  {/* Context Data */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-[#F5F5F7] p-4 rounded-[16px]">
                      <p className="text-[13px] text-[#86868B] font-medium">Exact Location</p>
                      <p className="text-[15px] font-semibold text-[#1D1D1F] mt-1">Building A, Floor 3 (North)</p>
                    </div>
                    <div className="bg-[#F5F5F7] p-4 rounded-[16px]">
                      <p className="text-[13px] text-[#86868B] font-medium">Time Detected</p>
                      <p className="text-[15px] font-semibold text-[#1D1D1F] mt-1">Just now</p>
                    </div>
                    <div className="bg-[#F5F5F7] p-4 rounded-[16px]">
                      <p className="text-[13px] text-[#86868B] font-medium">Valve Status</p>
                      <p className={`text-[15px] font-semibold mt-1 ${valveState === 'CLOSED' ? 'text-[#FF9500]' : 'text-[#34C759]'}`}>{valveState}</p>
                    </div>
                    <div className="bg-[#F5F5F7] p-4 rounded-[16px]">
                      <p className="text-[13px] text-[#86868B] font-medium">Sensor Anomalies</p>
                      <p className="text-[15px] font-semibold text-[#FF3B30] mt-1">Flow Surge, Low Pres.</p>
                    </div>
                  </div>

                  {/* Instructions */}
                  <div className="mb-6 pl-4 border-l-2 border-[#E5E5EA]">
                    <h4 className="text-[14px] font-semibold text-[#1D1D1F] mb-3">Repair Instructions</h4>
                    <ul className="space-y-2 text-[14px] text-[#86868B]">
                      <li className="flex gap-2"><span>1.</span> Ensure area is clear of electrical hazards.</li>
                      <li className="flex gap-2"><span>2.</span> Identify exact source of rupture on A3-04 segment.</li>
                      <li className="flex gap-2"><span>3.</span> Apply heavy-duty pipe patch or replace segment.</li>
                    </ul>
                  </div>

                  {/* Actions */}
                  <div className="space-y-3 pt-6 border-t border-[#F5F5F7]">
                    {repairStep === 'IDLE' ? (
                      <>
                        <button onClick={handleStartRepair} className="w-full bg-[#0071E3] hover:bg-[#0077ED] text-white py-3.5 rounded-full font-medium transition-colors text-[16px] shadow-sm">
                          Start Repair
                        </button>
                        <button onClick={() => setShowMap(!showMap)} className="w-full bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] py-3.5 rounded-full font-medium transition-colors text-[16px] flex items-center justify-center gap-2">
                          <Map size={18} /> {showMap ? 'Hide Map' : 'Navigate to Location'}
                        </button>

                        {showMap && (
                          <div className="bg-[#1D1D1F] p-5 rounded-[20px] mt-4 shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
                            <div className="w-full h-[200px] bg-black/40 rounded-[12px] flex items-center justify-center relative overflow-hidden mb-4">
                              <svg width="100%" height="100%" viewBox="0 0 100 100">
                                <line x1="50" y1="15" x2="50" y2="85" stroke="#333333" strokeWidth="4" strokeLinecap="round" />
                                <circle cx="50" cy="15" r="5" fill="#555555" />
                                <line x1="50" y1="40" x2="25" y2="40" stroke="#333333" strokeWidth="3" />
                                <circle cx="25" cy="40" r="4" fill="#555555" />
                                <line x1="50" y1="60" x2="75" y2="60" stroke="#333333" strokeWidth="3" />
                                <circle cx="75" cy="60" r="4" fill="#555555" />
                                <line x1="50" y1="80" x2="25" y2="80" stroke="#0071E3" strokeWidth="3" strokeDasharray="2 2" className="animate-pulse" />
                                <rect x="35" y="77.5" width="4" height="5" rx="1" fill="#FF9500" />
                                <circle cx="25" cy="80" r="10" fill="#0071E3" opacity="0.2" className="animate-ping" />
                                <circle cx="25" cy="80" r="4" fill="#0071E3" />
                                <text x="25" y="32" fill="#555555" fontSize="4.5" textAnchor="middle" fontWeight="500">A1-01</text>
                                <text x="75" y="52" fill="#555555" fontSize="4.5" textAnchor="middle" fontWeight="500">A2-02</text>
                                <text x="25" y="91" fill="#0071E3" fontSize="5" textAnchor="middle" fontWeight="600">A3-04 (Target)</text>
                              </svg>
                            </div>
                            <div className="flex gap-3 items-start">
                              <div className="w-8 h-8 rounded-full bg-[#0071E3]/20 flex items-center justify-center shrink-0 mt-0.5">
                                <Map size={16} className="text-[#0071E3]" />
                              </div>
                              <div>
                                <p className="text-[14px] font-semibold text-white">Route Active</p>
                                <p className="text-[13px] text-[#86868B]">Proceed to Basement Level 3, North Wall. Follow the blue tracer lines on your AR headset.</p>
                              </div>
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        <div className="mb-4">
                          <p className="text-[13px] font-semibold text-[#1D1D1F] mb-2">Proof of Work <span className="text-[#FF3B30]">*</span></p>
                          {!proofPhoto ? (
                            <label className="w-full h-[120px] border-2 border-dashed border-[#E5E5EA] rounded-[16px] flex flex-col items-center justify-center text-[#86868B] cursor-pointer hover:bg-[#F5F5F7] transition-colors">
                              <Camera size={24} className="mb-2" />
                              <span className="text-[14px] font-medium">Tap to take photo</span>
                              <input type="file" accept="image/*" className="hidden" onChange={handlePhotoUpload} />
                            </label>
                          ) : (
                            <div className="relative w-full h-[120px] rounded-[16px] overflow-hidden border border-[#E5E5EA]">
                              <img src={proofPhoto} alt="Repair Proof" className="w-full h-full object-cover" />
                              <label className="absolute bottom-2 right-2 bg-black/60 text-white px-3 py-1.5 rounded-full text-[12px] font-medium backdrop-blur-md cursor-pointer hover:bg-black/80">
                                Retake
                                <input type="file" accept="image/*" className="hidden" onChange={handlePhotoUpload} />
                              </label>
                            </div>
                          )}
                        </div>

                        <button 
                          onClick={handleRepairCompleted} 
                          disabled={!proofPhoto}
                          className={`w-full py-3.5 rounded-full font-medium transition-colors text-[16px] shadow-sm flex items-center justify-center gap-2 ${proofPhoto ? 'bg-[#34C759] hover:bg-[#34C759]/90 text-white' : 'bg-[#E5E5EA] text-[#86868B] cursor-not-allowed'}`}
                        >
                          <CheckCircle2 size={18} /> {proofPhoto ? 'Submit Verification' : 'Photo Required'}
                        </button>
                        
                        <div className="grid grid-cols-1 mt-3">
                          <button className="bg-[#F5F5F7] hover:bg-[#E5E5EA] text-[#1D1D1F] py-3 rounded-full font-medium transition-colors text-[14px]">
                            Add Maintenance Note
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </>
              )}
            </Card>
          ) : (
            <div className="space-y-6">
              <Card className="text-center py-20">
                <div className="w-20 h-20 bg-[#F5F5F7] rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="text-[#34C759]" size={40} strokeWidth={2} />
                </div>
                <h3 className="text-[22px] font-semibold text-[#1D1D1F]">No Active Incidents</h3>
                <p className="text-[15px] text-[#86868B] mt-2 max-w-[280px] mx-auto">The pipeline network is running smoothly. Grab a coffee!</p>
              </Card>

              {repairLogs.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-[20px] font-semibold text-[#1D1D1F] mb-4">Completed Work Orders</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                     {repairLogs.map((log: any) => (
                       <div key={log.id} className="bg-white p-4 rounded-[16px] shadow-[0_4px_20px_rgb(0,0,0,0.04)] border border-[#E5E5EA] flex gap-4">
                          <img src={log.photo} alt="Repair log" className="w-20 h-20 rounded-[12px] object-cover bg-[#F5F5F7]" />
                          <div>
                             <p className="font-semibold text-[#1D1D1F] text-[15px]">{log.node}</p>
                             <p className="text-[13px] text-[#86868B] mt-1">{log.date}</p>
                             <div className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 bg-[#34C759]/10 rounded-md">
                               <CheckCircle2 size={12} className="text-[#34C759]" />
                               <span className="text-[11px] font-bold text-[#34C759] uppercase tracking-wide">Verified</span>
                             </div>
                          </div>
                       </div>
                     ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ----------------------------------------------------------------------
  // SUPER ADMIN DASHBOARD
  // ----------------------------------------------------------------------
  if (user.role === 'SUPER_ADMIN') {
    const adminTabs = ['OVERVIEW', 'INFRASTRUCTURE', 'DEVICES', 'SENSORS_&_VALVES', 'AI_MODELS', 'USERS', 'SYSTEM_HEALTH'];

    return (
      <div className="min-h-screen bg-[#F5F5F7] font-sans selection:bg-[#0071E3] selection:text-white pb-12">
        <Header />
        
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          <div className="mb-6 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
            <div>
              <h2 className="text-[32px] font-semibold tracking-tight text-[#1D1D1F]">System Management</h2>
              <p className="text-[17px] text-[#86868B] mt-1">Super Admin Console</p>
            </div>
            
            <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar" style={{scrollbarWidth: 'none'}}>
              {adminTabs.map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveAdminTab(tab)}
                  className={`px-5 py-2.5 rounded-full text-[14px] font-medium whitespace-nowrap transition-colors ${activeAdminTab === tab ? 'bg-[#1D1D1F] text-white shadow-sm' : 'bg-white text-[#86868B] border border-[#E5E5EA] hover:bg-[#F5F5F7] hover:text-[#1D1D1F]'}`}
                >
                  {tab.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* TAB: OVERVIEW */}
          {activeAdminTab === 'OVERVIEW' && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                  { label: "Managed Societies", value: "12", unit: "", color: APPLE.blue },
                  { label: "Active Gateways", value: "14", unit: "", color: APPLE.dark },
                  { label: "Water Saved (YTD)", value: "2.4M", unit: "L", color: APPLE.green },
                  { label: "PINN Accuracy", value: "99.2", unit: "%", color: APPLE.dark },
                ].map((metric, i) => (
                  <Card key={i} className="flex flex-col">
                    <p className="text-[13px] font-medium text-[#86868B] mb-2 uppercase tracking-wide">{metric.label}</p>
                    <p className="text-[36px] font-semibold tracking-tight text-[#1D1D1F] leading-none">
                      {metric.value}<span className="text-[18px] text-[#86868B] font-normal ml-1">{metric.unit}</span>
                    </p>
                  </Card>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <Card className="h-full">
                    <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-6">Society Fleet</h3>
                    <div className="space-y-4">
                      {[
                        { name: 'Simplicity Society', location: 'North District', nodes: 4, status: isLeakActive ? 'LEAK' : (valveState === 'CLOSED' ? 'ISOLATED' : 'OPTIMAL'), color: isLeakActive ? APPLE.red : (valveState === 'CLOSED' ? APPLE.orange : APPLE.green) },
                        { name: 'Serenity Towers', location: 'West District', nodes: 12, status: 'OPTIMAL', color: APPLE.green },
                        { name: 'Grand Heights', location: 'Central District', nodes: 8, status: 'OPTIMAL', color: APPLE.green },
                        { name: 'Oasis Complex', location: 'East District', nodes: 6, status: 'MAINTENANCE', color: APPLE.orange },
                      ].map((soc, i) => (
                        <button 
                          key={i} 
                          onClick={() => {
                            GLOBAL_PREVIOUS_ROLE = 'SUPER_ADMIN';
                            login('FACILITY_MANAGER');
                          }}
                          className="w-full flex items-center justify-between p-4 bg-[#F5F5F7] hover:bg-[#E5E5EA] transition-colors rounded-[16px] group cursor-pointer text-left"
                        >
                          <div>
                            <h4 className="text-[17px] font-semibold text-[#1D1D1F] group-hover:text-[#0071E3] transition-colors">{soc.name}</h4>
                            <p className="text-[13px] text-[#86868B]">{soc.location} • {soc.nodes} Active Nodes</p>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-[13px] font-bold tracking-wide" style={{ color: soc.color }}>{soc.status}</span>
                            <ChevronRight className="text-[#D1D5DB] group-hover:text-[#0071E3] group-hover:translate-x-1 transition-all" size={20} />
                          </div>
                        </button>
                      ))}
                    </div>
                  </Card>
                </div>
                
                <div>
                  <Card className="h-full">
                    <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-6">Global Activity Log</h3>
                    <div className="space-y-6">
                      {isLeakActive && (
                        <div className="flex gap-4">
                          <div className="w-2 h-2 mt-2 rounded-full shrink-0 bg-[#FF3B30]"></div>
                          <div>
                            <p className="text-[15px] font-medium text-[#1D1D1F]">Pressure Drop Detected</p>
                            <p className="text-[13px] text-[#86868B]">Simplicity Society • Just now</p>
                          </div>
                        </div>
                      )}
                      {valveState === 'CLOSED' && (
                        <div className="flex gap-4">
                          <div className="w-2 h-2 mt-2 rounded-full shrink-0 bg-[#FF9500]"></div>
                          <div>
                            <p className="text-[15px] font-medium text-[#1D1D1F]">Auto-Isolation Engaged</p>
                            <p className="text-[13px] text-[#86868B]">Simplicity Society • Just now</p>
                          </div>
                        </div>
                      )}
                      <div className="flex gap-4">
                        <div className="w-2 h-2 mt-2 rounded-full shrink-0 bg-[#34C759]"></div>
                        <div>
                          <p className="text-[15px] font-medium text-[#1D1D1F]">Routine Sync Completed</p>
                          <p className="text-[13px] text-[#86868B]">Serenity Towers • 2m ago</p>
                        </div>
                      </div>
                      <div className="flex gap-4">
                        <div className="w-2 h-2 mt-2 rounded-full shrink-0 bg-[#FF9500]"></div>
                        <div>
                          <p className="text-[15px] font-medium text-[#1D1D1F]">Firmware Update</p>
                          <p className="text-[13px] text-[#86868B]">Oasis Complex • 1hr ago</p>
                        </div>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          )}

          {/* TAB: INFRASTRUCTURE */}
          {activeAdminTab === 'INFRASTRUCTURE' && (
             <Card className="animate-in fade-in duration-500">
               <div className="flex justify-between items-center mb-6">
                 <h3 className="text-[18px] font-semibold text-[#1D1D1F]">Infrastructure & Societies</h3>
                 <button onClick={() => setAdminModal({ type: 'TEXT', title: 'Register New Society', placeholder: 'e.g., Prestige Falcon City', step: 'INPUT' })} className="bg-[#0071E3] text-white px-5 py-2.5 rounded-full text-[14px] font-medium hover:bg-[#0077ED]">+ Add Society</button>
               </div>
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                   <thead>
                     <tr className="border-b border-[#E5E5EA] text-[#86868B] text-[13px]">
                       <th className="pb-3 font-medium px-4">Name</th>
                       <th className="pb-3 font-medium px-4">Buildings</th>
                       <th className="pb-3 font-medium px-4">Floors</th>
                       <th className="pb-3 font-medium px-4">Zones</th>
                       <th className="pb-3 font-medium px-4">Actions</th>
                     </tr>
                   </thead>
                   <tbody>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 text-[14px] font-semibold text-[#1D1D1F]">Simplicity Society</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">2 (A, B)</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">12</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">14 Active</td>
                       <td onClick={() => { GLOBAL_PREVIOUS_ROLE = 'SUPER_ADMIN'; login('FACILITY_MANAGER'); }} className="py-4 px-4 text-[#0071E3] text-[13px] font-medium cursor-pointer hover:underline">Manage</td>
                     </tr>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 text-[14px] font-semibold text-[#1D1D1F]">Serenity Towers</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">4 (T1-T4)</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">48</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">32 Active</td>
                       <td onClick={() => { GLOBAL_PREVIOUS_ROLE = 'SUPER_ADMIN'; login('FACILITY_MANAGER'); }} className="py-4 px-4 text-[#0071E3] text-[13px] font-medium cursor-pointer hover:underline">Manage</td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </Card>
          )}

          {/* TAB: DEVICES */}
          {activeAdminTab === 'DEVICES' && (
             <Card className="animate-in fade-in duration-500">
               <div className="flex justify-between items-center mb-6">
                 <h3 className="text-[18px] font-semibold text-[#1D1D1F]">ESP32 Edge Gateways</h3>
                 <button onClick={() => setAdminModal({ type: 'TEXT', title: 'Provision ESP32 Gateway', placeholder: 'Enter MAC Address (e.g., 00:1B:44:11:3A:B7)', step: 'INPUT' })} className="bg-[#0071E3] text-white px-5 py-2.5 rounded-full text-[14px] font-medium hover:bg-[#0077ED]">+ Register Device</button>
               </div>
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                   <thead>
                     <tr className="border-b border-[#E5E5EA] text-[#86868B] text-[13px]">
                       <th className="pb-3 font-medium px-4">Node ID</th>
                       <th className="pb-3 font-medium px-4">Location Assigned</th>
                       <th className="pb-3 font-medium px-4">Firmware</th>
                       <th className="pb-3 font-medium px-4">Last Heartbeat</th>
                       <th className="pb-3 font-medium px-4">Device Health</th>
                     </tr>
                   </thead>
                   <tbody>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 font-mono text-[14px] text-[#1D1D1F]">ESP-A3-04</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">Simplicity • Bldg A • Flr 3</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">v1.2.4</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">2s ago</td>
                       <td className="py-4 px-4"><span className="bg-[#34C759]/10 text-[#34C759] text-[11px] font-bold px-2 py-1 rounded tracking-wide">OPTIMAL</span></td>
                     </tr>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 font-mono text-[14px] text-[#1D1D1F]">ESP-A1-01</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">Simplicity • Bldg A • Flr 1</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">v1.2.4</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">5s ago</td>
                       <td className="py-4 px-4"><span className="bg-[#34C759]/10 text-[#34C759] text-[11px] font-bold px-2 py-1 rounded tracking-wide">OPTIMAL</span></td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </Card>
          )}

          {/* TAB: SENSORS & VALVES */}
          {activeAdminTab === 'SENSORS_&_VALVES' && (
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-500">
               <Card>
                 <h3 className="text-[18px] font-semibold text-[#1D1D1F] mb-6">Sensors Overview</h3>
                 <div className="space-y-4">
                   <div className="flex justify-between items-center p-4 bg-[#F5F5F7] rounded-[16px]">
                     <span className="text-[15px] font-medium text-[#1D1D1F]">Flow Sensors (YF-S201)</span>
                     <span className="text-[13px] text-[#86868B]">44 Active</span>
                   </div>
                   <div className="flex justify-between items-center p-4 bg-[#F5F5F7] rounded-[16px]">
                     <span className="text-[15px] font-medium text-[#1D1D1F]">Pressure (0-1.2MPa)</span>
                     <span className="text-[13px] text-[#86868B]">44 Active</span>
                   </div>
                   <div className="flex justify-between items-center p-4 bg-[#F5F5F7] rounded-[16px]">
                     <span className="text-[15px] font-medium text-[#1D1D1F]">Acoustic/Piezo</span>
                     <span className="text-[13px] text-[#86868B]">28 Active</span>
                   </div>
                   <div className="flex justify-between items-center p-4 bg-[#F5F5F7] rounded-[16px]">
                     <span className="text-[15px] font-medium text-[#1D1D1F]">Pump Motor Current</span>
                     <span className="text-[13px] text-[#86868B]">12 Active</span>
                   </div>
                 </div>
               </Card>
               <Card>
                 <div className="flex justify-between items-center mb-6">
                   <h3 className="text-[18px] font-semibold text-[#1D1D1F]">Valves & Actuators</h3>
                   <button onClick={() => setAdminModal({ type: 'TEXT', title: 'Register Smart Valve', placeholder: 'Enter Actuator ID (e.g., VLV-992)', step: 'INPUT' })} className="text-[#0071E3] text-[14px] font-medium hover:underline">+ Register Valve</button>
                 </div>
                 <div className="space-y-4">
                   <div className="p-4 border border-[#E5E5EA] rounded-[16px]">
                     <div className="flex justify-between items-center mb-4">
                       <span className="font-mono text-[14px] font-semibold text-[#1D1D1F]">VALVE-A3-04</span>
                       <span className={`text-[11px] font-bold px-2 py-1 rounded tracking-wide ${valveState === 'CLOSED' ? 'bg-[#FF9500]/10 text-[#FF9500]' : 'bg-[#34C759]/10 text-[#34C759]'}`}>
                         {valveState === 'CLOSED' ? 'ISOLATED' : 'HEALTHY'}
                       </span>
                     </div>
                     <div className="flex gap-3">
                       <button className="flex-1 bg-[#F5F5F7] hover:bg-[#E5E5EA] py-2.5 rounded-[12px] text-[13px] font-semibold text-[#1D1D1F] transition-colors">Config Zone</button>
                       <button onClick={valveState === 'OPEN' ? triggerValve : repairPipe} className="flex-1 bg-[#F5F5F7] hover:bg-[#E5E5EA] py-2.5 rounded-[12px] text-[13px] font-semibold text-[#1D1D1F] transition-colors">
                         {valveState === 'OPEN' ? 'Test Actuator' : 'Reset Actuator'}
                       </button>
                     </div>
                   </div>
                 </div>
               </Card>
             </div>
          )}

          {/* TAB: AI MODELS */}
          {activeAdminTab === 'AI_MODELS' && (
             <Card className="animate-in fade-in duration-500">
               <div className="flex justify-between items-center mb-6">
                 <h3 className="text-[18px] font-semibold text-[#1D1D1F]">AI Engine Management</h3>
                 <button onClick={() => setAdminModal({ type: 'FILE', title: 'Upload Model Weights', placeholder: 'Select .tflite file', step: 'INPUT' })} className="bg-[#1D1D1F] text-white px-5 py-2.5 rounded-full text-[14px] font-medium hover:bg-[#333333]">Upload Weights (.tflite)</button>
               </div>
               <div className="bg-[#F5F5F7] p-6 rounded-[20px] border border-[#E5E5EA] mb-6">
                 <div className="flex justify-between items-start">
                   <div>
                     <div className="flex items-center gap-3 mb-2">
                       <h4 className="text-[18px] font-semibold text-[#1D1D1F]">PINN-EDGE-V2.4.1</h4>
                       <span className="bg-[#34C759]/10 text-[#34C759] text-[11px] font-bold px-2 py-1 rounded tracking-wide">ACTIVE DEPLOYMENT</span>
                     </div>
                     <p className="text-[14px] text-[#86868B]">Physics-Informed Neural Network • Edge Optimized (8-bit Quantized)</p>
                   </div>
                 </div>
                 <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-6 pt-6 border-t border-[#E5E5EA]">
                   <div>
                     <p className="text-[12px] font-semibold text-[#86868B] uppercase tracking-wide">Calibration Status</p>
                     <p className="text-[16px] font-semibold text-[#1D1D1F] mt-1">Calibrated (99.2% Acc)</p>
                   </div>
                   <div>
                     <p className="text-[12px] font-semibold text-[#86868B] uppercase tracking-wide">Nodes Deployed</p>
                     <p className="text-[16px] font-semibold text-[#1D1D1F] mt-1">14 / 14 Gateways</p>
                   </div>
                   <div>
                     <p className="text-[12px] font-semibold text-[#86868B] uppercase tracking-wide">Last Updated</p>
                     <p className="text-[16px] font-semibold text-[#1D1D1F] mt-1">Aug 14, 2026</p>
                   </div>
                 </div>
                 <div className="flex flex-col sm:flex-row gap-4 mt-8">
                   <button onClick={() => setAdminModal({ type: 'CONFIRM', title: 'Rollback to v2.3.9', placeholder: 'This will temporarily stop AI inference on edge gateways.', step: 'INPUT' })} className="bg-white hover:bg-[#F5F5F7] border border-[#E5E5EA] px-6 py-3 rounded-full text-[14px] font-semibold text-[#FF3B30] transition-colors shadow-sm">Rollback to v2.3.9</button>
                   <button onClick={() => setAdminModal({ type: 'CONFIRM', title: 'Trigger Global Re-calibration', placeholder: 'This will restart edge prediction loops and consume significant bandwidth. Proceed?', step: 'INPUT' })} className="bg-white hover:bg-[#F5F5F7] border border-[#E5E5EA] px-6 py-3 rounded-full text-[14px] font-semibold text-[#1D1D1F] transition-colors shadow-sm">Trigger Global Re-calibration</button>
                 </div>
               </div>
             </Card>
          )}

          {/* TAB: USERS */}
          {activeAdminTab === 'USERS' && (
             <Card className="animate-in fade-in duration-500">
               <div className="flex justify-between items-center mb-6">
                 <h3 className="text-[18px] font-semibold text-[#1D1D1F]">User Access Control</h3>
                 <button onClick={() => setAdminModal({ type: 'TEXT', title: 'Provision New User', placeholder: 'Enter email address', step: 'INPUT' })} className="bg-[#0071E3] text-white px-5 py-2.5 rounded-full text-[14px] font-medium hover:bg-[#0077ED]">+ Create User</button>
               </div>
               <div className="overflow-x-auto">
                 <table className="w-full text-left border-collapse">
                   <thead>
                     <tr className="border-b border-[#E5E5EA] text-[#86868B] text-[13px]">
                       <th className="pb-3 font-medium px-4">Name</th>
                       <th className="pb-3 font-medium px-4">Role</th>
                       <th className="pb-3 font-medium px-4">Society</th>
                       <th className="pb-3 font-medium px-4">Status</th>
                       <th className="pb-3 font-medium px-4 text-right">Actions</th>
                     </tr>
                   </thead>
                   <tbody>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 text-[14px] font-semibold text-[#1D1D1F]">Harsh Shinde</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">Super Admin</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">All Societies</td>
                       <td className="py-4 px-4"><span className="bg-[#34C759]/10 text-[#34C759] text-[11px] font-bold px-2 py-1 rounded tracking-wide">ACTIVE</span></td>
                       <td className="py-4 px-4 text-[13px] font-semibold cursor-pointer text-right space-x-4">
                         <span className="text-[#0071E3] hover:underline">Edit</span>
                         <span className="text-[#FF3B30] hover:underline">Disable</span>
                       </td>
                     </tr>
                     <tr className="border-b border-[#F5F5F7] hover:bg-[#F5F5F7]/50 transition-colors">
                       <td className="py-4 px-4 text-[14px] font-semibold text-[#1D1D1F]">Ramesh Kumar</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">Facility Manager</td>
                       <td className="py-4 px-4 text-[14px] text-[#86868B]">Simplicity Society</td>
                       <td className="py-4 px-4"><span className="bg-[#34C759]/10 text-[#34C759] text-[11px] font-bold px-2 py-1 rounded tracking-wide">ACTIVE</span></td>
                       <td className="py-4 px-4 text-[13px] font-semibold cursor-pointer text-right space-x-4">
                         <span className="text-[#0071E3] hover:underline">Edit</span>
                         <span className="text-[#FF3B30] hover:underline">Disable</span>
                       </td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </Card>
          )}

          {/* TAB: SYSTEM HEALTH */}
          {activeAdminTab === 'SYSTEM_HEALTH' && (
             <Card className="animate-in fade-in duration-500">
               <h3 className="text-[18px] font-semibold text-[#1D1D1F] mb-6">Live Infrastructure Health</h3>
               <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                 {[
                   { name: 'MQTT Broker (Mosquitto)', status: 'ONLINE', color: 'text-[#34C759]', bg: 'bg-[#34C759]/10' },
                   { name: 'Core API (FastAPI)', status: 'ONLINE', color: 'text-[#34C759]', bg: 'bg-[#34C759]/10' },
                   { name: 'Database (PostgreSQL)', status: 'ONLINE', color: 'text-[#34C759]', bg: 'bg-[#34C759]/10' },
                   { name: 'WebSockets Server', status: 'ONLINE', color: 'text-[#34C759]', bg: 'bg-[#34C759]/10' },
                   { name: 'AI Inference Engine', status: 'ONLINE', color: 'text-[#34C759]', bg: 'bg-[#34C759]/10' },
                   { name: 'Edge Gateways', status: 'DEGRADED', color: 'text-[#FF9500]', bg: 'bg-[#FF9500]/10', detail: '2 Nodes Pending Sync' },
                 ].map(sys => (
                   <div key={sys.name} className="p-5 bg-[#F5F5F7] rounded-[20px] border border-[#E5E5EA]">
                     <div className="flex justify-between items-start mb-4">
                       <div className={`w-2.5 h-2.5 rounded-full ${sys.bg.replace('/10', '')} mt-1 animate-pulse`}></div>
                       <span className={`${sys.bg} ${sys.color} text-[11px] font-bold px-2.5 py-1 rounded uppercase tracking-wide`}>{sys.status}</span>
                     </div>
                     <p className="text-[15px] font-semibold text-[#1D1D1F] leading-tight">{sys.name}</p>
                     {sys.detail && <p className="text-[13px] font-medium text-[#FF9500] mt-2">{sys.detail}</p>}
                   </div>
                 ))}
               </div>
             </Card>
          )}

        </div>

        {/* ADMIN MODAL */}
        {adminModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-[24px] shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
               <div className="p-6">
                 {adminModal.step === 'SUCCESS' ? (
                   <div className="text-center py-6">
                     <div className="w-16 h-16 bg-[#34C759]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                       <CheckCircle2 className="text-[#34C759]" size={32} strokeWidth={2.5} />
                     </div>
                     <h3 className="text-[20px] font-semibold text-[#1D1D1F]">Success</h3>
                     <p className="text-[14px] text-[#86868B] mt-2">The operation completed successfully.</p>
                   </div>
                 ) : (
                   <>
                     <h3 className="text-[20px] font-semibold text-[#1D1D1F]">{adminModal.title}</h3>
                     <p className="text-[14px] text-[#86868B] mt-1 mb-6">
                       {adminModal.type === 'CONFIRM' ? adminModal.placeholder : 'Enter the required information below to proceed.'}
                     </p>
                     
                     {adminModal.type === 'TEXT' && (
                       <input 
                         type="text" 
                         placeholder={adminModal.placeholder} 
                         disabled={adminModal.step === 'PROCESSING'}
                         className="w-full bg-[#F5F5F7] border border-[#E5E5EA] rounded-[12px] px-4 py-3 text-[15px] outline-none focus:border-[#0071E3] transition-colors disabled:opacity-50" 
                         autoFocus 
                       />
                     )}
                     {adminModal.type === 'FILE' && (
                       <div className={`border-2 border-dashed border-[#E5E5EA] rounded-[16px] p-8 text-center bg-[#F5F5F7] ${adminModal.step === 'PROCESSING' ? 'opacity-50' : ''}`}>
                         <p className="text-[14px] font-medium text-[#1D1D1F]">Click to browse or drag file here</p>
                         <p className="text-[12px] text-[#86868B] mt-1">Supports .tflite up to 50MB</p>
                       </div>
                     )}
                   </>
                 )}
               </div>

               {adminModal.step !== 'SUCCESS' && (
                 <div className="flex border-t border-[#E5E5EA]">
                   <button 
                     onClick={() => setAdminModal(null)} 
                     disabled={adminModal.step === 'PROCESSING'}
                     className="flex-1 py-4 text-[15px] font-medium text-[#86868B] hover:bg-[#F5F5F7] transition-colors disabled:opacity-50"
                   >
                     Cancel
                   </button>
                   <div className="w-[1px] bg-[#E5E5EA]"></div>
                   <button 
                     disabled={adminModal.step === 'PROCESSING'}
                     onClick={() => {
                       setAdminModal(prev => prev ? { ...prev, step: 'PROCESSING' } : null);
                       setTimeout(() => {
                         setAdminModal(prev => prev ? { ...prev, step: 'SUCCESS' } : null);
                         setTimeout(() => setAdminModal(null), 1500);
                       }, 1200);
                     }} 
                     className="flex-1 py-4 text-[15px] font-semibold text-[#0071E3] hover:bg-[#F5F5F7] transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                   >
                     {adminModal.step === 'PROCESSING' ? (
                       <>
                         <div className="w-4 h-4 border-2 border-[#0071E3]/30 border-t-[#0071E3] rounded-full animate-spin"></div>
                         Processing
                       </>
                     ) : (
                       adminModal.type === 'CONFIRM' ? 'Proceed' : 'Confirm'
                     )}
                   </button>
                 </div>
               )}
            </div>
          </div>
        )}

      </div>
    );
  }

  // ----------------------------------------------------------------------
  // FACILITY MANAGER DASHBOARD
  // ----------------------------------------------------------------------
  
  const historicalData = [
    { day: 'Mon', consumption: 4200, loss: 0 },
    { day: 'Tue', consumption: 4100, loss: 0 },
    { day: 'Wed', consumption: 4350, loss: 0 },
    { day: 'Thu', consumption: 4800, loss: 120 },
    { day: 'Fri', consumption: 4000, loss: 0 },
    { day: 'Sat', consumption: 4500, loss: 0 },
    { day: 'Sun', consumption: 4250, loss: 0 },
  ];

  return (
    <div className="min-h-screen bg-[#F5F5F7] font-sans selection:bg-[#0071E3] selection:text-white pb-12">
      <Header />
      
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* ALERTS SECTION (Apple styled) */}
        {isLeakActive && valveState !== 'CLOSED' && (
          <div className="bg-[#FF3B30] rounded-[24px] p-6 shadow-[0_8px_30px_rgb(255,59,48,0.2)] text-white flex flex-col sm:flex-row items-center justify-between gap-6 transition-all">
            <div className="flex items-center gap-4">
              <AlertCircle size={32} />
              <div>
                <h3 className="text-[20px] font-semibold">Incident Detected: Pipe Rupture</h3>
                <p className="text-white/80 text-[15px] mt-1">NODE-A3-04 • Confidence: 98.4%</p>
              </div>
            </div>
            <button 
              onClick={triggerValve}
              className="px-6 py-3 bg-white text-[#FF3B30] rounded-full font-semibold text-[15px] hover:bg-white/90 transition-colors whitespace-nowrap shadow-sm"
            >
              Force Isolation
            </button>
          </div>
        )}

        {valveState === 'CLOSING' && (
           <div className="bg-[#FF9500] rounded-[24px] p-6 shadow-[0_8px_30px_rgb(255,149,0,0.2)] text-white flex items-center gap-4">
             <div className="animate-spin"><Wrench size={24} /></div>
             <div>
               <h3 className="text-[17px] font-semibold">Actuating Valve...</h3>
               <p className="text-white/80 text-[14px]">Waiting for hardware ACK from ESP32</p>
             </div>
           </div>
        )}

        {valveState === 'CLOSED' && (
          <div className="bg-white border border-[#FF9500]/30 rounded-[24px] p-6 shadow-[0_8px_30px_rgb(255,149,0,0.08)] flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-[#FF9500]/10 rounded-full flex items-center justify-center">
                <CheckCircle2 className="text-[#FF9500]" size={24} />
              </div>
              <div>
                <h3 className="text-[20px] font-semibold text-[#1D1D1F]">Zone Isolated</h3>
                <p className="text-[#86868B] text-[15px] mt-1">Water loss stopped. Pending maintenance repair.</p>
              </div>
            </div>
            <button 
              onClick={repairPipe} 
              className="px-6 py-3 bg-[#F5F5F7] text-[#1D1D1F] hover:bg-[#E5E5EA] rounded-full font-medium text-[15px] transition-colors whitespace-nowrap"
            >
              Resolve & Reset
            </button>
          </div>
        )}

        {/* ROW 1: METRICS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: "Active Nodes", value: "4", unit: "/ 4", color: APPLE.blue },
            { label: "System Pressure", value: valveState === 'CLOSED' ? "2.9" : "2.8", unit: "bar", color: APPLE.dark },
            { label: "Total Flow Rate", value: valveState === 'CLOSED' ? "54" : (isLeakActive ? "77" : "72"), unit: "L/m", color: APPLE.dark },
            { label: "Water Saved (Est)", value: valveState === 'CLOSED' ? "1,240" : "0", unit: "L", color: APPLE.green },
          ].map((metric, i) => (
            <Card key={i} className="flex flex-col">
              <p className="text-[13px] font-medium text-[#86868B] mb-2 uppercase tracking-wide">{metric.label}</p>
              <p className="text-[36px] font-semibold tracking-tight text-[#1D1D1F] leading-none">
                {metric.value}<span className="text-[18px] text-[#86868B] font-normal ml-1">{metric.unit}</span>
              </p>
            </Card>
          ))}
        </div>

        {/* ROW 2: LIVE DATA (8/4 Split) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Main Telemetry & Acoustic (Col 8) */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <Card className="flex-1 min-h-[300px] flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-[17px] font-semibold text-[#1D1D1F]">Live Telemetry</h3>
                  <p className="text-[13px] text-[#86868B] mt-0.5">Flow & Pressure Analytics (NODE-A3-04)</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-[#34C759]/10 rounded-full">
                  <div className="w-2 h-2 rounded-full bg-[#34C759] animate-pulse"></div>
                  <span className="text-[12px] font-semibold text-[#34C759] uppercase tracking-wide">Live Stream</span>
                </div>
              </div>
              <div className="flex-1 w-full h-full min-h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5EA" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 11}} dy={10} />
                    <YAxis yAxisId="left" axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 11}} domain={[0, 30]} />
                    <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 11}} domain={[0, 5]} />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E5E5EA', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', fontWeight: 500 }} />
                    <Line yAxisId="left" type="monotone" dataKey="flow" stroke={APPLE.blue} strokeWidth={3} dot={false} isAnimationActive={false} />
                    <Line yAxisId="right" type="monotone" dataKey="pressure" stroke={APPLE.dark} strokeWidth={3} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="h-[200px] flex flex-col">
              <div className="mb-2">
                <h3 className="text-[17px] font-semibold text-[#1D1D1F]">Acoustic / Vibration Anomalies</h3>
                <p className="text-[13px] text-[#86868B]">PINN Edge Inference Signature</p>
              </div>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5EA" />
                    <XAxis dataKey="time" hide />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 11}} domain={[0, 1.5]} />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #E5E5EA' }} />
                    <Line type="stepAfter" dataKey="acoustic" stroke={APPLE.red} strokeWidth={2.5} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          {/* Network Topology & Status (Col 4) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <Card className="flex flex-col flex-1">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-[17px] font-semibold text-[#1D1D1F]">Network Topology</h3>
                <Map size={18} className="text-[#86868B]" />
              </div>
              
              <div className="w-full h-[180px] bg-[#F5F5F7] rounded-[16px] flex items-center justify-center relative overflow-hidden mb-6">
                <svg width="100%" height="100%" viewBox="0 0 100 100">
                  <line x1="50" y1="15" x2="50" y2="85" stroke="#D1D5DB" strokeWidth="4" strokeLinecap="round" />
                  <circle cx="50" cy="15" r="5" fill="#1D1D1F" />
                  <line x1="50" y1="40" x2="25" y2="40" stroke="#E5E5EA" strokeWidth="3" />
                  <circle cx="25" cy="40" r="4" fill="#34C759" />
                  <line x1="50" y1="60" x2="75" y2="60" stroke="#E5E5EA" strokeWidth="3" />
                  <circle cx="75" cy="60" r="4" fill="#34C759" />
                  <line x1="50" y1="80" x2="25" y2="80" stroke={isLeakActive ? "#FF3B30" : "#E5E5EA"} strokeWidth="3" />
                  <rect x="35" y="77.5" width="4" height="5" rx="1" fill={valveState === 'CLOSED' ? "#FF9500" : "#1D1D1F"} />
                  {isLeakActive && <circle cx="25" cy="80" r="8" fill="#FF3B30" opacity="0.2" className="animate-ping" />}
                  <circle cx="25" cy="80" r="4" fill={isLeakActive ? "#FF3B30" : (valveState === 'CLOSED' ? "#FF9500" : "#34C759")} />
                  
                  <text x="25" y="32" fill="#86868B" fontSize="4.5" textAnchor="middle" fontWeight="500">A1-01</text>
                  <text x="75" y="52" fill="#86868B" fontSize="4.5" textAnchor="middle" fontWeight="500">A2-02</text>
                  <text x="25" y="91" fill={isLeakActive ? "#FF3B30" : "#86868B"} fontSize="5" textAnchor="middle" fontWeight="600">A3-04</text>
                </svg>
              </div>

              <div className="flex-1 space-y-3">
                <h4 className="text-[13px] font-semibold text-[#86868B] uppercase tracking-wide">Live Node Status</h4>
                {['NODE-A1-01', 'NODE-A2-02', 'NODE-A3-04', 'NODE-B1-01'].map((node, i) => {
                  const isTargetNode = node === 'NODE-A3-04';
                  let statusTxt = "OPTIMAL";
                  let color = APPLE.green;
                  
                  if (isTargetNode) {
                    if (isLeakActive) { statusTxt = "LEAK DETECTED"; color = APPLE.red; }
                    else if (valveState === 'CLOSED') { statusTxt = "ISOLATED"; color = APPLE.orange; }
                  }

                  return (
                    <div key={i} className="flex justify-between items-center p-3 bg-[#F5F5F7] rounded-[12px]">
                      <span className="font-mono text-[13px] font-medium text-[#1D1D1F]">{node}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }}></div>
                        <span className="text-[11px] font-bold" style={{ color }}>{statusTxt}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>

        {/* ROW 3: INFRASTRUCTURE (4/4/4 Split) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="flex flex-col h-full">
            <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-4 flex items-center gap-2"><Building size={18} className="text-[#86868B]"/> Hierarchy & Zones</h3>
            <div className="space-y-4 flex-1">
              <div className="pl-2 border-l-2 border-[#E5E5EA]">
                <p className="text-[15px] font-semibold text-[#1D1D1F]">Simplicity Society</p>
                <div className="pl-4 mt-2 space-y-3 border-l-2 border-[#E5E5EA] ml-1">
                  <div>
                    <p className="text-[14px] font-medium text-[#1D1D1F]">Building A</p>
                    <div className="pl-4 mt-1 space-y-1">
                      <p className="text-[13px] text-[#86868B] flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#34C759] rounded-full"></span> Zone 1 (Optimal)</p>
                      <p className="text-[13px] text-[#86868B] flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#34C759] rounded-full"></span> Zone 2 (Optimal)</p>
                      <p className="text-[13px] text-[#86868B] flex items-center gap-2">
                        <span className={`w-1.5 h-1.5 rounded-full ${isLeakActive ? 'bg-[#FF3B30]' : (valveState === 'CLOSED' ? 'bg-[#FF9500]' : 'bg-[#34C759]')}`}></span> 
                        Zone 3 (Basement)
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-[14px] font-medium text-[#1D1D1F]">Building B</p>
                    <p className="pl-4 mt-1 text-[13px] text-[#86868B] flex items-center gap-2"><span className="w-1.5 h-1.5 bg-[#34C759] rounded-full"></span> All Zones (Optimal)</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="flex flex-col h-full">
            <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-4 flex items-center gap-2"><Database size={18} className="text-[#86868B]"/> Pumps & Tanks</h3>
            <div className="space-y-4">
              <div className="p-4 bg-[#F5F5F7] rounded-[16px]">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-[15px] font-medium text-[#1D1D1F]">Main Supply Pump</p>
                  <span className="text-[11px] font-bold text-[#34C759] bg-[#34C759]/10 px-2 py-0.5 rounded">ONLINE</span>
                </div>
                <div className="flex justify-between text-[13px] text-[#86868B]">
                  <span>Power: 4.2 kW</span>
                  <span>Flow: 120 L/m</span>
                </div>
              </div>
              <div className="p-4 bg-[#F5F5F7] rounded-[16px]">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-[15px] font-medium text-[#1D1D1F]">Overhead Tank A</p>
                  <span className="text-[11px] font-bold text-[#0071E3] bg-[#0071E3]/10 px-2 py-0.5 rounded">FILLING</span>
                </div>
                <div className="w-full bg-[#E5E5EA] rounded-full h-1.5 mt-2 mb-1">
                  <div className="bg-[#0071E3] h-1.5 rounded-full" style={{ width: '68%' }}></div>
                </div>
                <div className="flex justify-between text-[13px] text-[#86868B]">
                  <span>Level: 68%</span>
                  <span>Vol: 6,800 L</span>
                </div>
              </div>
            </div>
          </Card>

          <Card className="flex flex-col h-full bg-[#1D1D1F] text-white">
            <h3 className="text-[17px] font-semibold mb-4 flex items-center gap-2"><Layers size={18} className="text-[#86868B]"/> Manual Override</h3>
            <p className="text-[13px] text-[#86868B] mb-6">Use these controls to inject artificial anomalies into the PINN model for demonstration purposes.</p>
            
            <div className="space-y-4 mt-auto">
              <button 
                onClick={triggerRealLeak}
                disabled={isLeakActive || valveState !== 'OPEN'}
                className="w-full py-4 rounded-xl font-medium text-[15px] transition-colors bg-[#FF3B30] hover:bg-[#FF3B30]/90 disabled:opacity-50 disabled:bg-[#333333] disabled:text-[#86868B]"
              >
                Inject Physical Leak
              </button>
              
              <button 
                onClick={valveState === 'OPEN' ? triggerValve : repairPipe}
                className="w-full py-4 rounded-xl font-medium text-[15px] transition-colors border border-white/10 hover:bg-white/10"
              >
                {valveState === 'OPEN' ? 'Force Close Valve' : 'Reset System'}
              </button>
            </div>
          </Card>
        </div>

        {/* ROW 4: ANALYTICS */}
        <Card>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-[17px] font-semibold text-[#1D1D1F] flex items-center gap-2"><BarChart2 size={18} className="text-[#0071E3]"/> Historical Analytics</h3>
              <p className="text-[13px] text-[#86868B] mt-0.5">Water Consumption vs Estimated Loss (Last 7 Days)</p>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={historicalData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5EA" />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 13}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#86868B', fontSize: 13}} dx={-10} />
                <Tooltip 
                  cursor={{fill: '#F5F5F7'}} 
                  contentStyle={{borderRadius: '12px', border: '1px solid #E5E5EA', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', fontWeight: 500 }} 
                />
                <Bar dataKey="consumption" stackId="a" fill="#0071E3" radius={[4, 4, 0, 0]} name="Consumption (L)" isAnimationActive={false} />
                <Bar dataKey="loss" stackId="a" fill="#FF3B30" radius={[4, 4, 0, 0]} name="Loss (L)" isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

      </div>
    </div>
  );
}
